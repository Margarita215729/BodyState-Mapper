"""Shared path constants for THSI Static Scientific Evidence Graph scripts."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SOURCES_PDF_DIR = PROJECT_ROOT / "sources_pdf"
DATA_DIR = PROJECT_ROOT / "data"
SCHEMAS_DIR = PROJECT_ROOT / "schemas"
FIGURES_DIR = PROJECT_ROOT / "figures"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

REGISTRY_CSV = DATA_DIR / "evidence_source_registry_v0_1.csv"
REGISTRY_JSON = DATA_DIR / "evidence_source_registry_v0_1.json"
EDGES_CSV = DATA_DIR / "static_scientific_edges_v0_1.csv"
EDGES_JSON = DATA_DIR / "static_scientific_edges_v0_1.json"
NODES_CSV = DATA_DIR / "static_nodes_v0_1.csv"
NODES_JSON = DATA_DIR / "static_nodes_v0_1.json"
GRAPH_JSON = DATA_DIR / "static_scientific_evidence_graph_v0_1.json"

EVIDENCE_SOURCE_SCHEMA = SCHEMAS_DIR / "evidence_source.schema.json"
STATIC_EDGE_SCHEMA = SCHEMAS_DIR / "static_edge.schema.json"
STATIC_NODE_SCHEMA = SCHEMAS_DIR / "static_node.schema.json"
STATIC_GRAPH_SCHEMA = SCHEMAS_DIR / "static_graph.schema.json"

GRAPH_ID = "thsi_static_scientific_evidence_graph_v0_1"
GRAPH_VERSION = "0.1"

NODES_MD = DATA_DIR / "static_nodes_v0_1.md"
EXAMPLE_QUERY_JSON = OUTPUTS_DIR / "example_static_graph_query_v0_1.json"
EXAMPLE_QUERY_MD = OUTPUTS_DIR / "example_static_graph_query_v0_1.md"

PERSONAL_OBSERVATION_SCHEMA = SCHEMAS_DIR / "personal_observation.schema.json"
RAW_OBSERVATION_SCHEMA = SCHEMAS_DIR / "raw_observation.schema.json"
PERSONAL_BASELINE_SCHEMA = SCHEMAS_DIR / "personal_baseline.schema.json"
DERIVED_MARKER_SCHEMA = SCHEMAS_DIR / "derived_marker.schema.json"
PERSONAL_EVIDENCE_GRAPH_SCHEMA = SCHEMAS_DIR / "personal_evidence_graph.schema.json"

DEMO_OBSERVATIONS = DATA_DIR / "demo_observations_v0_1.json"
DEMO_RAW_OBSERVATIONS = DATA_DIR / "demo_raw_observations_v0_1.json"
DEMO_PERSONAL_BASELINE = DATA_DIR / "demo_personal_baseline_v0_1.json"

DEMO_INFERENCE_JSON = OUTPUTS_DIR / "demo_inference_result_v0_1.json"
DEMO_INFERENCE_MD = OUTPUTS_DIR / "demo_inference_report_v0_1.md"
DEMO_PERSONAL_EVIDENCE_GRAPH = OUTPUTS_DIR / "demo_personal_evidence_graph_v0_1.json"
DEMO_PERSONAL_EVIDENCE_GRAPH_REPORT = (
    OUTPUTS_DIR / "demo_personal_evidence_graph_report_v0_1.md"
)
DEMO_INFERENCE_INPUT_FROM_PERSONAL_GRAPH = (
    OUTPUTS_DIR / "demo_inference_input_from_personal_graph_v0_1.json"
)
DEMO_PERSONAL_INFERENCE_JSON = OUTPUTS_DIR / "demo_personal_inference_result_v0_1.json"
DEMO_PERSONAL_INFERENCE_MD = OUTPUTS_DIR / "demo_personal_inference_report_v0_1.md"

INFERENCE_ID = "demo_inference_v0_1"
PERSONAL_GRAPH_ID = "demo_personal_evidence_graph_v0_1"
PERSONAL_INFERENCE_ID = "demo_personal_inference_v0_1"

REGISTRY_FIELDS = [
    "source_id",
    "title",
    "authors",
    "year",
    "journal_or_source",
    "doi",
    "url",
    "pdf_filename",
    "source_type",
    "domain",
    "access_status",
    "population",
    "sample_size",
    "methodology_short",
    "main_findings_short",
    "supported_nodes",
    "supported_edges",
    "limitations",
    "risk_of_overinterpretation",
    "evidence_strength_score",
    "use_in_thsi",
    "notes_for_thsi",
]

EDGE_FIELDS = [
    "edge_id",
    "source_node",
    "target_node",
    "relationship_type",
    "evidence_strength_score",
    "confidence_prior",
    "source_ids",
    "domain",
    "methodology_basis",
    "main_finding_summary",
    "limitations",
    "context_requirements",
    "forbidden_direct_inference",
    "risk_of_overinterpretation",
]

NODE_FIELDS = [
    "node_id",
    "node_type",
    "label",
    "domain",
    "description",
    "allowed_as_input",
    "allowed_as_output",
    "clinical_diagnosis",
    "created_from_edges",
]

NODE_TYPES = (
    "observable_marker",
    "physiological_mechanism",
    "biochemical_marker",
    "neurobiological_affective_bridge",
    "psychological_state_hypothesis",
    "risk_state",
    "context_node",
    "model_feature_node",
    "methodological_node",
)

REGISTRY_REQUIRED_FIELDS = (
    "source_id",
    "title",
    "pdf_filename",
    "source_type",
    "domain",
    "evidence_strength_score",
)

EDGE_REQUIRED_FIELDS = (
    "edge_id",
    "source_node",
    "target_node",
    "relationship_type",
    "evidence_strength_score",
    "confidence_prior",
    "source_ids",
    "limitations",
    "risk_of_overinterpretation",
)

SOURCE_TYPE_STRENGTH = {
    "meta_analysis": 5,
    "umbrella_review": 5,
    "systematic_review_of_reviews": 5,
    "systematic_review": 4,
    "methodological_review": 4,
    "machine_learning_systematic_review": 4,
    "narrative_review": 3,
    "theoretical_review": 3,
    "experimental_study": 2,
}
