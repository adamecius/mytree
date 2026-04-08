from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Dict, Optional

import networkx as nx


class Layer(str, Enum):
    PHYSICS = "physics"
    MATH = "math"
    NUMERICS = "numerics"


class NodeKind(str, Enum):
    THEORY = "theory"
    REPRESENTATION = "representation"
    SOLVER = "solver"


class RelationKind(str, Enum):
    APPROXIMATION_OF = "approximation_of"
    REPRESENTED_BY = "represented_by"
    SOLVED_BY = "solved_by"


class ApproximationFamily(str, Enum):
    PHYSICS_REDUCTION = "physics_reduction"
    REPRESENTATION_TRUNCATION = "representation_truncation"
    ANSATZ_RESTRICTION = "ansatz_restriction"
    EFFECTIVE_PROJECTION = "effective_projection"
    FUNCTIONAL_REFORMULATION = "functional_reformulation"
    SOLVER_CONSTRAINT = "solver_constraint"


@dataclass
class NodeData:
    node_id: str
    label: str
    layer: Layer
    kind: NodeKind
    subtype: str
    description: str = ""
    methods: list[str] = field(default_factory=list)
    mathematical_representation: Optional[str] = None
    numerical_platforms: list[str] = field(default_factory=list)
    computational_scaling: Optional[str] = None
    problem_domains: list[str] = field(default_factory=list)
    key_references: list[str] = field(default_factory=list)
    exactness_class: Optional[str] = None
    systematically_improvable: Optional[bool] = None
    controlled: Optional[bool] = None
    approximation_rank: Optional[int] = None
    notes: str = ""

    def to_nx_attrs(self) -> Dict[str, Any]:
        data = asdict(self)
        data["layer"] = self.layer.value
        data["kind"] = self.kind.value
        return data


@dataclass
class EdgeData:
    relation: RelationKind
    label: str
    approximation_type: Optional[str] = None
    approximation_family: Optional[ApproximationFamily] = None
    information_loss: Optional[str] = None
    systematically_improvable: Optional[bool] = None
    controlled: Optional[bool] = None
    notes: str = ""

    def to_nx_attrs(self) -> Dict[str, Any]:
        data = asdict(self)
        data["relation"] = self.relation.value
        if self.approximation_family is not None:
            data["approximation_family"] = self.approximation_family.value
        return data


def add_typed_node(graph: nx.MultiDiGraph, node: NodeData) -> None:
    graph.add_node(node.node_id, **node.to_nx_attrs())


def add_typed_edge(graph: nx.MultiDiGraph, source: str, target: str, edge: EdgeData) -> None:
    graph.add_edge(source, target, key=f"{edge.relation.value}:{edge.label}", **edge.to_nx_attrs())


def nodes_by_layer(graph: nx.MultiDiGraph, layer: Layer) -> list[str]:
    return [n for n, d in graph.nodes(data=True) if d.get("layer") == layer.value]


def edges_by_relation(graph: nx.MultiDiGraph, relation: RelationKind) -> list[tuple[str, str, str, dict[str, Any]]]:
    return [
        (u, v, k, d)
        for u, v, k, d in graph.edges(keys=True, data=True)
        if d.get("relation") == relation.value
    ]


def layered_positions(graph: nx.MultiDiGraph) -> dict[str, tuple[float, float]]:
    layer_y = {"physics": 2.0, "math": 1.0, "numerics": 0.0}
    positions: dict[str, tuple[float, float]] = {}

    for layer_name in [Layer.PHYSICS.value, Layer.MATH.value, Layer.NUMERICS.value]:
        layer_nodes = [(n, d) for n, d in graph.nodes(data=True) if d.get("layer") == layer_name]
        layer_nodes.sort(key=lambda item: (item[1].get("approximation_rank", 999), item[1].get("label", "")))
        for i, (node_id, _) in enumerate(layer_nodes):
            positions[node_id] = (float(i), layer_y[layer_name])
    return positions


def node_neighborhood_subgraph(graph: nx.MultiDiGraph, node_id: str, include_reverse: bool = True) -> nx.MultiDiGraph:
    if node_id not in graph:
        raise KeyError(f"Node not found: {node_id}")

    neighbors = {node_id}
    neighbors.update(graph.successors(node_id))
    if include_reverse:
        neighbors.update(graph.predecessors(node_id))
    return graph.subgraph(neighbors).copy()


