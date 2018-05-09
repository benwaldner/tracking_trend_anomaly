import pandas as pd
import numpy as np
import scipy.fftpack
from matplotlib import  pyplot as plt

f = ""

y = np.fromfile(open(f,'r'), dtype=float)

N = len(y)
#x = np.linspace(0,2*np.pi,N)
#y = np.sin(x) + np.random.random(N) * 0.2

w = scipy.fftpack.rfft(y) # revert
f = scipy.fftpack.rfftfreq(N, 1) # frequency
spectrum = w**2

cutoff_idx = spectrum < (spectrum.max()/5) 
w2 = w.copy()
w2[cutoff_idx] = 0

y2 = scipy.fftpack.irfft(w2)

f_out1 = open("", 'a')
f_out2 = open("", 'a')


#for j in y:
#    print >> f_out1, j

for i in y2:
    print >> f_out2, i
plt.plot(y2)
