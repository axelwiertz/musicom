'''
Music Samples
'''

# Scales
s1 = S('C Major')
t1 = s1.get('-,1,-,2') % (1 / 2,)
t1 = s1.get('r,1,r,2')

#1
chord ('F2, A2, F3')
S('F major').get('1.-2;3.-2;1.-1')
#2
chord('C2, C3, E3, G3')


# Melody

# Musical composition examples page 13

s1 = S('F major')

b1 = s1.get('-') + s1.get('1.-1; 3.-1; 1') + s1.get('5.-1; 5   ; 7.-1;2') + s1.get('1.-1; 5.-1; 1   ;3')
b2 = s1.get('6.-1; 4.-1; 1   ;4') + s1.get('1.-1; 3.-1; 1   ;5') + s1.get('6.-1; 3.-1; 1   ;6') + s1.get('5.-1; 5.-1; 2   ;7')
b3 = s1.get('1.-1; 5.-1; 3   ;1.+1')%(1,)


b21 = s1.get('-') + s1.get('1') + s1.get('7.-1; 2') + s1.get('5.-1; 3')
b22 = s1.get('6.-1; 4') + s1.get('3.-1; 5') + s1.get('4.-1; 6') + s1.get('2.-1; 7')
b23 = s1.get('1.-1; 1.+1')%(1,)

play (b1 + b2 + b3)
play (b21 + b22 + b23)

