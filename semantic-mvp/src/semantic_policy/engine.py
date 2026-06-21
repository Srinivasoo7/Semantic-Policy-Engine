from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Tuple

from rdflib import Graph, Namespace, RDF, URIRef

try:
    from pyshacl import validate
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "pyshacl is required. Install dependencies with: pip install -r requirements.txt"
    ) from exc


AP = Namespace("http://example.org/agent-policy#")
SH = Namespace("http://www.w3.org/ns/shacl#")


@dataclass
class PolicyResult:
    scenario: str
    conforms: bool
    decision: str
    messages: List[str]
    inferred_types: List[str]
    raw_report: str
    asserted_facts: List[str] = field(default_factory=list)
    violated_policy: str = ""


def load_graph(paths: Iterable[Path]) -> Graph:
    graph = Graph()
    for path in paths:
        graph.parse(str(path), format="turtle")
    return graph


def _collect_messages(results_graph: Graph) -> List[str]:
    messages: List[str] = []
    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        for message in results_graph.objects(result, SH.resultMessage):
            messages.append(str(message))
    return messages


def _collect_asserted_facts(scenario_graph: Graph) -> List[str]:
    """Return human-readable representations of the triples in the scenario graph."""
    facts: List[str] = []
    for s, p, o in scenario_graph:
        s_str = str(s).split("#")[-1]
        p_str = str(p).split("#")[-1]
        o_str = str(o).split("#")[-1]
        facts.append(f"{s_str} {p_str} {o_str}")
    return facts


def _collect_violated_policy(results_graph: Graph) -> str:
    """Return the local name of the first sh:sourceShape found in the results graph."""
    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        for shape in results_graph.objects(result, SH.sourceShape):
            return str(shape).split("#")[-1]
    return ""


def _collect_inferred_types(
    data_graph: Graph, scenario_only_graph: Graph, enterprise_graph: Graph
) -> List[str]:
    """Collect all inferred type assertions that were not in the original graphs."""
    inferred = []
    for s, p, o in data_graph.triples((None, RDF.type, None)):
        if str(o).startswith(str(AP)):
            if (s, RDF.type, o) not in scenario_only_graph and (s, RDF.type, o) not in enterprise_graph:
                s_name = str(s).split("#")[-1]
                o_name = str(o).split("#")[-1]
                inferred.append(f"{s_name} a {o_name}")
    return sorted(list(set(inferred)))


def _collect_violated_shapes(results_graph: Graph) -> List[str]:
    """Return a list of local names of the source shapes that failed validation."""
    shapes: List[str] = []
    for result in results_graph.subjects(RDF.type, SH.ValidationResult):
        for shape in results_graph.objects(result, SH.sourceShape):
            shapes.append(str(shape).split("#")[-1])
    return sorted(list(set(shapes)))


def decision_from_shapes(conforms: bool, violated_shapes: List[str]) -> str:
    if conforms or not violated_shapes:
        return "ALLOW"

    # Priority 1: DENY shapes
    if "LoadedSkillCredentialExfiltrationShape" in violated_shapes:
        return "DENY"

    # Priority 2: REQUIRE_APPROVAL shapes
    approval_shapes = {
        "RestartProductionServerShape",
        "UnverifiedFinanceSkillPreloadShape",
        "DeployProductionServerShape",
    }
    if any(s in approval_shapes for s in violated_shapes):
        return "REQUIRE_APPROVAL"

    # Priority 3: ALLOW_WITH_OBLIGATION shapes
    if "QueryLogsProductionServerShape" in violated_shapes:
        return "ALLOW_WITH_OBLIGATION"

    return "REQUIRE_CLARIFICATION"


def run_policy_check(
    scenario_file: Path,
    root: Path | None = None,
    debug: bool = False,
) -> PolicyResult:
    if root is None:
        root = Path(__file__).resolve().parents[2]

    ontology_path = root / "data" / "ontology.ttl"
    enterprise_path = root / "data" / "enterprise.ttl"
    shapes_path = root / "shapes" / "policy_shapes.ttl"

    # Load graphs separately to distinguish asserted vs inferred facts
    scenario_only_graph = Graph()
    scenario_only_graph.parse(str(scenario_file), format="turtle")

    enterprise_graph = Graph()
    enterprise_graph.parse(str(enterprise_path), format="turtle")

    ontology_graph = Graph()
    ontology_graph.parse(str(ontology_path), format="turtle")

    # Combine into a single graph for validation
    data_graph = Graph()
    data_graph += ontology_graph
    data_graph += enterprise_graph
    data_graph += scenario_only_graph

    shapes_graph = load_graph([shapes_path])

    # Run validation. Set inplace=True to mutate data_graph with OWL RL inferences.
    conforms, results_graph, results_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="owlrl",
        inplace=True,
        debug=debug,
        serialize_report_graph=False,
    )

    messages = _collect_messages(results_graph)
    violated_shapes = _collect_violated_shapes(results_graph)
    decision = decision_from_shapes(conforms, violated_shapes)

    inferred_types = _collect_inferred_types(
        data_graph, scenario_only_graph, enterprise_graph
    )
    asserted_facts = _collect_asserted_facts(scenario_only_graph)
    violated_policy = violated_shapes[0] if violated_shapes else ""

    return PolicyResult(
        scenario=scenario_file.stem,
        conforms=conforms,
        decision=decision,
        messages=messages,
        inferred_types=inferred_types,
        raw_report=results_text,
        asserted_facts=asserted_facts,
        violated_policy=violated_policy,
    )
