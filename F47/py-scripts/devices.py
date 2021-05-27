import pyvisa as visa
import time
import serial

import numpy as np

rm = visa.ResourceManager('@ni')
print(rm.list_resources())

#func_gen    = rm.open_resource('USB0::0x0957::0x2C07::MY52803890::INSTR')  # Small function generator for ring voltage ramp
hameg       = serial.Serial("COM6", 9600, timeout = 1)  # 4-channel power supply for filament current
srs         = serial.Serial("COM4",baudrate=115200,timeout=1) # New main supply for electrodes; tuning ratio with voltage divider
hf_gen      = rm.open_resource('GPIB0::7::INSTR')       # Big HF generator for freq scans
analyzer    = rm.open_resource('USB0::0x1AB1::0x0960::DSA8A154402671::INSTR')
trigger     = serial.Serial("COM5", 115200, timeout = 1)          # Arduino trigger generator

time.sleep(1) # wait for the serial connection to the trigger box

# SRS205 - controls ring electrode and correction electrodes.
# initialize in +/- 100V range, 15V setting and output on.
#srs.write(b"*RST\r\n");
#srs.write(b"RNGE2\r\n");
#srs.write(b"VOLT15\r\n");
#srs.write(b"SOUTon\r\n");

def set_ring_voltage(voltage):
    srs.write(("VOLT" + str(voltage) + "\r\n").encode());
    srs.write(("SOUTon\r\n").encode());

def set_ring_sweep(scan_start, scan_stop, scan_time): #defines the ring voltage sweep for detection; fastest time is 100ms for the full range
    srs.write(("VOLT" + str(scan_start) + "\r\n").encode());
    srs.write(("SOUTon\r\n").encode());
    srs.write(("SCAR RANGE100\r\n").encode())
    srs.write(("SCAB" + str(scan_start) + "\r\n").encode());
    srs.write(("SCAE" + str(scan_stop) + "\r\n").encode());
    srs.write(("SCAT" + str(scan_time) + "\r\n").encode());
    srs.write(("SCAA ARMED\r\n").encode());

def srs_rearm_device(): # Arms the device for the next identical sweep
    srs.write(("SCAA ARMED\r\n").encode());
    
# Hameg

def set_coil_current(current):
    hameg.write("INST OUT3\r\n".encode())
    str_value = "{0:.3f}".format(float(current))
    cmd = "CURR " +str_value+ "\r\n"
    hameg.write(cmd.encode())
    hameg.write("INST OUT4\r\n".encode())
    hameg.write(cmd.encode())


# hf_gen: The high frequency signal generator for the electron excitation
def set_excitation_frequency(frequency):
    hf_gen.write("FR "+str(frequency)+" MZ")     # set Frequency
    time.sleep(0.05)                                # wait for generator to set the new freqency

def set_excitation_power(power):
    hf_gen.write("AP "+str(power)+" DM")         # set Amplitude
    time.sleep(0.1)

def excitation_on():
    hf_gen.write("R3")                           # output on
    time.sleep(0.1)

def excitation_off():
    hf_gen.write("R2")                           # output off
    time.sleep(0.1)

# RIGOL spectrum analyzer for axial excitation and detection
def set_analyzer_to_zero_span(center_freq="56.5MHz", ref_level = "-12.0", 
                              PDIV_scale = "1.0", sweep_time="100ms", attenuation="7"):
    
    analyzer.write(":SYST:PRES:TYPe FACT")
    analyzer.write(":SYST:PRES")

    #analyzer.write(":SENSe:FREQuency:CENTer 57.4MHz")
    analyzer.write(":SENSe:FREQuency:CENTer "+center_freq)
    analyzer.write(":SENSe:FREQuency:SPAN 0")

    # the sweep time 100 ms is usefull to make sure you see everything
    # if you want to "zoom" in you can reduce this to e.g. 25 ms and
    # the resulting dip may be more stable in amplitude because you
    # get 4 times as many points in the time span you are intereseted in. 
    #analyzer.write(":SENSe:SWEep:TIME 100ms")
    analyzer.write(":SENSe:SWEep:TIME "+sweep_time)
    analyzer.write(":SENSe:SWEep:TIME:AUTO:RULes NORMal")

    # trigger settings, non negatiable
    analyzer.write(":TRIGger:SEQuence:SOURce EXTernal")
    analyzer.write(":TRIGger:SEQuence:EXTernal:SLOPe POSitive")

    # these are the best settings for sampling
    #analyzer.write(":SENSe:BANDwidth:RESolution 1000000") # why?
    #analyzer.write(":SENSe:BANDwidth:VIDeo 1000000")      # why?
    analyzer.write(":SENSe:DETector:FUNCtion SAMPle")   # no averaging

    #analyzer.write(":SENSe:POWer:RF:ATTenuation 7")
    analyzer.write(":SENSe:POWer:RF:ATTenuation "+attenuation)
    analyzer.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude -20dBm")

    # adjusting for the window on the spectrum analyzer
    #analyzer.write(":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel -8.0") 
    analyzer.write(":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel "+ref_level) 
    #analyzer.write(":DISPlay:WINdow:TRACe:Y:SCALe:PDIVision 0.5") 
    analyzer.write(":DISPlay:WINdow:TRACe:Y:SCALe:PDIVision "+PDIV_scale)

    analyzer.write(":DISPlay:WINdow:TRACe:Y:SCALe:SPACing LOG")  # Careful: No unit defaults to Volt now!!!
    analyzer.write("OUTPut ON")

