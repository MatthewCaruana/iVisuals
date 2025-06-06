import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# Create main window
root = tk.Tk()
root.geometry("400x300")
root.configure(bg="white")  # Optional: match background

# Create a frame to hold the matplotlib figure (optional, for layout)
frame = tk.Frame(root, bg="white")
frame.pack(fill=tk.BOTH, expand=True)

# Create a matplotlib figure and plot something
fig, ax = plt.subplots(figsize=(4, 3), dpi=100)

# Remove paddings and borders
fig.patch.set_visible(False)  # Hide figure background
fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

# (Optional) Hide axes spines and ticks for a truly borderless look
for spine in ax.spines.values():
    spine.set_visible(False)
ax.set_xticks([])
ax.set_yticks([])

# Plot your data
ax.plot([0, 1, 2, 3], [0, 1, 0, 1])

# Embed the matplotlib figure in Tkinter
canvas = FigureCanvasTkAgg(fig, master=frame)
canvas.draw()
widget = canvas.get_tk_widget()
widget.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)
canvas._tkcanvas.config(bg='black')  # Optional: match background

root.mainloop()