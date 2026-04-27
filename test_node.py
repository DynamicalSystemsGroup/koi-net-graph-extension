import pyshacl
from rdflib import Graph
from koi_net.config import PartialNodeConfig, KoiNetConfig, PartialNodeProfile
from koi_net.core import PartialNode
from koi_net_graph_extension.context_coercer import ContextCoercer
from koi_net_graph_extension.contexts import GraphVocabLoader
from koi_net_graph_extension.graph_parser import GraphParser


class MyPartialNodeConfig(PartialNodeConfig):
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="partial",
        node_profile=PartialNodeProfile()
    )

class MyPartialNode(PartialNode):
    config_schema = MyPartialNodeConfig
    graph_vocab_loader = GraphVocabLoader
    context_coerver = ContextCoercer
    graph_parser = GraphParser


q = """
SELECT ?source ?ridType ?target
WHERE {
    GRAPH ?g {
        ?edge koi:edgeSource ?source .
        ?edge koi:edgeTarget ?target .
        ?edge koi:ridType ?ridType .
    }
}
"""

q2 = """
PREFIX koi: <orn:koi-net.vocab:>

SELECT ?source ?edge ?ridType
WHERE {
    GRAPH ?g {
        ?edge koi:ridType ?ridType .
        ?edge koi:edgeSource ?source .
    }
    FILTER (
        ?ridType != "orn:koi-net.node" &&
        ?ridType != "orn:koi-net.edge" &&
        NOT EXISTS {
            GRAPH ?nodeGraph {
                ?source koi:nodeProvides/koi:eventType ?ridType .
            }
        }
    )
}
"""

q3 = """
PREFIX koi: <orn:koi-net.vocab:>

SELECT ?node ?provides ?eventType ?stateType
WHERE {
    GRAPH ?g {
        ?node koi:nodeProvides ?provides .
        ?provides koi:eventType ?eventType .
        ?provides koi:stateType ?stateType .
    }
}
"""

q4 = """
PREFIX koi: <orn:koi-net.vocab:>
SELECT ?node ?type ?value
WHERE {
    GRAPH ?g {
        ?node a <orn:koi-net.node> .
        ?node koi:nodeProvides ?provides .
        {
            ?provides koi:eventType ?value .
            BIND("eventType" AS ?type)
        } UNION {
            ?provides koi:stateType ?value .
            BIND("stateType" AS ?type)
        }
    }
}
ORDER BY ?node ?type
"""


node = MyPartialNode()

def val():
    shacl_graph = Graph()
    shacl_graph.parse("edge_constraint.json", format="json-ld")
    
    conform, results_graph, results_text = pyshacl.validate(
        data_graph=node.graph_parser.dataset,
        shacl_graph=shacl_graph
    )
    print(results_text)
    
def query(q):
    for r in node.graph_parser.dataset.query(q):
        print(", ".join(r))
    

if __name__ == "__main__":
    node.graph_parser.start()
    
    # for (s, p, o, g) in node.graph_parser.dataset:
    #     print(s, p, o)
        
    query(q2)
        
    node.graph_parser.dataset.serialize("output.ttl")
    