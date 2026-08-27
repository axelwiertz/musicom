import random, os
styles_dir = "/opt/data/projects/Styles/"
excl = {"_Comparison","_Data_Patterns","Research","Poetry","Production","Percussion","Other","016-genre-pattern-dataset"}
folders = [d for d in os.listdir(styles_dir) if os.path.isdir(os.path.join(styles_dir,d)) and d not in excl]
methods = [
    "stochastic-markov-pitch","euclidean-rhythm","fhn-neural","cellular-automaton",
    "l-system","son-clave","pentatonic-gamelan","circle-of-fifths","lydian-modal",
    "markov-harmony","random-walk","fibonacci-phrase","tresillo-cuba","sine-sweep",
]
# recent methods (last 7 days) — avoid these
recent = ["fhn-neural","cellular-automaton","stochastic-markov-pitch","euclidean-rhythm"]
pool = [m for m in methods if m not in recent]
style = random.choice(sorted(folders))
method = random.choice(pool)
print("STYLE="+style)
print("METHOD="+method)