def validate_graph_structure(graph: nx.MultiDiGraph) -> list[str]:
    errors: list[str] = []
    for node_id, data in graph.nodes(data=True):
        layer = data.get("layer")
        kind = data.get("kind")
        if layer not in {layer.value for layer in Layer}:
            errors.append(f"Invalid layer for node {node_id}: {layer}")
        if kind not in {kind.value for kind in NodeKind}:
            errors.append(f"Invalid kind for node {node_id}: {kind}")

    valid_pairs = {
        RelationKind.APPROXIMATION_OF.value: {(l.value, l.value) for l in Layer},
        RelationKind.REPRESENTED_BY.value: {(Layer.PHYSICS.value, Layer.MATH.value)},
        RelationKind.SOLVED_BY.value: {(Layer.MATH.value, Layer.NUMERICS.value)},
    }

    for source, target, _, data in graph.edges(keys=True, data=True):
        relation = data.get("relation")
        source_layer = graph.nodes[source].get("layer")
        target_layer = graph.nodes[target].get("layer")
        if relation not in valid_pairs:
            errors.append(f"Invalid relation kind for edge {source}->{target}: {relation}")
            continue
        if (source_layer, target_layer) not in valid_pairs[relation]:
            errors.append(
                f"Invalid layer pair for relation {relation}: {source}({source_layer}) -> {target}({target_layer})"
            )
    return errors


