import tkinter as tk
import json

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import time

class iRacingOverlay(tk.Tk):
    def __init__(self, queue, settings, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.title("iRacing Overlay")
        self.geometry("240x100")
        self.attributes("-alpha", 0.8)  # Set transparency
        self.configure(bg='black')
        self.focus_force()
        self.attributes("-topmost", True)  # Keep the window on top
        self.overrideredirect(True)  # Remove window decorations

        self.inputChart_xaxis = list(range(100))
        self.throttleInputHistory = [0] * 100
        self.brakeInputHistory = [0] * 100
        self.clutchInputHistory = [0] * 100

        self.editMode = False

        self.after(0, self.readQueue)

        self.setBindings()
        self.createUIElements()
        
    def setBindings(self):
        self.bind("<KeyPress>", self.on_key_press) 
        self.bind("<Button-1>", self.on_mouse_click)  # Left mouse button click
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.bind("<Escape>", lambda e: self.destroy())  # Escape key to close the overlay

    def createUIElements(self):
        # Create a frame for the input history
        self.inputFrame = tk.Frame(self, bg='#404040')
        self.inputFrame.grid(padx=0, pady=0, sticky='nsew')

        # Create Gear label
        self.gearLabel = tk.Label(self.inputFrame, text="N", fg='white', bg='#404040', font=('Calibri', 18, 'bold'))
        self.gearLabel.grid(row=0, column=0, padx=10, pady=10, sticky='nsew')

        # Create Speed label
        self.speedLabel = tk.Label(self.inputFrame, text="0", fg='white', bg='#404040', font=('Calibri', 10))
        self.speedLabel.grid(row=1, column=0, padx=10, pady=10, sticky='nsew')

        self.inputChart = Figure(figsize=(2, 1), dpi=100, frameon=False, tight_layout=True)
        self.updateInputChart()
        self.inputChartCanvas = FigureCanvasTkAgg(self.inputChart, master=self.inputFrame)
        self.inputChartCanvas.draw()
        self.inputChartCanvas.get_tk_widget().grid(column=1, row=0, rowspan=2, padx=1, pady=1, sticky='nsew')
        self.inputChartCanvas._tkcanvas.config(bg='#404040')


    def updateInputChart(self):
        self.inputChartPlot = self.inputChart.add_subplot(111)
        self.inputChartPlot.set_facecolor('#404040')
        self.inputChartPlot.axes.get_xaxis().set_visible(False)
        self.inputChartPlot.axes.get_yaxis().set_visible(False)
        self.inputChartPlot.axes.set_xlim(0, 100)
        self.inputChartPlot.axes.set_ylim(0, 100)
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


    def run(self):
        try:
            self.mainloop()
        except KeyboardInterrupt:
            self.destroy()
            print("Overlay closed.")

    def on_key_press(self, event):
        if(event.keysym == 'F7'):
            self.editMode = not self.editMode
            print("Setting edit mode to", self.editMode)


    def on_mouse_click(self, event):
        if self.editMode:
            # Handle mouse click events
            self.offset_x =self.winfo_pointerx() - self.winfo_rootx()
            self.offset_y = self.winfo_pointery() - self.winfo_rooty()

    def on_mouse_drag(self, event):
        if self.editMode:
            if None not in (self.offset_x, self.offset_y):
                x = self.winfo_pointerx() - self.offset_x
                y = self.winfo_pointery() - self.offset_y
                self.geometry(f"+{x}+{y}")

    def on_mouse_release(self, event):
        if self.editMode:
            # Reset the offset when the mouse is released
            self.offset_x = None
            self.offset_y = None