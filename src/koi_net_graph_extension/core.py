from rdflib import Dataset

from .components.graph_mirror import GraphMirror
from .components.graph_parser import GraphParser
from .components.graph_vocab_deref_handler import GraphVocabDerefHandler


class GraphMixin:
    rdf_dataset: Dataset = lambda: Dataset()
    graph_vocab_deref_handler: GraphVocabDerefHandler = GraphVocabDerefHandler
    graph_parser: GraphParser = GraphParser
    graph_mirror: GraphMirror = GraphMirror