from pathlib import Path

import pyshacl
from rdflib import Graph

from test_node import TestNode

node = TestNode(root_dir=Path("test_node"))


def main():
    shacl_graph = Graph()
    shacl_graph.parse("edge_constraint.ttl")
    
    conform, results_graph, results_text = pyshacl.validate(
        data_graph=node.rdf_dataset,
        shacl_graph=shacl_graph
    )
    print(results_text)
    
    node.rdf_dataset.serialize("test.ttl")



def query(q):
    for r in node.rdf_dataset.query(q):
        print(", ".join(r))


if __name__ == "__main__":
    node.start()
    try:
        main()

    finally:
        node.stop()