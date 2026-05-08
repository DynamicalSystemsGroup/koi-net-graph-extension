from koi_net.config import FullNodeConfig, FullNodeProfile, KoiNetConfig
from koi_net.core import FullNode
from rid_lib import RID, RIDType



class HungryNodeConfig(FullNodeConfig):
    koi_net: KoiNetConfig = KoiNetConfig(
        node_name="hungry_node",
        node_profile=FullNodeProfile(),
        rid_types_of_interest=[RIDType.from_string("orn:example.type")]
    )

class HungryNode(FullNode):
    config_schema = HungryNodeConfig



if __name__ == "__main__":
    node = HungryNode()
    node.run()