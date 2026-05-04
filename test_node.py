import pyshacl
from rdflib import Dataset, Graph
from koi_net.config import FullNodeConfig, FullNodeProfile, KoiNetConfig, NodeProvides
from koi_net.core import FullNode
from rid_lib import RID, RIDType
from koi_net_graph_extension.graph_mirror import GraphMirror
from koi_net_graph_extension.graph_parser import GraphParser
from koi_net_graph_extension.graph_vocab_deref_handler import GraphVocabDerefHandler
from koi_net_graph_extension.shacl_edge_negotiator import ShaclEdgeNegotiationHandler
from koi_net_graph_extension.update_diff_monitor import UpdateDiffMonitor


class MyPartialNodeConfig(FullNodeConfig):
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="test_node",
        node_profile=FullNodeProfile(
            provides=NodeProvides(
                event=[RIDType.from_string("orn:example.type")]
            )
        )
    )

class TestNode(FullNode):
    config_schema = MyPartialNodeConfig
    graph_vocab_deref_handler = GraphVocabDerefHandler
    graph_parser = GraphParser
    graph_mirror = GraphMirror
    rdf_dataset = lambda: Dataset()
    edge_negotiation_handler = ShaclEdgeNegotiationHandler
    update_diff_monitor = UpdateDiffMonitor




def val():
    shacl_graph = Graph()
    shacl_graph.parse("edge_constraint.json", format="json-ld")
    
    conform, results_graph, results_text = pyshacl.validate(
        data_graph=node.rdf_dataset,
        shacl_graph=shacl_graph
    )
    print(results_text)
    


if __name__ == "__main__":
    node = TestNode()
    node.run()
    
    # node.start()
    
    # ds: Dataset = node.rdf_dataset
    
    # ds.serialize()
    
    # for ng in ds.contexts():
    #     print(f"Graph <{ng.identifier}>")
    #     for s, p, o in ng:
    #         print(f"\t<{s}> <{p}> <{o}>")