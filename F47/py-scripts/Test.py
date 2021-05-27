import devices
import time

## define and set times for measurement cycle
# The times are relative times to the pulse before and are listed here
# in the order the pulses will be send.
load = 500
wait1 = 5
excite = 10
wait2 = 5
rigol = 5   # the Rigol spectrum analyzer has a 30 ms trigger delay
wait3 = 30 
detect = 50


# the rigol time starts after wait2, but the rigol trigger
# can be shifted independently to later times after the detection (RAMP) 
# with wait3, thats why the total cycle time is defined like this:
cycle_time = load + wait1 + excite + wait2 + rigol + wait3 + detect
     
devices.set_time('load', load)
devices.set_time('wait1', wait1)
devices.set_time('excite', excite)
devices.set_time('wait2', wait2)
devices.set_time('rigol', rigol),

devices.set_time('wait3', wait3)
devices.set_time('detect', detect)

## set magnetic field
devices.set_coil_current(1.3) # maximum current: 1.3 A


## set ring voltage
# The sweeping will be done by switching to 15 V with a capacitance
# connected to use the discharge of the C as a method of ramping.
# The ramp is not linear and you can check the voltage value at
# data taking time using an osci probe connected to Vring in the
# detection system box.
# This voltage here defines the ring voltage before the ramp, so
# also during excitation. But reducing it, will also change the
# voltage and axial frequency your ion has during detection.
devices.set_ring_voltage(39.5)


## Initialize the RIGOL spectrum analyzer for measurement
# Trigger and some other settings are hard code in the routine, but
# some values you might want to adjust during a scan can be given as
# an argument. Check the definition of this function for more information.
#devices.set_analyzer_to_zero_span()
devices.set_analyzer_to_zero_span(center_freq="57.3MHz", ref_level = "-15.5", 
                              PDIV_scale = "5.0", sweep_time="250ms")

# just give the RIGOL some time to understand its commands.
time.sleep(1)

# continuously load, excite, and measure:


while True: 
     devices.send_trigger()
     time.sleep((cycle_time+200)/1000)
     time.sleep(0.5)
     print('.', end='')
