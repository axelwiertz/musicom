# chromatic_interval_network_to_networkx.py
import networkx as nx
import matplotlib.pyplot as plt

def make_chromatic_interval_network():
    """
    Returns a dict-based chromatic graph:
    { source: [ (target, semitones_root, voice_leading_list, relation, weight, info_dict), ... ] }
    Semitones: positive = upward from source root to target root (mod 12)
    Example key = C (I = C)
    """
    g = {}

    def add_node(n):
        if n not in g:
            g[n] = []

    def connect(a, b, semitones_root, voice_leading=None, relation="", weight=1.0, info=None):
        add_node(a); add_node(b)
        g[a].append((b, semitones_root, voice_leading or [], relation, weight, info or {}))

    nodes = [
        "I", "bVII", "bVII7", "IV", "V", "V7", "ii", "iii", "vi",
        "chromatic_mediant", "Mixolydian", "backdoor", "plagal", "dominant_substitute"
    ]
    for n in nodes: add_node(n)

    connect("I", "bVII", 10, voice_leading=[-2, -2, -1], relation="modal_borrow", weight=0.4,
            info={"example":"C -> Bb (root down M2 / -2 semitones)"})
    connect("bVII", "I", 2, voice_leading=[2,2,1], relation="modal_resolution", weight=0.8,
            info={"example":"Bb -> C (root up M2 / 2 semitones)"})
    connect("bVII", "bVII7", 0, voice_leading=[0,-1], relation="add7_extension", weight=0.9,
            info={"example":"Bb -> Bb7 (add minor7 A♭/G#)"})
    connect("bVII7", "I", 2, voice_leading=[2,1,-1], relation="backdoor", weight=0.9,
            info={"example":"Bb7 -> C (backdoor cadence)"})
    connect("bVII", "IV", 7, voice_leading=[-3,0,2], relation="subdominant_motion", weight=0.6,
            info={"example":"Bb -> F (root up P5 / 7 semitones from Bb to F)"})
    connect("IV", "I", 7, voice_leading=[-5,0,0], relation="plagal", weight=0.5,
            info={"example":"F -> C (plagal motion)"})
    connect("V", "I", 5, voice_leading=[-1,-2,-2], relation="dominant_resolution", weight=1.0,
            info={"example":"G -> C (dominant resolution)"})
    connect("ii", "V", 5, voice_leading=[2,-1,-1], relation="ii_v", weight=0.9)
    connect("bVII", "chromatic_mediant", 4, voice_leading=[3,3,4], relation="chromatic_mediant_relation", weight=0.3)
    connect("Mixolydian", "bVII", 10, voice_leading=[0], relation="diatonic_in_mode", weight=1.0)
    connect("bVII7", "V", 9, voice_leading=[-2,-1], relation="dominant_substitute", weight=0.5,
            info={"example":"Bb7 -> G (root up 9 semitones / down 3)"})
    connect("I", "iii", 4, voice_leading=[4,3,3], relation="mediant", weight=0.4)
    connect("iii", "vi", 5, voice_leading=[1,2,2], relation="mediant_to_submediant", weight=0.4)

    return g

def to_networkx(chromatic_graph, directed=True):
    """
    Convert the dict-based chromatic graph to a NetworkX graph.
    Edge attributes: semitones_root, voice_leading, relation, weight, info
    """
    G = nx.DiGraph() if directed else nx.Graph()
    for src, edges in chromatic_graph.items():
        G.add_node(src)
        for (t, st, vl, rel, w, info) in edges:
            G.add_node(t)
            G.add_edge(src, t,
                       semitones_root=int(st),
                       voice_leading=list(vl),
                       relation=str(rel),
                       weight=float(w),
                       info=dict(info))
    return G

def export_graph(G, basename="chromatic_intervals"):
    """
    Export to GraphML, GEXF, and GML. Also save a simple PNG visualization.
    Requires networkx and matplotlib.
    """
    nx.write_graphml(G, f"{basename}.graphml")
    nx.write_gexf(G, f"{basename}.gexf")
    nx.write_gml(G, f"{basename}.gml")

    # Simple plotting
    plt.figure(figsize=(10, 7))
    pos = nx.spring_layout(G, seed=42)
    nx.draw_networkx_nodes(G, pos, node_color="lightblue", node_size=900)
    nx.draw_networkx_labels(G, pos, font_size=10)
    # draw directed edges with widths by weight
    edges = G.edges(data=True)
    widths = [max(0.4, d.get("weight", 1.0)) * 1.5 for (_, _, d) in edges]
    nx.draw_networkx_edges(G, pos, arrowstyle="->", arrowsize=16, width=widths, connectionstyle="arc3,rad=0.1")
    # edge labels: show semitone root interval + relation
    edge_labels = {(u, v): f"{d.get('semitones_root')}, {d.get('relation')}" for u, v, d in edges}
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(f"{basename}.png", dpi=300)
    plt.close()

if __name__ == "__main__":
    chroma = make_chromatic_interval_network()
    G = to_networkx(chroma, directed=True)
    export_graph(G, basename="chromatic_interval_network")
    print("Exports written: chromatic_interval_network.graphml/.gexf/.gml and .png")