def build_materials_ontology_graph() -> nx.MultiDiGraph:
    graph = nx.MultiDiGraph(name="materials_layered_ontology")

    physics_nodes = [
        NodeData(
            node_id="phys:ground_truth",
            label="Ground-truth",
            layer=Layer.PHYSICS,
            kind=NodeKind.THEORY,
            subtype="fundamental_theory",
            description="Most complete microscopic description in scope.",
            key_references=["Feynman 1982", "Lloyd 1996"],
            exactness_class="exact in principle",
            systematically_improvable=True,
            controlled=True,
            approximation_rank=0,
        ),
        NodeData(
            node_id="phys:relativistic_many_body",
            label="Relativistic many-body Hamiltonian",
            layer=Layer.PHYSICS,
            kind=NodeKind.THEORY,
            subtype="fundamental_theory",
            key_references=["Dirac, 1928, Proc. Roy. Soc. A"],
            approximation_rank=1,
        ),
        NodeData(
            node_id="phys:nonrel_coulomb",
            label="Non-relativistic electron-nuclear Coulomb Hamiltonian",
            layer=Layer.PHYSICS,
            kind=NodeKind.THEORY,
            subtype="fundamental_theory",
            key_references=["Martin, 2004, Electronic Structure"],
            approximation_rank=2,
        ),
        NodeData(
            node_id="phys:born_oppenheimer",
            label="Born-Oppenheimer electronic Hamiltonian",
            layer=Layer.PHYSICS,
            kind=NodeKind.THEORY,
            subtype="electronic_structure_theory",
            key_references=["Born & Oppenheimer, 1927, Annalen der Physik"],
            approximation_rank=3,
        ),
        NodeData(
            node_id="phys:finite_basis_electronic",
            label="Finite-basis electronic Hamiltonian",
            layer=Layer.PHYSICS,
            kind=NodeKind.THEORY,
            subtype="electronic_structure_theory",
            key_references=["Helgaker et al., 2000, Molecular Electronic-Structure Theory"],
            approximation_rank=4,
        ),
        NodeData(
            node_id="phys:effective_hamiltonian",
            label="Effective reduced Hamiltonian",
            layer=Layer.PHYSICS,
            kind=NodeKind.THEORY,
            subtype="reduced_hamiltonian",
            key_references=["Malrieu et al., 2014, Rev. Mod. Phys."],
            approximation_rank=5,
        ),
        NodeData(
            node_id="phys:low_energy_model",
            label="Low-energy lattice model",
            layer=Layer.PHYSICS,
            kind=NodeKind.THEORY,
            subtype="low_energy_model",
            key_references=[
                "Ashcroft & Mermin, 1976, Solid State Physics",
                "Arovas et al., 2022, Annu. Rev. CMP",
            ],
            approximation_rank=6,
        ),
    ]

    math_nodes = [
        NodeData(
            node_id="math:qft",
            label="Quantum field theory",
            layer=Layer.MATH,
            kind=NodeKind.REPRESENTATION,
            subtype="field_formalism",
            approximation_rank=0,
        ),
        NodeData(
            node_id="math:continuous_hilbert",
            label="Continuous Hilbert space",
            layer=Layer.MATH,
            kind=NodeKind.REPRESENTATION,
            subtype="hilbert_space_formalism",
            approximation_rank=1,
        ),
        NodeData(
            node_id="math:first_quantisation",
            label="First quantisation",
            layer=Layer.MATH,
            kind=NodeKind.REPRESENTATION,
            subtype="hilbert_space_formalism",
            approximation_rank=2,
        ),
        NodeData(
            node_id="math:second_quantisation",
            label="Second quantisation",
            layer=Layer.MATH,
            kind=NodeKind.REPRESENTATION,
            subtype="operator_representation",
            key_references=["Fetter & Walecka, 2003, Quantum Theory of Many-Particle Systems"],
            approximation_rank=2,
        ),
        NodeData(
            node_id="math:fock_space",
            label="Finite Fock space",
            layer=Layer.MATH,
            kind=NodeKind.REPRESENTATION,
            subtype="discretised_representation",
            key_references=["Fetter & Walecka, 2003"],
            approximation_rank=3,
        ),
        NodeData(
            node_id="math:path_integral",
            label="Path integral",
            layer=Layer.MATH,
            kind=NodeKind.REPRESENTATION,
            subtype="field_formalism",
            key_references=["Feynman, 1948, Rev. Mod. Phys."],
            approximation_rank=2,
        ),
        NodeData(
            node_id="math:finite_basis",
            label="Finite basis representation",
            layer=Layer.MATH,
            kind=NodeKind.REPRESENTATION,
            subtype="discretised_representation",
            key_references=["Helgaker et al., 2000"],
            approximation_rank=3,
        ),
        NodeData(
            node_id="math:density_functional",
            label="Density-functional reformulation",
            layer=Layer.MATH,
            kind=NodeKind.REPRESENTATION,
            subtype="functional_reformulation",
            key_references=[
                "Hohenberg & Kohn, 1964, Phys. Rev.",
                "Mardirossian & Head-Gordon, 2017, Mol. Phys.",
            ],
            approximation_rank=4,
        ),
        NodeData(
            node_id="math:tensor_network",
            label="Tensor-network ansatz",
            layer=Layer.MATH,
            kind=NodeKind.REPRESENTATION,
            subtype="compressed_ansatz",
            key_references=["Orús, 2014, Annals of Physics"],
            approximation_rank=4,
        ),
        NodeData(
            node_id="math:lattice_hamiltonian",
            label="Lattice Hamiltonian representation",
            layer=Layer.MATH,
            kind=NodeKind.REPRESENTATION,
            subtype="discretised_representation",
            approximation_rank=4,
        ),
    ]

    numerics_nodes = [
        NodeData(
            node_id="num:exact_diagonalisation",
            label="Exact diagonalisation",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="exact_solver",
            approximation_rank=0,
        ),
        NodeData(
            node_id="num:full_ci",
            label="Full CI",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="exact_solver",
            key_references=["Szabo & Ostlund, 1996, Modern Quantum Chemistry"],
            approximation_rank=0,
        ),
        NodeData(
            node_id="num:selected_ci",
            label="Selected CI",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="exact_solver",
            approximation_rank=1,
        ),
        NodeData(
            node_id="num:hartree_fock_scf",
            label="Hartree-Fock SCF",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="mean_field_solver",
            key_references=["Jensen, 2017, Introduction to Computational Chemistry"],
            approximation_rank=3,
        ),
        NodeData(
            node_id="num:coupled_cluster",
            label="Coupled cluster",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="post_hf_solver",
            key_references=["Bartlett & Musiał, 2007, Rev. Mod. Phys."],
            approximation_rank=2,
        ),
        NodeData(
            node_id="num:dmrg",
            label="DMRG",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="tensor_network_solver",
            key_references=["White, 1992, Phys. Rev. Lett."],
            approximation_rank=1,
        ),
        NodeData(
            node_id="num:afqmc",
            label="AFQMC",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="stochastic_solver",
            approximation_rank=1,
        ),
        NodeData(
            node_id="num:phaseless_afqmc",
            label="Phaseless AFQMC",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="stochastic_solver",
            approximation_rank=2,
        ),
        NodeData(
            node_id="num:dmc",
            label="Diffusion Monte Carlo",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="stochastic_solver",
            approximation_rank=1,
        ),
        NodeData(
            node_id="num:kohn_sham_scf",
            label="Kohn-Sham SCF",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="density_solver",
            key_references=["Kohn & Sham, 1965, Phys. Rev."],
            approximation_rank=3,
        ),
        NodeData(
            node_id="num:qpe",
            label="Quantum phase estimation",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="quantum_algorithm",
            key_references=["McArdle et al., 2020, Rev. Mod. Phys."],
            approximation_rank=0,
        ),
        NodeData(
            node_id="num:qubitisation",
            label="Qubitisation",
            layer=Layer.NUMERICS,
            kind=NodeKind.SOLVER,
            subtype="quantum_algorithm",
            approximation_rank=0,
        ),
    ]

    for collection in (physics_nodes, math_nodes, numerics_nodes):
        for node in collection:
            add_typed_node(graph, node)

    for source, target, edge in [
        (
            "phys:ground_truth",
            "phys:relativistic_many_body",
            EdgeData(RelationKind.APPROXIMATION_OF, "effective relativistic many-body reduction", approximation_family=ApproximationFamily.PHYSICS_REDUCTION),
        ),
        (
            "phys:relativistic_many_body",
            "phys:nonrel_coulomb",
            EdgeData(RelationKind.APPROXIMATION_OF, "non-relativistic limit", approximation_family=ApproximationFamily.PHYSICS_REDUCTION),
        ),
        (
            "phys:nonrel_coulomb",
            "phys:born_oppenheimer",
            EdgeData(RelationKind.APPROXIMATION_OF, "born-oppenheimer separation", approximation_family=ApproximationFamily.PHYSICS_REDUCTION),
        ),
        (
            "phys:born_oppenheimer",
            "phys:finite_basis_electronic",
            EdgeData(RelationKind.APPROXIMATION_OF, "basis truncation", approximation_family=ApproximationFamily.REPRESENTATION_TRUNCATION),
        ),
        (
            "phys:finite_basis_electronic",
            "phys:effective_hamiltonian",
            EdgeData(RelationKind.APPROXIMATION_OF, "effective reduction", approximation_family=ApproximationFamily.EFFECTIVE_PROJECTION),
        ),
        (
            "phys:effective_hamiltonian",
            "phys:low_energy_model",
            EdgeData(RelationKind.APPROXIMATION_OF, "downfolding", approximation_family=ApproximationFamily.EFFECTIVE_PROJECTION),
        ),
        (
            "math:continuous_hilbert",
            "math:finite_basis",
            EdgeData(RelationKind.APPROXIMATION_OF, "finite discretisation", approximation_family=ApproximationFamily.REPRESENTATION_TRUNCATION),
        ),
        (
            "math:second_quantisation",
            "math:fock_space",
            EdgeData(RelationKind.APPROXIMATION_OF, "finite fock truncation", approximation_family=ApproximationFamily.REPRESENTATION_TRUNCATION),
        ),
        (
            "math:fock_space",
            "math:tensor_network",
            EdgeData(RelationKind.APPROXIMATION_OF, "tensor compression", approximation_family=ApproximationFamily.ANSATZ_RESTRICTION),
        ),
        (
            "math:fock_space",
            "math:density_functional",
            EdgeData(RelationKind.APPROXIMATION_OF, "density reformulation", approximation_family=ApproximationFamily.FUNCTIONAL_REFORMULATION),
        ),
        (
            "math:finite_basis",
            "math:lattice_hamiltonian",
            EdgeData(RelationKind.APPROXIMATION_OF, "lattice projection", approximation_family=ApproximationFamily.EFFECTIVE_PROJECTION),
        ),
        (
            "num:full_ci",
            "num:selected_ci",
            EdgeData(RelationKind.APPROXIMATION_OF, "determinant selection", approximation_family=ApproximationFamily.SOLVER_CONSTRAINT),
        ),
        (
            "num:afqmc",
            "num:phaseless_afqmc",
            EdgeData(RelationKind.APPROXIMATION_OF, "phaseless constraint", approximation_family=ApproximationFamily.SOLVER_CONSTRAINT),
        ),
    ]:
        add_typed_edge(graph, source, target, edge)

    for source, target, label in [
        ("phys:ground_truth", "math:qft", "represented in microscopic field form"),
        ("phys:nonrel_coulomb", "math:continuous_hilbert", "represented by continuous wavefunction"),
        ("phys:nonrel_coulomb", "math:first_quantisation", "represented in first quantisation"),
        ("phys:nonrel_coulomb", "math:path_integral", "represented by path integral"),
        ("phys:born_oppenheimer", "math:second_quantisation", "represented in second quantisation"),
        ("phys:finite_basis_electronic", "math:finite_basis", "represented by finite basis"),
        ("phys:effective_hamiltonian", "math:fock_space", "represented in reduced fock space"),
        ("phys:low_energy_model", "math:lattice_hamiltonian", "represented as lattice Hamiltonian"),
        ("phys:born_oppenheimer", "math:density_functional", "reformulated as density functional"),
    ]:
        add_typed_edge(graph, source, target, EdgeData(RelationKind.REPRESENTED_BY, label))

    for source, target, label in [
        ("math:fock_space", "num:exact_diagonalisation", "solved by"),
        ("math:fock_space", "num:full_ci", "solved by"),
        ("math:fock_space", "num:selected_ci", "approximately solved by"),
        ("math:tensor_network", "num:dmrg", "optimised by"),
        ("math:path_integral", "num:dmc", "sampled by"),
        ("math:density_functional", "num:kohn_sham_scf", "solved by"),
        ("math:second_quantisation", "num:coupled_cluster", "solved by"),
        ("math:finite_basis", "num:hartree_fock_scf", "optimised by"),
        ("math:first_quantisation", "num:qpe", "solved on FTQC by"),
        ("math:second_quantisation", "num:qubitisation", "hamiltonian simulated by"),
        ("math:fock_space", "num:afqmc", "sampled by"),
    ]:
        add_typed_edge(graph, source, target, EdgeData(RelationKind.SOLVED_BY, label))

    return graph
