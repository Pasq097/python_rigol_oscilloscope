import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import visa

rm = pyvisa.ResourceManager()
rm.list_resources()
inst = rm.open_resource('USB0::0x1AB1::0x04CE::DS1ZA221503969::INSTR')
print(inst.query("*IDN?"))

# Turn on display for channel 1 and channel 2
inst.write(':CHAN1:DISP ON')
inst.write(':CHAN2:DISP ON')

# Get waveform data for channel 1
inst.write(':WAVeform:SOURce CHAN1')
inst.write(':WAVeform:FORMAT ASCII')
inst.write(':WAVeform:POINTS:MODE RAW')
inst.write(':WAVeform:DATA?')
waveform_data1 = inst.read_raw()
waveform_values1 = [float(val) for val in waveform_data1.decode()[11:].split(',')]

# Get waveform data for channel 2
inst.write(':WAVeform:SOURce CHAN2')
inst.write(':WAVeform:FORMAT ASCII')
inst.write(':WAVeform:POINTS:MODE RAW')
inst.write(':WAVeform:DATA?')
waveform_data2 = inst.read_raw()
waveform_values2 = [float(val) for val in waveform_data2.decode()[11:].split(',')]


# Plot the waveforms
time = np.linspace(0, len(waveform_values1)-1, len(waveform_values1))*float(inst.query(':WAVeform:XINCrement?'))
fig, ax = plt.subplots()
ax.plot(time, waveform_values1, label='Channel 1')
ax.plot(time, waveform_values2, label='Channel 2')
ax.legend()
ax.set_xlabel('Time (s)')
ax.set_ylabel('Voltage (V)')

pp1 = max(waveform_values1) - min(waveform_values1)
pp2 = max(waveform_values2) - min(waveform_values2)
gain = 20*np.log10(pp2/pp1)
print("Gain in dB:", gain)

plt.show()
