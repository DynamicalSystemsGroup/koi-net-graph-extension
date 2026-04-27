from rid_lib.core import ORN


class KoiNetPredicate(ORN):
    namespace="koi-net.vocab"
    
    def __init__(self, term: str):
        self.term = term
            
    @property
    def reference(self):
        return self.term
        
    @classmethod
    def from_reference(cls, reference):
        return cls(reference)


class KoiNetContext(ORN):
    namespace="koi-net.context"
    
    def __init__(self, ref: str):
        self.ref = ref
    
    @property
    def reference(self):
        return self.ref
        
    @classmethod
    def from_reference(cls, reference):
        return cls(reference)
