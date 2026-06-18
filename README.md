# koi-net-graph-extension

An extension for the KOI-net library. Provides components, RID types, and vocabulary for handling graph-based knowledge objects in JSON-LD format. The easiest way to use this library is adding the `GraphMixin` to your node class:

```python
from koi_net.core import FullNode
from koi_net_graph_extension.core import GraphMixin

class MyNode(FullNode, GraphMixin):
    ...
```