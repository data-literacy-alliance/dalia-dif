from rdflib import Graph
from rdflib.compare import isomorphic


def same_graphs(g1: Graph, g2: Graph) -> bool:
    if not isomorphic(g1, g2):
        raise AssertionError(f"""\
            Graphs do not match:

            {g1.serialize()}
            -------
            {g2.serialize()}
        """)
    return True
