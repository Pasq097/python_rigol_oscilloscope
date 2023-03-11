import tkinter as tk
from tkinter import ttk
import pyvisa
import numpy as np
import matplotlib.pyplot as plt
import visa
from scipy.signal import savgol_filter
class Application(ttk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.master.title("Measurement GUI")
        self.create_widgets()
        self.freq_list = []
        self.gain_list = []

    def create_widgets(self):
        # Create a frame for the plot
        self.plot_frame = ttk.Frame(self.master)
        self.plot_frame.grid(row=0, column=0, sticky="nsew")

        # Create a button to trigger the measurement
        self.measure_button = ttk.Button(self.master, text="Measure", command=self.measure)
        self.measure_button.grid(row=1, column=0, sticky="w")

        # Create a button to plot the gain vs frequency data
        self.plot_button = ttk.Button(self.master, text="Plot", command=self.plot_data)
        self.plot_button.grid(row=3, column=0, sticky="w")

        # Create an input box for frequency
        self.freq_label = ttk.Label(self.master, text="Frequency:")
        self.freq_label.grid(row=2, column=0, sticky="w")
        self.freq_entry = ttk.Entry(self.master)
        self.freq_entry.grid(row=2, column=0, sticky="e")

        # Create a frame for the gain list
        self.gain_frame = ttk.Frame(self.master, borderwidth=2, relief="ridge")
        self.gain_frame.grid(row=0, column=1, rowspan=3, sticky="nsew")

        # Create a label for the gain list
        self.gain_label = ttk.Label(self.gain_frame, text="Frequency   Gain", font=("TkDefaultFont", 10, "bold"))
        self.gain_label.pack(side="top", fill="x")

        # Create a scrollbar for the gain list
        self.gain_scrollbar = ttk.Scrollbar(self.gain_frame)
        self.gain_scrollbar.pack(side="right", fill="y")

        # Create a listbox for the gain list
        self.gain_listbox = tk.Listbox(self.gain_frame, yscrollcommand=self.gain_scrollbar.set)
        self.gain_listbox.pack(side="left", fill="both", expand=True)
        self.gain_scrollbar.config(command=self.gain_listbox.yview)

    def measure(self):

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
        time = np.linspace(0, len(waveform_values1) - 1, len(waveform_values1)) * float(
            inst.query(':WAVeform:XINCrement?'))
        fig, ax = plt.subplots()
        ax.plot(time, waveform_values1, label='Channel 1')
        ax.plot(time, waveform_values2, label='Channel 2')
        ax.legend()
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Voltage (V)')

        pp1 = max(waveform_values1) - min(waveform_values1)
        pp2 = max(waveform_values2) - min(waveform_values2)
        gain = 20 * np.log10(pp1 / pp2)
        print("Gain in dB:", gain)
        self.freq_list.append(float(self.freq_entry.get()))
        self.gain_list.append(gain)
        plt.show()

        self.gain_listbox.delete(0, tk.END)
        for freq, gain in zip(self.freq_list, self.gain_list):
            self.gain_listbox.insert(tk.END, f"{freq:.2f} Hz   {gain:.2f} dB")

        pass

    def plot_data(self):
        fig, ax = plt.subplots()
        ax.semilogx(self.freq_list, self.gain_list, marker='o', label='Original Data')

        # Apply the savgol_filter to the gain_list
        filtered_gain_list = savgol_filter(self.gain_list, 10, 3)
        ax.semilogx(self.freq_list, filtered_gain_list, label='Filtered Data')

        ax.set_xlabel('Frequency (Hz)')
        ax.set_ylabel('Gain (dB)')
        ax.legend()
        plt.show()



root = tk.Tk()
app = Application(master=root)
app.mainloop()
