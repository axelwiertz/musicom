import soundfile as sf
p = "/opt/data/projects/Research/outputs/sp150_hcris/sp150_hcris_demo.wav"
info = sf.info(p)
print(info)
d, sr = sf.read(p)
print("peak", float(abs(d).max()), "rms", float((d ** 2).mean() ** 0.5))