def set_analyzer_ref_level(ref_level):
    analyzer.write(":DISPlay:WINdow:TRACe:Y:SCALe:RLEVel "+str(ref_level))

def set_analyzer_ydivision(division):
    analyzer.write(":DISPlay:WINdow:TRACe:Y:SCALe:PDIVision "+str(division))

def set_analyzer_sweep_time(sweep_time):
    analyzer.write(":SENSe:SWEep:TIME "+str(sweep_time))

def set_analyzer_center_frequency(frequency):
     analyzer.write(":SENSe:FREQuency:CENTer "+str(frequency))
     
def get_analyzer_data_fast():
    for t in range(0, 10):
        try:
            data_str = analyzer.query(":TRACe:DATA? TRACE1")    #get data from spectrum analyzer
            hp = data_str.find("-",0,100)                       # cut header away
            data_str = data_str[hp:]                            # cut header away
            data = [float(s) for s in data_str.split(',')]      # convert into float numbers
            break;

        except:
            print("Error at "+str(t))
            time.sleep(4)
            pass

    return data

def get_analyzer_data(average_number):

    if(average_number < 1):
        average_number = 1

    for t in range(0, 10):
        try:
            #Take Data
            analyzer.write(":TRACe1:AVERage:TYPE VIDeo")
            analyzer.write(":TRACe:AVERage:COUNt "+str(average_number))

            analyzer.write(":TRACe:AVERage:CLEar")
            #analyzer.write(":TRACe:AVERage:RESet")

            avg_count = 0.0
            while avg_count < average_number:
                avg_count = int(analyzer.query(":TRACe:AVERage:COUNt:CURRent?"))
                time.sleep(1.5) # DSA 815 doesn't like to many request per time

        
            analyzer.write(":TRACe1:MODE VIEW")
            break;

        except:
            print("Error at set/read average")
            time.sleep(4)
            pass
     
    for t in range(0, 10):
        try:
            data_str = analyzer.query(":TRACe:DATA? TRACE1")    #get data from spectrum analyzer
            hp = data_str.find("-",0,100)                       # cut header away
            data_str = data_str[hp:]                            # cut header away
            data = [float(s) for s in data_str.split(',')]      # convert into float numbers
            break;

        except:
            print("Error at "+str(t))
            time.sleep(4)
            pass

    return data

#Axial Detection: Resonator Excited by SpectrumAnalyzer
def set_resonator_power(power):
    analyzer.write(":SOURce:POWer:LEVel:IMMediate:AMPLitude "+str(power))
    analyzer.write("OUTPut ON")

def set_resonator_on(power):
    analyzer.write("OUTPut ON")

def set_resonator_off(power):
    analyzer.write("OUTPut OFF")

#trigger
    
def get_trigger_times():
    trigger.clear() # Why? 
    trigger.write("times?")
    data = trigger.read()
    values = [float(s) for s in data[:-2].split(',')]
    return values

"""
def set_trigger_num(num):
    trigger.write(("trig_num "+str(num)+"\r\n").encode())
    trigger.write(("trig\n"+"\r\n").encode()) 
"""
def send_trigger():
    trigger.write(("trig"+"\r\n").encode()) 

def set_trigger_times(load, wait1, excite, wait2, detect, wait3, rigol):
    if load + wait1 + excite + wait2 + detect > 1500:
        print("Warning: Trigger period larger than 1.5s.")
        print("Serial communication more likely to fail now.")
    cmd = "times "+str(load)+" "+str(wait1)+" "+str(excite)+" "
    cmd += str(wait2)+" "+str(detect)+" "+str(wait3)+" "+str(rigol)+"\r\n"
    time.sleep(0.1)
    trigger.write( cmd.encode() )
    time.sleep(0.1)

def set_time(ident='load', val=200):
    ident = ident+' '
    val = str(val)
    print('send', ident+val+"\r\n", end='')
    time.sleep(0.1)
    trigger.write((ident+val+"\r\n").encode())
    time.sleep(0.1)

def fix_arduino_comm():
    trigger.close()
    time.sleep(2)
    trigger = rm.open_resource('ASRL5::INSTR')
