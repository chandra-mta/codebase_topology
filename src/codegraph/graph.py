"""
This module contains the NetworkX graph interface based on the SQL codebase database
"""
import networkx as nx
from codegraph.db import get_session
from codegraph.models import Node, Edge

def build_graph():
    G = nx.DiGraph()
    session = get_session()

    for f in session.query(Node).all():
        G.add_node(f.id, node_type=f.node_type)

    for e in session.query(Edge).all():
        G.add_edge(e.src, e.dst, relation=e.relation)

    session.close()
    return G