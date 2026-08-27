import json
d = json.load(open('/opt/data/projects/016-genre-pattern-dataset/data/klezmer_freylekhs.json'))
print('VALID JSON')
print('Top keys:', list(d.keys()))
print('Subgenre:', d['subgenre'])
print('Rows:', d['musicmatrix_mapping']['rows'])
print('Cols:', d['musicmatrix_mapping']['cols'])
print('Grid rows:', list(d['musicmatrix_mapping']['unit_matrix']['grid'].keys()))
print('Slots per row:', len(d['musicmatrix_mapping']['unit_matrix']['grid']['Lead (Violin/Clarinet)']['slots']))