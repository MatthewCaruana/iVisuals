import tkinter as tk
from tkinter import ttk
import json

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import time

class iRacingOverlay(tk.Tk):
    def __init__(self, queue, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.title("iRacing Overlay")
        self.geometry("0x0")
        self.attributes("-alpha", 0)  # Set transparency
        self.attributes("-topmost", True)  # Keep the window on top
        self.overrideredirect(True)  # Remove window decorations

        self.editMode = False

        self.after(0, self.readQueue)

        self.setBaseWindowBindings(self)
        self.createInputUIElements()
        self.createStandingsUIElements()

    def createInputUIElements(self):
        self.inputChart_xaxis = list(range(100))
        self.throttleInputHistory = [0] * 100
        self.brakeInputHistory = [0] * 100
        self.clutchInputHistory = [0] * 100

        self.inputWindow = tk.Toplevel()
        self.inputWindow.geometry("220x100")
        self.inputWindow.attributes("-alpha", 0.9)  # Set transparency
        self.inputWindow.attributes("-topmost", True)  # Keep the window on top
        self.inputWindow.overrideredirect(True)  # Remove window decorations

        # Create a frame for the input history
        self.inputFrame = tk.Frame(self.inputWindow, bg='#404040')
        self.inputFrame.grid(padx=0, pady=0, sticky='nsew')

        # Create Gear label
        self.gearLabel = tk.Label(self.inputFrame, text="N", fg='white', bg='#404040', font=('Calibri', 18, 'bold'))
        self.gearLabel.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        # Create Speed label
        self.speedLabel = tk.Label(self.inputFrame, text="0", fg='white', bg='#404040', font=('Calibri', 10))
        self.speedLabel.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        self.inputChart = Figure(figsize=(2, 1), dpi=100, frameon=False, constrained_layout=True)
        self.updateInputChart()
        self.inputChartCanvas = FigureCanvasTkAgg(self.inputChart, master=self.inputFrame)
        self.inputChartCanvas.draw()
        self.inputChartCanvas.get_tk_widget().grid(column=1, row=0, rowspan=2, padx=0, pady=0, sticky='nsew')
        self.inputChartCanvas._tkcanvas.config(bg='#404040')

        self.setBaseWindowBindings(self.inputWindow)

    def createStandingsUIElements(self):
        self.currentBestLaps = []

        self.standingsWindow = tk.Toplevel()
        self.standingsWindow.geometry("240x500")
        self.standingsWindow.attributes("-alpha", 0.9)
        self.standingsWindow.attributes("-topmost", True)  # Keep the window on top
        self.standingsWindow.overrideredirect(True)  # Remove window decorations

        self.standingsFrame = tk.Frame(self.standingsWindow, bg='#404040')
        self.standingsFrame.grid(padx=0, pady=0, sticky='nsew')

        self.stangingsTable = ttk.Treeview(self.standingsFrame)

        self.setBaseWindowBindings(self.standingsWindow)

    def updateInputChart(self):
        self.inputChartPlot = self.inputChart.add_subplot(111)
        self.inputChartPlot.set_facecolor('#404040')
        self.inputChartPlot.axes.get_xaxis().set_visible(False)
        self.inputChartPlot.axes.get_yaxis().set_visible(False)
        self.inputChartPlot.axes.set_xlim(0, 100)
        self.inputChartPlot.axes.set_ylim(0, 100)
        for spine in self.inputChartPlot.spines.values():
            spine.set_visible(False)
        self.inputChartPlot.axhline(y=20, color='grey', linewidth=0.5)
        self.inputChartPlot.axhline(y=40, color='grey', linewidth=0.5)
        self.inputChartPlot.axhline(y=60, color='grey', linewidth=0.5)
        self.inputChartPlot.axhline(y=80, color='grey', linewidth=0.5)
        self.inputChartPlot.plot(self.inputChart_xaxis, self.throttleInputHistory, color='green', linewidth=1.5)
        self.inputChartPlot.plot(self.inputChart_xaxis, self.brakeInputHistory, color='red', linewidth=1.5)
        self.inputChartPlot.plot(self.inputChart_xaxis, self.clutchInputHistory, color='blue', linewidth=1.5)

    def readQueue(self):
        if not self.queue.empty():
            message = self.queue.get()
            json_acceptable_string = message.replace("'", "\"")

            converted_message = json.loads(json_acceptable_string)
            self.updateOverlay(converted_message)
        self.after(20, self.readQueue)

    def updateOverlay(self, data):
        # Update speed label
        self.speedLabel.config(text=f"{data['speed']}")
        # Update gear label
        self.gearLabel.config(text=data['gear'])

        # Update throttle input history
        self.throttleInputHistory.pop(0)
        self.throttleInputHistory.append(data['throttle'])

        # Update brake input history
        self.brakeInputHistory.pop(0)
        self.brakeInputHistory.append(data['brake'])

        # Update clutch input history
        self.clutchInputHistory.pop(0)
        self.clutchInputHistory.append(data['clutch'])

        # Update the input chart
        self.inputChart.clear()
        self.updateInputChart()
        self.inputChartCanvas.draw()

    def setBaseWindowBindings(self, window):
        def on_key_press(event):
            if(event.keysym == 'F7'):
                self.editMode = not self.editMode
                print("Setting edit mode to", self.editMode)

        def on_mouse_click(event):
            if self.editMode:
                # Handle mouse click events
                window.offset_x =window.winfo_pointerx() - window.winfo_rootx()
                window.offset_y = window.winfo_pointery() - window.winfo_rooty()

        def on_mouse_drag(event):
            if self.editMode:
                if None not in (window.offset_x, window.offset_y):
                    x = window.winfo_pointerx() - window.offset_x
                    y = window.winfo_pointery() - window.offset_y
                    window.geometry(f"+{x}+{y}")

        def on_mouse_release(event):
            if self.editMode:
                # Reset the offset when the mouse is released
                window.offset_x = None
                window.offset_y = None

        window.bind("<KeyPress>", on_key_press)
        window.bind("<Button-1>", on_mouse_click)
        window.bind("<B1-Motion>", on_mouse_drag)
        window.bind("<ButtonRelease-1>", on_mouse_release)
        window.bind("<Escape>", lambda e: window.destroy())  # Escape key to close the overlay

    def run(self):
        try:
            self.mainloop()
        except KeyboardInterrupt:
            self.destroy()
            print("Overlay closed.")