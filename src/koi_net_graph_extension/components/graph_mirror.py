from dataclasses import dataclass
from logging import Logger

from rdflib import Dataset, URIRef
from koi_net.components import Cache
from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.protocol import EventType, KnowledgeObject

from .graph_parser import GraphParser


@dataclass
class GraphMirror(KnowledgeHandler):
    log: Logger
    cache: Cache
    rdf_dataset: Dataset
    graph_parser: GraphParser
    
    handler_type = HandlerType.Network
    
    def handle(self, kobj: KnowledgeObject):
        uri_ref = URIRef(str(kobj.rid))
        if kobj.normalized_event_type in (EventType.NEW, EventType.UPDATE):
            named_graph = self.graph_parser.bundle_to_graph(kobj.bundle)
            self.log.info(f"Writing {kobj.rid} to graph")
            self.rdf_dataset.remove_graph(uri_ref)
            self.rdf_dataset.add_graph(named_graph)
            
        elif kobj.normalized_event_type is EventType.FORGET:
            self.log.info(f"Deleting {kobj.rid} from graph")
            self.rdf_dataset.remove_graph(uri_ref)
            
    def start(self):
        for rid in self.cache.list_rids():
            bundle = self.cache.read(rid)
            
            named_graph = self.graph_parser.bundle_to_graph(bundle)
            self.log.info(f"Writing {bundle.rid} to graph")
            self.rdf_dataset.add_graph(named_graph)
