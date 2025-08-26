import random
#from collections import Counter
import numpy as np
#from tqdm import tqdm
from music21 import corpus, note, chord, stream, meter, tempo
#import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
from tensorflow.keras.utils import to_categorical

# ---------------------------
# 1) Data extraction / tokenization
# ---------------------------
# For demo, use a few Bach chorales from music21 corpus. Replace with your dataset.
SOURCES = ['bach/bwv66.6', 'bach/bwv1.1', 'bach/bwv2.7', 'bach/bwv3.6', 'bach/bwv4.5']

def extract_monophonic_tokens(part_in):
    # Flatten part_in and extract sequence of (pitch_or_rest, dur_token)
    tokens = []
    for el in part_in.recurse().notesAndRests:
        dur = el.duration.quarterLength
        # quantize durations to common denominators (e.g., 0.25)
        dur_q = round(dur * 4) / 4.0
        if isinstance(el, note.Rest):
            tokens.append(f"REST_{dur_q}")
        elif isinstance(el, chord.Chord):
            top = max(el.pitches)
            tokens.append(f"NOTE_{top.nameWithOctave}_{dur_q}")
        else:
            tokens.append(f"NOTE_{el.pitch.nameWithOctave}_{dur_q}")
    return tokens


# ---------------------------
# 3) Generation
# ---------------------------
def sample_from_probs(probs, temperature_in=1.0):
    probs = np.asarray(probs).astype('float64')
    if temperature_in <= 0:
        return np.argmax(probs)
    probs = np.log(probs + 1e-8) / temperature_in
    exp = np.exp(probs)
    probs = exp / np.sum(exp)
    return np.random.choice(len(probs), p=probs)

def tokens_to_stream(idx_sequence, idx_to_token) -> stream.Part:
    # Convert generated token indices back to music21 Stream
    part_out = stream.Part()
    part_out.append(tempo.MetronomeMark(number=90))
    part_out.append(meter.TimeSignature('4/4'))
    offset = 0.0
    for idx in idx_sequence:
        tok = idx_to_token[int(idx)]
        if tok.startswith('REST_'):
            dur = float(tok.split('_')[1])
            r = note.Rest(quarterLength=dur)
            part_out.insert(offset, r)
        else:
            _, pitch, dur = tok.split('_')
            dur = float(dur)
            n = note.Note(pitch, quarterLength=dur)
            part_out.insert(offset, n)
        offset += dur
    return part_out

def main():
    all_tokens = []
    for src in SOURCES:
        s = corpus.parse(src)
        # take the top part/ soprano where present
        part = s.parts[0] if len(s.parts) > 0 else s
        toks = extract_monophonic_tokens(part)
        all_tokens.append(toks)

    # Flatten and build vocabulary
    flat = [t for seq in all_tokens for t in seq]
    vocab = sorted(set(flat))
    token_to_idx = {t: i for i, t in enumerate(vocab)}
    idx_to_token = {i: t for t, i in token_to_idx.items()}

    # Create sequences for training (simple next-token prediction)
    SEQ_LEN = 32
    step = 1
    inputs = []
    targets = []
    for seq in all_tokens:
        if len(seq) <= SEQ_LEN: continue
        for i in range(0, len(seq) - SEQ_LEN, step):
            chunk = seq[i:i + SEQ_LEN]
            nxt = seq[i + SEQ_LEN]
            inputs.append([token_to_idx[t] for t in chunk])
            targets.append(token_to_idx[nxt])

    print(f"Vocab size: {len(vocab)}, training examples: {len(inputs)}")

    X = np.array(inputs, dtype=np.int32)
    y = to_categorical(targets, num_classes=len(vocab))

    # ---------------------------
    # 2) Build & train small RNN
    # ---------------------------
    EMBED_DIM = 64
    HIDDEN = 128
    BATCH = 32
    EPOCHS = 40

    model = Sequential([
        Embedding(input_dim=len(vocab), output_dim=EMBED_DIM, input_length=SEQ_LEN),
        LSTM(HIDDEN, return_sequences=False),
        Dense(len(vocab), activation='softmax')
    ])
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.summary()

    model.fit(X, y, batch_size=BATCH, epochs=EPOCHS)

    # seed: choose a random training sequence
    start_idx = random.randrange(0, len(inputs))
    seed = inputs[start_idx].copy()
    generated = seed.copy()
    GEN_LEN = 200
    temperature = 0.8

    for _ in range(GEN_LEN):
        x = np.array([generated[-SEQ_LEN:]])
        preds = model.predict(x, verbose=0)[0]
        idx = sample_from_probs(preds, temperature_in=temperature)
        generated.append(int(idx))

    gen_part = tokens_to_stream(generated[SEQ_LEN:SEQ_LEN+GEN_LEN], idx_to_token)

    score = stream.Score()
    score.insert(0, gen_part)

    out_xml = 'rnn_generated.musicxml'
    out_midi = 'rnn_generated.mid'
    score.write('musicxml', fp=out_xml)
    score.write('midi', fp=out_midi)
    print(f"Wrote {out_xml} and {out_midi}")

if __name__ == '__main__':
    main()
