import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

wait, avg, std = np.genfromtxt('lifetime_Neumann_Striebel.txt', delimiter=',', unpack=True)
start = 0  


fit_func = lambda t, N0, tau, off: N0*np.exp(-t/tau)+ off
guess = (300,  60,  1)
popt, pcov = curve_fit(fit_func, wait[start:], avg[start:], sigma=std[start:], p0=guess)

print(popt)
print(pcov)

N0 = popt[0]
tau = popt[1]
off = popt[2]

N0_err = pcov[0][0]**0.5
tau_err = pcov[1][1]**0.5
off_err = pcov[2][2]**0.5

fit_results=f'''Fit results:
N_0 = ({np.round(N0,2)} +- {np.round(N0_err,2)})
tau =  ({np.round(tau,2)} +- {np.round(tau_err,2)}) ms
off =  ({np.round(off,2)} +- {np.round(off_err,2)})'''

t = np.linspace(min(wait), max(wait), 100)
plt.errorbar(wait, avg, yerr=std, label='data', capsize=5, fmt='.')
plt.xlabel('wait-time [ms]')
plt.ylabel('avg dip depth')
plt.plot(t, fit_func(t, *popt), label='fit')
plt.legend()


plt.text(300, 12, fit_results)

plt.savefig('lifetime.png')
plt.show()


