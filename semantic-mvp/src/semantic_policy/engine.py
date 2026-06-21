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


def _collect_inferred_types(graph: Graph) -> List[str]:
    checks: List[Tuple[URIRef, URIRef]] = [
        (AP.srv_123, AP.ProductionServer),
        (AP.srv_123, AP.CriticalInfrastructureAsset),
        (AP.srv_456, AP.StagingServer),
        (AP.expense_reconciler, AP.UnverifiedSkill),
    ]

    inferred = []
    for subject, klass in checks:
        if (subject, RDF.type, klass) in graph:
            inferred.append(f"{subject.split('#')[-1]} a {klass.split('#')[-1]}")
    return inferred


def decision_from_messages(conforms: bool, messages: List[str]) -> str:
    if conforms:
        return "ALLOW"

    joined = " ".join(messages).lower()

    if "must be denied" in joined or "credential exfiltration" in joined:
        return "DENY"

    if (
        "requires approval" in joined
        or "requires approval or clarification" in joined
        or "requires an approved" in joined
    ):
        return "REQUIRE_APPROVAL"

    if "audit obligation" in joined:
        return "ALLOW_WITH_OBLIGATION"

    return "REQUIRE_CLARIFICATION"


def run_policy_check(
    scenario_file: Path,
    root: Path | None = None,
    debug: bool = False,
) -> PolicyResult:
    if root is None:
        root = Path(__file__).resolve().parents[2]

    data_graph = load_graph(
        [
            root / "data" / "ontology.ttl",
            root / "data" / "enterprise.ttl",
            scenario_file,
        ]
    )
    shapes_graph = load_graph([root / "shapes" / "policy_shapes.ttl"])

    # IMPORTANT:
    # pySHACL uses inference="owlrl" to materialize OWL/RDFS entailments
    # before SHACL validation. This lets SHACL see inferred facts such as:
    # srv_123 a ProductionServer.
    conforms, results_graph, results_text = validate(
        data_graph=data_graph,
        shacl_graph=shapes_graph,
        inference="owlrl",
        debug=debug,
        serialize_report_graph=False,
    )

    messages = _collect_messages(results_graph)

    # Some pySHACL versions do not mutate the input graph unless inplace=True.
    # This second pass is only for deterministic display of inferred types.
    try:
        validate(
            data_graph=data_graph,
            shacl_graph=shapes_graph,
            inference="owlrl",
            inplace=True,
            debug=False,
            serialize_report_graph=False,
        )
    except TypeError:
        pass

    inferred_types = _collect_inferred_types(data_graph)
    decision = decision_from_messages(conforms, messages)

    # Load the scenario file alone to extract asserted (input) facts
    scenario_only_graph = Graph()
    scenario_only_graph.parse(str(scenario_file), format="turtle")
    asserted_facts = _collect_asserted_facts(scenario_only_graph)

    violated_policy = _collect_violated_policy(results_graph)

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
