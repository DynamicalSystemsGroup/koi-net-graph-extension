from dataclasses import dataclass

import pyshacl
from rdflib import Dataset, Graph, URIRef
from rid_lib.ext import Bundle
from rid_lib.types import KoiNetEdge
from koi_net.protocol import EdgeProfile, EdgeStatus, Event, KnowledgeObject, EventType
from koi_net.components.interfaces import KnowledgeHandler, STOP_CHAIN, HandlerType
from koi_net.components import NodeIdentity, KobjQueue, EventQueue, Cache

from .graph_parser import GraphParser


@dataclass
class ShaclEdgeNegotiationHandler(KnowledgeHandler):
    identity: NodeIdentity
    cache: Cache
    event_queue: EventQueue
    kobj_queue: KobjQueue
    rdf_dataset: Dataset
    graph_parser: GraphParser
    
    handler_type = HandlerType.Bundle
    rid_types = (KoiNetEdge,)
    event_types = (EventType.NEW, EventType.UPDATE)
    
    def handle(self, kobj: KnowledgeObject):
        """Handles edge negotiation process.
        
        Automatically approves proposed edges if they request RID types this 
        node can provide (or KOI node, edge RIDs). Validates the edge type 
        is allowed for the node type (partial nodes cannot use webhooks). If 
        edge is invalid, a `FORGET` event is sent to the other node.
        """

        # only handle incoming events (ignore internal edge knowledge objects)
        if kobj.source is None: 
            return
        
        edge_profile = kobj.bundle.validate_contents(EdgeProfile)

        # indicates peer subscribing to this node
        if edge_profile.source == self.identity.rid:
            if edge_profile.status != EdgeStatus.PROPOSED:
                return
            
            self.log.debug("Handling edge negotiation")
            
            # FROM HERE BELOW, SHACL VALIDATION COVERAGE
            
            shacl_graph = Graph()
            shacl_graph.parse("edge_constraint.ttl")
            
            edge_uri = URIRef(str(kobj.rid))
            curr_edge_graph = self.graph_parser.bundle_to_graph(kobj.bundle)
            prev_edge_graph = self.rdf_dataset.graph(edge_uri)
            
            try:
                self.rdf_dataset.remove_graph(edge_uri)
                self.rdf_dataset.add_graph(curr_edge_graph)
            
                conform, results_graph, results_text = pyshacl.validate(
                    data_graph=self.rdf_dataset,
                    shacl_graph=shacl_graph
                )
                
                self.log.info(results_text)
                
                if conform:
                    self.log.debug("Approving proposed edge")
                    edge_profile.status = EdgeStatus.APPROVED
                    updated_bundle = Bundle.generate(kobj.rid, edge_profile.model_dump())

                    self.kobj_queue.push(bundle=updated_bundle, event_type=EventType.UPDATE)
                    return
                else:
                    self.log.warning(results_text)
                    # event = Event.from_rid(EventType.FORGET, kobj.rid)
                    # self.event_queue.push(event, edge_profile.target)
                    return STOP_CHAIN
            
            finally:
                self.rdf_dataset.remove_graph(edge_uri)
                self.rdf_dataset.add_graph(prev_edge_graph)
                
        elif edge_profile.target == self.identity.rid:
            if edge_profile.status == EdgeStatus.APPROVED:
                self.log.debug("Edge approved by other node!")

