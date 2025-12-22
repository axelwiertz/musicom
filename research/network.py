"""
Directed graphs representing chromatic and diatonic
interval networks enriched with chord qualities (triads and seventh chords)
and voice-leading information.
Each node represents a pitch class or scale degree, and edges are annotated
with interval data and voice-leading movements between chords.
The graphs can be exported in various formats and visualized using Matplotlib.
"""
from structures.pitch import MusicPitchClass

"""
TODO:
- Extend chord qualities to include more complex chords (e.g., ninths, elevenths).
- Implement more sophisticated voice-leading algorithms considering voice ranges (PitchRegister).
"""


# interval_networks_with_chords_and_voice_leading.py
import networkx as nx
import matplotlib.pyplot as plt
from typing import List

PITCH_CLASS_MAP = zip (MusicPitchClass.NUMBERS, MusicPitchClass.NAMES_SHARP)


# --- Basic maps -----------------------------------------------------------
SEMITONE_MAP = {
    "C": 0, "C#": 1, "Db": 1, "D": 2, "D#": 3, "Eb": 3, "E": 4, "F": 5,
    "F#": 6, "Gb": 6, "G": 7, "G#": 8, "Ab": 8, "A": 9, "A#": 10, "Bb": 10, "B": 11
}

# --- Utilities ------------------------------------------------------------
def semitones_between(a: str, b: str) -> int:
    return (SEMITONE_MAP[b] - SEMITONE_MAP[a]) % MusicPitchClass.TWELVE

def transpose_pc(pc: str, semitones: int) -> str:
    idx = MusicPitchClass.NAMES_SHARP.index(pc)
    return MusicPitchClass.NAMES_SHARP[(idx + semitones) % MusicPitchClass.TWELVE]

def triad(pc: str, quality: str = "maj") -> List[str]:
    # quality: 'maj' or 'min' or 'dim'
    root = pc
    if quality == "maj":
        third = transpose_pc(root, 4)
        fifth = transpose_pc(root, 7)
    elif quality == "min":
        third = transpose_pc(root, 3)
        fifth = transpose_pc(root, 7)
    elif quality == "dim":
        third = transpose_pc(root, 3)
        fifth = transpose_pc(root, 6)
    else:
        raise ValueError("unknown triad quality")
    return [root, third, fifth]

def seventh(pc: str, quality: str = "dom") -> List[str]:
    # quality: 'dom' (7), 'maj7', 'm7', 'ø7' (half-dim)
    root = pc
    if quality == "dom":
        return [root, transpose_pc(root,4), transpose_pc(root,7), transpose_pc(root,10)]
    if quality == "maj7":
        return [root, transpose_pc(root,4), transpose_pc(root,7), transpose_pc(root,11)]
    if quality == "m7":
        return [root, transpose_pc(root,3), transpose_pc(root,7), transpose_pc(root,10)]
    if quality == "ø7":
        return [root, transpose_pc(root,3), transpose_pc(root,6), transpose_pc(root,10)]
    raise ValueError("unknown 7th quality")

# --- Voice-leading helper ------------------------------------------------
def smooth_four_voice_leading(chord_from: List[str], chord_to: List[str]) -> List[int]:
    """
    Given two lists of pitch-class names representing (unordered) chord tones,
    produce an example 4-voice voice-leading as semitone movements per voice.
    Strategy:
      - For each chord tone in chord_from, match to nearest chord tone in chord_to (in semitones),
        minimizing absolute movement (allow up or down).
      - Return list of up to 4 integer semitone movements (negative = down).
    Note: this is a heuristic example, not exhaustive.
    """
    def pc_to_val(pc):
        return SEMITONE_MAP[pc]

    from_vals = [pc_to_val(p) for p in chord_from][:4]
    # pad/truncate to 4 voices
    while len(from_vals) < 4:
        from_vals.append(from_vals[0])  # double root if needed
    to_vals = [pc_to_val(p) for p in chord_to][:4]
    while len(to_vals) < 4:
        to_vals.append(to_vals[0])

    used = set()
    moves = []
    for fv in from_vals:
        # find target minimizing absolute signed semitone distance (allow wrap via ±12)
        best_t = None
        best_move = None
        best_dist = 999
        for i, tv in enumerate(to_vals):
            if i in used: continue
            # consider moving tv by k*12 to be closest
            candidates = [tv + k*12 for k in (-1,0,1)]
            for cand in candidates:
                move = (cand - fv)
                if abs(move) < best_dist:
                    best_dist = abs(move); best_move = move; best_t = i
        if best_t is not None:
            used.add(best_t)
        moves.append(best_move if best_move is not None else 0)
    return moves

# --- Build chromatic graph ------------------------------------------------
def build_chromatic_graph() -> nx.DiGraph:
    graph = nx.DiGraph()
    # add nodes with chord qualities: triad (major/minor) and dominant 7th
    for pc in MusicPitchClass.NAMES_SHARP:
        # default triad quality: use major triad as metadata; diatonic quality will be in diatonic graph
        node_attrs = {
            "type": "pitch_class",
            "triad_maj": triad(pc, "maj"),
            "triad_min": triad(pc, "min"),
            "seventh_dom": seventh(pc, "dom"),
            "label": pc
        }
        graph.add_node(pc, **node_attrs)

    # connect every ordered pair with semitone and voice_leading info
    for a in MusicPitchClass.NAMES_SHARP:
        for b in MusicPitchClass.NAMES_SHARP:
            st = semitones_between(a, b)
            # choose representative chord voicings for voice-leading:
            # use root-position major triad for source, root-position major triad for target
            from_tri = triad(a, "maj")
            to_tri = triad(b, "maj")
            vl = smooth_four_voice_leading(from_tri, to_tri)
            graph.add_edge(a, b,
                       semitones=st,
                       relation="chromatic",
                       weight=max(0.1, 12 - st),
                       voice_leading=vl,
                       from_chord=from_tri,
                       to_chord=to_tri)
    return graph

