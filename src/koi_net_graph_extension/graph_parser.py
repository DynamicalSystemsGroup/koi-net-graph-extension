from dataclasses import dataclass, field
from koi_net.components import Cache, Effector
from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.protocol import KnowledgeObject
from rdflib import Dataset, Graph, URIRef
from rid_lib.ext import Bundle
from rid_lib.types import KoiNetEdge, KoiNetNode

from .rid_types import KoiNetContext

@dataclass
class GraphParser(KnowledgeHandler):
    effector: Effector
    cache: Cache
    dataset: Dataset = field(default_factory=Dataset)
    
    handler_type = HandlerType.Network
    rid_types = (KoiNetNode, KoiNetEdge)
    
    def parse_object(
        self, 
        obj: dict, 
        graph: Graph, 
        default_context: KoiNetContext | None = None
    ):
        ctx_rid = obj.get("@context", default_context)
        if not ctx_rid:
            return
        ctx_bundle = self.effector.deref(ctx_rid)
        if not ctx_bundle:
            self.log.warning(f"Failed to dereference context {ctx_rid}")
            return
        obj["@context"] = ctx_bundle.contents
        
        print(obj)
        
        graph.parse(data=obj, format="json-ld")
        
    def parse_bundle(self, bundle: Bundle):
        named_graph = self.dataset.graph(URIRef(str(bundle.rid)))
        
        context_lookup = {
            KoiNetNode: KoiNetContext(KoiNetNode.namespace),
            KoiNetEdge: KoiNetContext(KoiNetEdge.namespace)
        }
        
        # self.log.info("Parsing manifest...")
        self.parse_object(
            obj=bundle.manifest.model_dump(mode="json", by_alias=True),
            graph=named_graph,
            default_context=KoiNetContext("manifest")
        )
        # self.log.info("Parsing contents...")
        self.parse_object(
            obj=bundle.contents | {
                "@id": str(bundle.rid),
                "@type": str(type(bundle.rid))
            },
            graph=named_graph,
            default_context=context_lookup.get(type(bundle.rid))
        )
        
        
        self.log.info(f"Parsed {len(named_graph)} triples from {bundle.rid}:")
        for triple in named_graph:
            self.log.info(", ".join(triple))
        
        return named_graph
        
    def start(self):
        for rid in self.cache.list_rids(self.rid_types):
            bundle = self.cache.read(rid)
            self.parse_bundle(bundle)
    
    def handle(self, kobj: KnowledgeObject):
        named_graph = self.parse_bundle(kobj.bundle)
        
        