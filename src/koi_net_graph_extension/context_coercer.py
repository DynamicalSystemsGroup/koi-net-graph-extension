from dataclasses import dataclass

from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.protocol import KnowledgeObject
from rid_lib.ext import Manifest
from rid_lib.types import KoiNetEdge, KoiNetNode

from .rid_types import KoiNetContext


@dataclass
class ContextCoercer(KnowledgeHandler):
    handler_type = HandlerType.Bundle
    rid_types = (KoiNetNode, KoiNetEdge)
    
    def handle(self, kobj: KnowledgeObject):
        if "@context" in kobj.contents:
            return
        
        self.log.info("INJECTING CONTEXT")
        kobj.contents["@context"] = str(KoiNetContext(type(kobj.rid).namespace))
        kobj.manifest = Manifest.generate(
            rid=kobj.rid,
            data=kobj.contents,
        )
        kobj.manifest.context = "orn:koi-net.context:manifest"
        
        return kobj