from dataclasses import dataclass
from logging import Logger

from deepdiff import DeepDiff
from koi_net.components.interfaces import KnowledgeHandler, HandlerType
from koi_net.protocol import EventType, KnowledgeObject


@dataclass
class UpdateDiffMonitor(KnowledgeHandler):
    log: Logger
    
    handler_type = HandlerType.Network
    
    def handle(self, kobj: KnowledgeObject):
        if kobj.normalized_event_type is not EventType.UPDATE:
            return
        
        diff = DeepDiff(kobj.prev_bundle.contents, kobj.contents)
        self.log.info("UPDATE DIFF DETECTED")
        self.log.info(diff)