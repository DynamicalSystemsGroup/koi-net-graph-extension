from dataclasses import dataclass
from logging import Logger
from koi_net.components import Cache, Effector
from rdflib import Graph, URIRef
from rid_lib import RID
from rid_lib.ext import Bundle
from rid_lib.types import KoiNetEdge, KoiNetNode

from .rid_types import KoiNetContext

@dataclass
class GraphParser:
    log: Logger
    effector: Effector
    cache: Cache
    
    def retrieve_context(self, ctx_rid: KoiNetContext):
        ctx_bundle = self.effector.deref(ctx_rid)
        if ctx_bundle:
            return ctx_bundle.contents
        else:
            self.log.warning("Failed to retrieve context")
            return {}
    
    def preprocess_object(
        self, 
        obj: dict, 
        default_context: KoiNetContext | None = None
    ):
        obj = obj.copy()
        expanded_ctx = {}
        ctx = obj.get("@context", default_context)
        if type(ctx) is str:
            try:
                ctx_rid = RID.from_string(ctx)
                expanded_ctx |= self.retrieve_context(ctx_rid)
            except TypeError:
                self.log.warning("Invalid RID in context")
                
        elif type(ctx) is dict:
            expanded_ctx |= ctx
            
        elif type(ctx) is list:
            for item in ctx:
                if type(item) is str:
                    try:
                        ctx_rid = RID.from_string(item)
                        expanded_ctx |= self.retrieve_context(ctx_rid)
                    except TypeError:
                        self.log.warning("Invalid RID in context")
                elif type(item) is dict:
                    expanded_ctx |= item
                else:
                    continue
                
        else:
            self.log.info("No context found")
            return obj
        
        self.log.info(f"Expanded context: {expanded_ctx}")
        
        obj["@context"] = expanded_ctx
        
        return obj
        
    def bundle_to_graph(self, bundle: Bundle):
        named_graph = Graph(identifier=URIRef(str(bundle.rid)))

        context_lookup = {
            KoiNetNode: KoiNetContext(KoiNetNode.namespace),
            KoiNetEdge: KoiNetContext(KoiNetEdge.namespace)
        }
        
        self.log.info(f"Parsing bundle {bundle.rid}")
        self.log.info("Processing manifest")
        manifest_obj = self.preprocess_object(
            obj=bundle.manifest.model_dump(mode="json", by_alias=True),
            default_context=KoiNetContext("manifest")
        )
        named_graph.parse(data=manifest_obj, format="json-ld")
        
        self.log.info("Processing contents")
        contents_obj = self.preprocess_object(
            obj=bundle.contents | {
                "@id": str(bundle.rid),
                "@type": str(type(bundle.rid))
            },
            default_context=context_lookup.get(type(bundle.rid))
        )
        named_graph.parse(data=contents_obj, format="json-ld")
        
        self.log.info(f"Parsed {len(named_graph)} triples from {bundle.rid}:")
        for triple in named_graph:
            self.log.info(", ".join(triple))
        
        return named_graph