# --- Build diatonic graph -------------------------------------------------
def build_diatonic_graph(key: str = "C") -> nx.DiGraph:
    scales = {
        "C": ["C", "D", "E", "F", "G", "A", "B"],
    }
    scale = scales[key]
    degree_names = ["I","ii","iii","IV","V","vi","vii°"]
    degree_qualities = ["maj","min","min","maj","maj","min","dim"]  # triad qualities in major
    seventh_qualities = ["maj7","m7","m7","maj7","7","m7","ø7"]

    graph = nx.DiGraph()
    # add pitch and degree nodes with chord-quality attributes
    for deg, pitch, tqual, squal in zip(degree_names, scale, degree_qualities, seventh_qualities):
        tri = triad(pitch, tqual if tqual != "dim" else "dim")
        sev = seventh(pitch, squal)
        graph.add_node(pitch, type="pitch", degree=deg, triad=tri, seventh=sev, label=pitch)
        graph.add_node(deg, type="degree", pitch=pitch, triad=tri, seventh=sev, label=deg)

    # connect pitch nodes with diatonic intervals and voice-leading using the diatonic triads
    n = len(scale)
    step_to_label = {1:"P1", 2:"M2", 3:"M3", 4:"P4", 5:"P5", 6:"M6", 7:"M7"}
    for i, src in enumerate(scale):
        for j, tgt in enumerate(scale):
            step = (j - i) % n
            step_num = step + 1  # 1..7
            label = step_to_label.get(step_num, f"step{step_num}")
            weight = max(0.1, 8 - step_num)
            # pick triads for voice-leading: root-position triads for pitch nodes
            from_tri = triad(src, "maj" if src in ["C","F","G"] else "min" if src in ["D","E","A"] else "dim")
            to_tri = triad(tgt, "maj" if tgt in ["C","F","G"] else "min" if tgt in ["D","E","A"] else "dim")
            vl = smooth_four_voice_leading(from_tri, to_tri)
            graph.add_edge(src, tgt,
                       degree_steps=step_num,
                       diatonic_interval=label,
                       relation="diatonic",
                       weight=weight,
                       voice_leading=vl,
                       from_chord=from_tri,
                       to_chord=to_tri)
            # also connect degree nodes (I, ii, ...)
            src_deg = degree_names[i]
            tgt_deg = degree_names[j]
            # use degree triads from node attributes
            f_a = graph.nodes[src_deg]["triad"] if src_deg in graph.nodes else from_tri
            f_b = graph.nodes[tgt_deg]["triad"] if tgt_deg in graph.nodes else to_tri
            vl_deg = smooth_four_voice_leading(f_a, f_b)
            graph.add_edge(src_deg, tgt_deg,
                       degree_steps=step_num,
                       diatonic_interval=label,
                       relation="diatonic_degree",
                       weight=weight,
                       voice_leading=vl_deg,
                       from_chord=f_a,
                       to_chord=f_b)
    return graph

# --- Export & plot -------------------------------------------------------
def export_graph(graph: nx.Graph, basename: str):
    nx.write_graphml(graph, f"{basename}.graphml")
    nx.write_gexf(graph, f"{basename}.gexf")
    nx.write_gml(graph, f"{basename}.gml")

def plot_graph(graph: nx.Graph, basename: str, figsize=(10,8)):
    plt.figure(figsize=figsize)
    pos = nx.spring_layout(graph, seed=42)
    node_colors = []
    labels = {}
    for n, d in graph.nodes(data=True):
        labels[n] = d.get("label", n)
        if d.get("type") == "pitch":
            node_colors.append("lightblue")
        elif d.get("type") == "degree":
            node_colors.append("lightgreen")
        else:
            node_colors.append("lightgray")
    nx.draw_networkx_nodes(graph, pos, node_color=node_colors, node_size=700)
    nx.draw_networkx_labels(graph, pos, labels=labels, font_size=9)
    widths = [max(0.4, d.get("weight",1.0)) for _,_,d in graph.edges(data=True)]
    nx.draw_networkx_edges(graph, pos, arrowstyle="->", arrowsize=12, width=widths)
    # edge labels: show semitones or diatonic interval and abbreviated voice-leading
    edge_labels = {}
    for u,v,d in graph.edges(data=True):
        if "semitones" in d:
            vl = d.get("voice_leading", [])
            vl_short = ",".join(f"{int(x)}" for x in vl[:4])
            edge_labels[(u,v)] = f"{d['semitones']}st | vl[{vl_short}]"
        elif "diatonic_interval" in d:
            vl = d.get("voice_leading", [])
            vl_short = ",".join(f"{int(x)}" for x in vl[:4])
            edge_labels[(u,v)] = f"{d['diatonic_interval']} | vl[{vl_short}]"
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=edge_labels, font_size=7)
    plt.axis("off")
    plt.tight_layout()
    plt.savefig(f"{basename}.png", dpi=300)
    plt.close()

# --- Main -----------------------------------------------------------------
if __name__ == "__main__":
    chroma = build_chromatic_graph()
    export_graph(chroma, "chromatic_with_chords_and_voice_leading")
    plot_graph(chroma, "chromatic_with_chords_and_voice_leading", figsize=(10,10))

    diat = build_diatonic_graph("C")
    export_graph(diat, "diatonic_C_with_chords_and_voice_leading")
    plot_graph(diat, "diatonic_C_with_chords_and_voice_leading", figsize=(9,7))

    print("Exported graph files and PNGs for chromatic and diatonic graphs.")
