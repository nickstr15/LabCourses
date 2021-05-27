#---Import all packages and set working directory-------------
import glob
import numpy as np
import matplotlib.pyplot as plt
#import peakutils #activate only if installed // used for peakdetection
from matplotlib.backends.backend_pdf import PdfPages
import re
numbers = re.compile(r'(\d+)')
def numericalSort(value):
    parts = numbers.split(value)
    parts[1::2] = map(int, parts[1::2])
    return parts

#---Settings------------------------------------------------
filepath = '*.csv'
peakdetection = False
exportpdf = True
pdfname = 'FrequencyScans.pdf'
#-----------------------------------------------------------
files = sorted(glob.glob(filepath), key=numericalSort)
fig, axs = plt.subplots(len(glob.glob(filepath)),1, figsize=(50, 50))
fig.subplots_adjust(hspace = .3, wspace=0.2)
axs = axs.ravel()

for i, item in enumerate(files):
    axs[i].plot(np.loadtxt(item, usecols=[0], delimiter=','), np.loadtxt(item, usecols=[1], delimiter=','))
    axs[i].set_title(item, fontsize=25)
    axs[i].set_ylabel('Amplitude[a.u]', fontsize=20)
    axs[i].set_xlabel('Frequency [MHz]', fontsize=20)
fig.suptitle('Bestimmung Zyklotronfrequenz', fontsize=80).set_y(0.93)


#plt.show() #activate if you want to see plot instead of just export pdf
if exportpdf:
    pp = PdfPages(pdfname)
    plt.savefig(pp, format='pdf')
    pp.close()

