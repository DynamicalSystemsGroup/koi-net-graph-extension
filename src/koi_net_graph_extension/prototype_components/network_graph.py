from dataclasses import dataclass
from logging import Logger
from typing import Literal

from rdflib import Dataset
from rid_lib import RID, RIDType
from rid_lib.types import KoiNetEdge, KoiNetNode

from koi_net.components.identity import NodeIdentity
from koi_net.protocol.edge import EdgeStatus

KOI = "orn:koi-net.vocab:"


@dataclass
class NetworkGraph:
    rdf_dataset: Dataset
    identity: NodeIdentity
    log: Logger

    def get_edge(
        self, source: KoiNetNode, target: KoiNetNode
    ) -> KoiNetEdge | None:
        result = self.rdf_dataset.query(f"""
            PREFIX koi: <{KOI}>

            SELECT ?edge
            WHERE {{
                GRAPH ?g {{
                    ?edge koi:edgeSource <{source}> .
                    ?edge koi:edgeTarget <{target}> .
                }}
            }}
        """)
        for row in result:
            return RID.from_string(str(row.edge))
        return None

    def get_edges(
        self,
        direction: Literal["in", "out"] | None = None,
    ) -> list[KoiNetEdge]:
        self_uri = f"<{self.identity.rid}>"

        if direction == "out":
            pattern = f"?edge koi:edgeSource {self_uri} ."
        elif direction == "in":
            pattern = f"?edge koi:edgeTarget {self_uri} ."
        else:
            pattern = f"""
                {{ ?edge koi:edgeSource {self_uri} . }}
                UNION
                {{ ?edge koi:edgeTarget {self_uri} . }}
            """

        result = self.rdf_dataset.query(f"""
            PREFIX koi: <{KOI}>

            SELECT DISTINCT ?edge
            WHERE {{
                GRAPH ?g {{
                    {pattern}
                }}
            }}
        """)
        return [RID.from_string(str(row.edge)) for row in result]

    def get_neighbors(
        self,
        direction: Literal["in", "out"] | None = None,
        status: EdgeStatus | None = None,
        allowed_type: RIDType | None = None,
    ) -> list[KoiNetNode]:
        self_uri = f"<{self.identity.rid}>"
        status_filter = f'?edge koi:edgeStatus "{status.value}" .' if status else ""
        type_filter = f'?edge koi:ridType "{allowed_type}" .' if allowed_type else ""

        out_pattern = f"""
            ?edge koi:edgeSource {self_uri} .
            ?edge koi:edgeTarget ?neighbor .
            {status_filter}
            {type_filter}
        """
        in_pattern = f"""
            ?edge koi:edgeTarget {self_uri} .
            ?edge koi:edgeSource ?neighbor .
            {status_filter}
            {type_filter}
        """

        if direction == "out":
            where_body = f"GRAPH ?g {{ {out_pattern} }}"
        elif direction == "in":
            where_body = f"GRAPH ?g {{ {in_pattern} }}"
        else:
            where_body = f"""
                GRAPH ?g {{
                    {{ {out_pattern} }}
                    UNION
                    {{ {in_pattern} }}
                }}
            """

        result = self.rdf_dataset.query(f"""
            PREFIX koi: <{KOI}>

            SELECT DISTINCT ?neighbor
            WHERE {{ {where_body} }}
        """)
        return [RID.from_string(str(row.neighbor)) for row in result]
