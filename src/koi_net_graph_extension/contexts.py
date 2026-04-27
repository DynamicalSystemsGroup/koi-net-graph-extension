from dataclasses import dataclass

from koi_net.components import Cache
from koi_net.infra import depends_on
from rid_lib.ext import Bundle

from .rid_types import KoiNetContext

contexts = {
    KoiNetContext("manifest"): {
        "koi": "orn:koi-net.vocab:",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "rid": "@id",
        "timestamp": {
            "@id": "koi:timestamp",
            "@type": "xsd:dateTime"
        },
        "sha256_hash": {"@id": "koi:sha256Hash"}
    },
    KoiNetContext("koi-net.node"): {
        "koi": "orn:koi-net.vocab:",
        "node_type": {"@id": "koi:nodeType"},
        "provides": {"@id": "koi:nodeProvides"},
        "event": {"@id": "koi:eventType"},
        "state": {"@id": "koi:stateType"},
        "public_key": {"@id": "koi:publicKey"}
    },
    KoiNetContext("koi-net.edge"): {
        "koi": "orn:koi-net.vocab:",
        "source": {"@id": "koi:edgeSource", "@type": "@id"},
        "target": {"@id": "koi:edgeTarget", "@type": "@id"},
        "edge_type": {"@id": "koi:edgeType"},
        "status": {"@id": "koi:edgeStatus"},
        "rid_types": {"@id": "koi:ridType"}
    }
}

@dataclass
class GraphVocabLoader:
    cache: Cache
    
    @depends_on("cache")
    def start(self):
        for rid, contents in contexts.items():
            self.cache.write(
                Bundle.generate(
                    rid=rid,
                    contents=contents
                )
            )