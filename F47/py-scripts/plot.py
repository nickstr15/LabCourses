import matplotlib.pyplot as plt
import numpy as np

freq, amp = np.genfromtxt(r'2021_04_27_13_49_03_FullRangeScan\2021_04_27_13_49_04_28.12V_1.3A_360-400MHz_-12dBm.csv', delimiter=',', unpack=True)
plt.plot(freq, amp)
plt.show()