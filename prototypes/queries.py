
q = """
SELECT ?source ?ridType ?target
WHERE {
    GRAPH ?g {
        ?edge koi:edgeSource ?source .
        ?edge koi:edgeTarget ?target .
        ?edge koi:ridType ?ridType .
    }
}
"""

q2 = """
PREFIX koi: <orn:koi-net.vocab:>

SELECT ?source ?edge ?ridType
WHERE {
    GRAPH ?g {
        ?edge koi:ridType ?ridType .
        ?edge koi:edgeSource ?source .
    }
    FILTER (
        ?ridType != "orn:koi-net.node" &&
        ?ridType != "orn:koi-net.edge" &&
        NOT EXISTS {
            GRAPH ?nodeGraph {
                ?source koi:nodeProvides/koi:eventType ?ridType .
            }
        }
    )
}
"""

q3 = """
PREFIX koi: <orn:koi-net.vocab:>

SELECT ?node ?provides ?eventType ?stateType
WHERE {
    GRAPH ?g {
        ?node koi:nodeProvides ?provides .
        ?provides koi:eventType ?eventType .
        ?provides koi:stateType ?stateType .
    }
}
"""

q4 = """
PREFIX koi: <orn:koi-net.vocab:>
SELECT ?node ?type ?value
WHERE {
    GRAPH ?g {
        ?node a <orn:koi-net.node> .
        ?node koi:nodeProvides ?provides .
        {
            ?provides koi:eventType ?value .
            BIND("eventType" AS ?type)
        } UNION {
            ?provides koi:stateType ?value .
            BIND("stateType" AS ?type)
        }
    }
}
ORDER BY ?node ?type
"""
