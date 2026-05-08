from rdflib import Graph, Dataset, URIRef

doc = {
    "@context": {"timestamp": "http://example.org/timestamp"},
    "@id": "urn:bundle:zzz",
    "timestamp": "2026-04-27",
    "@graph": [
        {
            "@id": "urn:slack.message:xxx",
            "http://example.org/mentionsUser": "urn:github.user:yyy"
        }
    ]
}

g = Graph(identifier=URIRef("urn:bundle:zzz"))
g.parse(data=doc, format="json-ld")

for triple in g:
    print(triple)