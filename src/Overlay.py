import tkinter as tk

import json

class iRacingOverlay(tk.Tk):
    def __init__(self, queue, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue
        self.title("iRacing Overlay")
        self.geometry("800x600")
        self.configure(bg='blue')
        self.focus_force()
        self.attributes("-topmost", True)  # Keep the window on top
        self.overrideredirect(True)  # Remove window decorations

        self.editMode = False

        self.after(17, self.readQueue)

        self.bind("<KeyPress>", self.on_key_press) 
        self.bind("<Button-1>", self.on_mouse_click)  # Left mouse button click
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.bind("<Escape>", lambda e: self.destroy())  # Escape key to close the overlay

        # Add a label to display some information
        self.label = tk.Label(self, text="iRacing Overlay", fg='white', bg='black', font=('Arial', 24))
        self.label.pack(pady=20)

    def readQueue(self):
        print("In readQueue")
        if not self.queue.empty():
            message = self.queue.get()
            print("Received message:", message)
            json_acceptable_string = message.replace("'", "\"")

            converted_message = json.loads(json_acceptable_string)
            self.updateOverlay(converted_message)

            self.label.config(text=f"Speed: {converted_message['speed']} km/h\n")
        self.after(17, self.readQueue)

    def updateOverlay(self, data):
        self.label.config(text=f"Speed: {data['speed']} km/h\n")

    def run(self):
        try:
            self.mainloop()
        except KeyboardInterrupt:
            self.destroy()
            print("Overlay closed.")

    def on_key_press(self, event):
        if(event.keysym == 'F6'):
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