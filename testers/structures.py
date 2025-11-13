def main():
    # Piano register from A0 to C8
    reg = PitchRegister(TwelveTET.A, 0, TwelveTET.C, 8)
    reg.show()

    pos = reg.index_of(3, 7)  # octave 3, pitchclass 7 -> index
    next_pos = reg.transpose(pos,reg.ASCENDING)  # next pitchclass
    octave_pitchclass = reg.get_at(next_pos)
    print (f'PitchRegister: pos {pos} -> next pos {next_pos} -> (octave, pitchclass) {octave_pitchclass}')

    pcs = PitchClassSet()
    print(f'PitchClassSet combinations: {len(pcs.combinations)}')

    scale5cmajor = MusicScale(Diatonic.PENTA, Diatonic.SCALE,
                              tonic=TwelveTET.C, mode=Diatonic.major_mode)
    scale7cmajor = MusicScale(Diatonic.HEPTA, Diatonic.SCALE,
                              tonic=TwelveTET.C, mode=Diatonic.major_mode)

    m21intervals = list(interval.ChromaticInterval(n) for n in TwelveTET.PITCH_CLASS_NUMBERS)

    # Table of all absolute chromatic data along pitch number set
    interval_pattern7 = MusicPattern(Diatonic.HEPTA, Diatonic.SCALE)
    interval_pattern7.save()
    scale7 = MusicScale(Diatonic.HEPTA, Diatonic.SCALE, tonic=TwelveTET.C, mode=Diatonic.major_mode)

    # Pitch helixes for heptatonic modes
    # Major
    majormodehelix = TwelveTET.OCTAVES * interval_pattern7.modeshelix[Diatonic.major_mode]
    # Minor
    minormodehelix = TwelveTET.OCTAVES * interval_pattern7.modeshelix[Diatonic.minor_mode]

    # Major mode pitch helixes for all tonics (C, C#, D, ..., B)
    majorscales = [majormodehelix[-x:] + majormodehelix[:-x] for x in range(TwelveTET.TWELVE)]
    minorscales = [minormodehelix[-x:] + minormodehelix[:-x] for x in range(TwelveTET.TWELVE)]

    chromatic_data = pd.DataFrame(majorscales)
    chromatic_data.to_excel(Config.DEFAULT_PATH + 'ChromaticLayer.xlsx', index=True, sheet_name='Pitch')

    chromatic_table = chromatic_data.transpose()
    #chromatic_table.columns = ['Nr', 'ClassNr', 'ClassChr', 'Freq'] + list(TwelveTET.PITCH_CLASS_NAMES_SHARP)
    chromatic_table.to_excel(Config.DEFAULT_PATH + 'ChromaticTable.xlsx', index=True, sheet_name='Pitch')

    hepta_major_arr = np.array(majorscales)

    pc_circle = Circle(TwelveTET.TWELVE, TwelveTET.PITCH_CLASS_NAMES_SHARP)
    pc_circle.show()

#    pc_circle.show(pcp7.majormodeschromatic, TwelveTET.PITCH_CLASS_NAMES_SHARP, 'Major circle')



if __name__ == '__main__':
    main()
