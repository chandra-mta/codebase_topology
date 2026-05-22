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
        node_attrs = orm_to_dict(f)
        #: Convert datetime to string for JSON serialization
        node_attrs['last_updated'] = node_attrs['last_updated'].isoformat() if node_attrs['last_updated'] else None
        G.add_node(f.id, **node_attrs)

    for e in edges:
        edge_attrs = orm_to_dict(e)
        #: Convert datetime to string for JSON serialization
        edge_attrs['last_updated'] = edge_attrs['last_updated'].isoformat() if edge_attrs['last_updated'] else None
        G.add_edge(e.src_id, e.dst_id, **edge_attrs)
    return G