import devices
import time
import os
import numpy as np

#============================================
# Definition of constants / measurement range
#============================================

#create path for datafiles (ADD YOUR GROUP NAME!):
today = time.strftime("%Y_%m_%d_%H_%M_%S")
directoryname = 'Neumann_Striebel_'+ today + "_FullRangeScan"
if not os.path.exists(directoryname):
    os.makedirs(directoryname)
path = directoryname

#Trigger timings
load = 500
wait1 = 5
excite = 10
wait2 = 5
rigol = 5   # the Rigol spectrum analyzer has a 30 ms trigger delay
wait3 = 0 
detect = 50
cycle_time = load + wait1 + excite + wait2 + rigol + wait3 + detect
     
devices.set_time('load', load)
devices.set_time('wait1', wait1)
devices.set_time('excite', excite)
devices.set_time('wait2', wait2)
devices.set_time('detect', detect)
devices.set_time('wait3', wait3)
devices.set_time('rigol', rigol)

#number of averages per cycle
average_num = 5 

#trap ring voltage
ring_voltages = [24, 27, 28.12, 30, 35, 40]

#magnet coil currents
coil_currents = [1.1, 1.15, 1.2, 1.25, 1.3]


#finalize setup for measurement: set spectrum analyzer to zero span mode
devices.set_analyzer_to_zero_span(center_freq="57.3MHz", ref_level = "-15.5", 
                              PDIV_scale = "5.0", sweep_time="250ms")

print("Start...")

#============================================
# MEASUREMENT FUNCTION
#============================================

def scanFreq(freq_min, freq_max, freq_step, rvolt, ccurrent, excitation_power):
    """
    This function scans over the frequency of the antenna excitation signal starting from freq_min until freq_max in steps of freq_step.
    For each step it reads the trace of the SDA815 spectrum analyzer and calculates the MMD (maximum-minimum-depth), averages it (depending
    on your settings) and writes it into a file.
    """

    #epoch_time = int(time.time()) # this function saves the current time (as kept by the computer) into epoch_time

    """
    Specifies the filename starting with the date and the names of your individual measurements.
    When you use this function later choose something meaningful for "name" in each individual measurement
    e.g. add the ring voltage, coil current, excitation power, frequency range, ...
    In this way it is easier to analyze the data later.
    """

    #define the filename and create/open datafile
    fname = 'Neumann_Striebel_' + time.strftime("%Y_%m_%d_%H_%M_%S") + "_" + str(rvolt) + "V_" + str(ccurrent) + "A_" + str(freq_min) + "-" + str(freq_max) + "MHz_" + str(excitation_power) + "dBm.csv"
    file = open(os.path.join(path, fname), "w+")
    file_flush_counter = 0  #counts the amount of data points saved into the buffer (the computer's temporary storage space)
    devices.set_ring_voltage(rvolt) #sets the ring voltage to given value
    devices.set_coil_current(ccurrent) #sets the coil current to given value
    devices.excitation_on() #switch on the output of the excitation
    devices.set_excitation_power(excitation_power) #sets the excitation power to given value
    for f in np.arange(freq_min, freq_max, freq_step): #scan the frequencies from freq_min in steps of size freq_step until freq_max
        devices.set_excitation_frequency(f) #set the current excitation frequency to f
        mmr_av = []
        for ii in range(average_num):
            try:
                devices.send_trigger()
            except:
                print("trigger failed")
                try:
                    devices.trigger.clear()
                    time.sleep(0.3)
                    devices.send_trigger()
                except:
                    print("trigger failed double")
                    devices.trigger.clear()
                    devices.fix_arduino_comm()
                    time.sleep(10)
                    devices.send_trigger()
        
            time.sleep(0.4)
            time.sleep((cycle_time+150)/1000) #sleep in seconds, a bit longer than the measurement cycle        
            data = devices.get_analyzer_data_fast() #this function obtains the data currently shown in the DSA 815 - an array containing the vertical coordinates (MMD) of the points in the graph.
            mmr_av.append(np.average(data[0:10]) - min(data[1:])) # calculates the MMD of the data. MMD = depth of deepest dip in graph
            
        mmr = np.average(mmr_av)
        
        #print(str(f) + "," + str(mmr))  # prints the data point we just obtained - excitation signal frequency and the corresponding MMD to the shell.
        file.write(str(f) + "," + str(mmr) + "\n") # saves the data point into the buffer.
		# to save the data point into the file and not only into the buffer, we need to flush the file.
		# We choose to do this every 40 data points (an arbitrary number) and not every one data point
		# in order to make the program run faster.
        if(file_flush_counter >= 10): # we flush the file every 40 data points
            file.flush()  # not only write into buffer also to the file
            file_flush_counter = 0 # reset the buffer
        else: # if we didn't reach 40 yet,
            file_flush_counter += 1 # increase the count by 1
    file.close() # close the file


#============================================
# MEASUREMENT
#============================================

"""
PLACE YOUR ACTUAL MEASUREMENT CODE HERE AND USE THE ABOVE DEFINED FUNCTION AND THE FOLLOWING COMMANDS:

devices.set_coil_current(1.3)
devices.set_ring_voltage(rvolt)
devices.set_excitation_power(-12)
scanFreq(freq_min,freq_max,freq_step, ring_voltage, ccurent)
"""


excitation_powers = [-5,0,5,10]
coil_currents = [1.1, 1.15, 1.2, 1.25, 1.3]
ring_voltages = [20,25,30,35,40,45]


freq_sequences = [(1,10), (30,80), (300,500)]

freq_step = 0.1

# frequency sweep over 3 excitation powers
print('frequency sweep over excitation power (1/4)')
for ep in excitation_powers:
    for (freq_min, freq_max) in freq_sequences:
        scanFreq(freq_min, freq_max, freq_step, rvolt=40, ccurrent=1.3, excitation_power=ep)


# voltage sweep
print('frequency sweep over ring voltage (2/4)')
for rv in ring_voltages:
    for (freq_min, freq_max) in freq_sequences:
        scanFreq(freq_min, freq_max, freq_step, rvolt=rv, ccurrent=1.3, excitation_power=10)

# current sweep
print('frequency sweep over coil currents (3/4)')
for cc in coil_currents:
    for (freq_min, freq_max) in freq_sequences:
        scanFreq(freq_min, freq_max, freq_step, rvolt=40, ccurrent=cc, excitation_power=10)

print('complete frequence spectrum (4/4)')
scanFreq(1, 500, 0.1, rvolt=39.5, ccurrent=1.3, excitation_power=10)


del devices.hf_gen
del devices.analyzer

print('finished')
#Reset coil current to let the coil cool down
devices.set_coil_current(0.05)
