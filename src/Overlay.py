import tkinter as tk
from tkinter import ttk
import json

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from SettingsManager import SettingsManager

import time

class iRacingOverlay(tk.Tk):
    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.title("iRacing Overlay")
        self.geometry("0x0")
        self.attributes("-alpha", 0)  # Set transparency
        self.attributes("-topmost", True)  # Keep the window on top
        self.overrideredirect(True)  # Remove window decorations

        self.editMode = False

        self.after(0, self.readQueue)
        self.settings = SettingsManager()

        self.setBaseWindowBindings(self)
        self.createInputUIElements()
        self.createStandingsUIElements()


    def createInputUIElements(self):
        self.inputChart_xaxis = list(range(100))
        self.throttleInputHistory = [0] * 100
        self.brakeInputHistory = [0] * 100
        self.clutchInputHistory = [0] * 100

        self.inputWindow = tk.Toplevel()

        geometry_offset = self.settings.get_setting("InputUI", "geometry_xy") + "+" + str(self.settings.get_setting("InputUI", "offset_x")) + "+" + str(self.settings.get_setting("InputUI", "offset_y"))

        self.inputWindow.geometry(geometry_offset)
        self.inputWindow.attributes("-alpha", self.settings.get_setting("InputUI", "alpha"))  # Set transparency
        self.inputWindow.attributes("-topmost", self.settings.get_setting("InputUI", "topmost"))  # Keep the window on top
        self.inputWindow.overrideredirect(True)  # Remove window decorations

        # Create a frame for the input history
        self.inputFrame = tk.Frame(self.inputWindow, bg=self.settings.get_setting("InputUI", "background_color"))
        self.inputFrame.grid(padx=0, pady=0, sticky='nsew')

        # Create Gear label
        self.gearLabel = tk.Label(self.inputFrame, text="N", fg='white', bg=self.settings.get_setting("InputUI", "background_color"), font=('Calibri', 18, 'bold'))
        self.gearLabel.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        # Create Speed label
        self.speedLabel = tk.Label(self.inputFrame, text="0", fg='white', bg=self.settings.get_setting("InputUI", "background_color"), font=('Calibri', 10))
        self.speedLabel.grid(row=1, column=0, padx=5, pady=5, sticky='nsew')

        self.inputChart = Figure(figsize=(2, 1), dpi=100, frameon=False, constrained_layout=True)
        self.updateInputChart()
        self.inputChartCanvas = FigureCanvasTkAgg(self.inputChart, master=self.inputFrame)
        self.inputChartCanvas.draw()
        self.inputChartCanvas.get_tk_widget().grid(column=1, row=0, rowspan=2, padx=0, pady=0, sticky='nsew')
        self.inputChartCanvas._tkcanvas.config(bg=self.settings.get_setting("InputUI", "background_color"))

        self.setBaseWindowBindings(self.inputWindow)

    def createStandingsUIElements(self):
        self.currentBestLaps = []

        geometry_offset = self.settings.get_setting("StandingsUI", "geometry_xy") + "+" + str(self.settings.get_setting("StandingsUI", "offset_x")) + "+" + str(self.settings.get_setting("StandingsUI", "offset_y"))

        self.standingsWindow = tk.Toplevel()
        self.standingsWindow.geometry(geometry_offset)
        self.standingsWindow.attributes("-alpha", self.settings.get_setting("StandingsUI", "alpha"))
        self.standingsWindow.attributes("-topmost", self.settings.get_setting("StandingsUI", "topmost"))  # Keep the window on top
        self.standingsWindow.overrideredirect(True)  # Remove window decorations

        self.standingsFrame = tk.Frame(self.standingsWindow, bg=self.settings.get_setting("StandingsUI", "background_color"))
        self.standingsFrame.grid(padx=0, pady=0, sticky='nsew')

        self.stangingsTable = ttk.Treeview(self.standingsFrame)

        self.setBaseWindowBindings(self.standingsWindow)
        self.updateStandingsUI()

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

    def updateStandingsUI(self):
        self.stangingsTable.destroy()
        self.stangingsTable = ttk.Treeview(self.standingsFrame, columns=('Position', 'Driver', 'Car', 'Laps', 'Best Lap'), show='headings')
        self.stangingsTable.heading('Position', text='Pos')
        self.stangingsTable.heading('Driver', text='Driver')
        self.stangingsTable.heading('Car', text='Car')
        self.stangingsTable.heading('Laps', text='Laps')
        self.stangingsTable.heading('Best Lap', text='Best Lap')

        # Add the table to the frame
        self.stangingsTable.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')

        # Configure the columns
        for col in self.stangingsTable['columns']:
            self.stangingsTable.column(col, anchor='center')

        # Add a scrollbar
        scrollbar = ttk.Scrollbar(self.standingsFrame, orient="vertical", command=self.stangingsTable.yview)
        scrollbar.grid(row=0, column=1, sticky='ns')
        self.stangingsTable.configure(yscrollcommand=scrollbar.set)

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

    def updateUILocationSettings(self):
        self.settings.update_settings("InputUI", "offset_x", self.inputWindow.winfo_x())
        self.settings.update_settings("InputUI", "offset_y", self.inputWindow.winfo_y())
        self.settings.update_settings("StandingsUI", "offset_x", self.standingsWindow.winfo_x())
        self.settings.update_settings("StandingsUI", "offset_y", self.standingsWindow.winfo_y())
        print("Updated UI locations in settings.")

    def setBaseWindowBindings(self, window):
        def on_key_press(event):
            if(event.keysym == 'F7'):
                self.editMode = not self.editMode
                print("Setting edit mode to", self.editMode)

                if(not self.editMode):
                    self.updateUILocationSettings()

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