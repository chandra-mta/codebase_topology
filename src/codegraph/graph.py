"""
This module contains the NetworkX graph interface based on the SQL codebase database
"""
import networkx as nx
from codegraph.db import get_session, orm_to_dict
from codegraph.models import Node, Edge



def build_graph(nodes: list[Node], edges: list[Edge]) -> nx.DiGraph:
    """
    Build a graph with provided queried nodes and edges
    """
    G = nx.DiGraph()
    for f in nodes:
        G.add_node(f.id, **orm_to_dict(f))

    for e in edges:
        G.add_edge(e.src_id, e.dst_id, **orm_to_dict(e))
    return G