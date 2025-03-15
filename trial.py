import tkinter as tk
from PIL import Image, ImageTk, ImageSequence

def update_frame(label, frames, frame_index):
    # Update the label with the next frame
    frame = frames[frame_index]
    tk_image = ImageTk.PhotoImage(frame)
    label.config(image=tk_image)
    label.image = tk_image  # Keep a reference to avoid garbage collection

    # Schedule the next frame
    frame_index = (frame_index + 1) % len(frames)
    root.after(20, update_frame, label, frames, frame_index)  # Adjust frame delay here

# Initialize Tkinter
root = tk.Tk()
root.title("GIF in Tkinter")

# Path to your GIF file
gif_path = "images\Loading.gif"

# Load the GIF
gif = Image.open(gif_path)
frames = [frame.copy() for frame in ImageSequence.Iterator(gif)]

# Create a label to display the GIF
label = tk.Label(root)
label.pack()

# Start the animation
update_frame(label, frames, 0)

root.mainloop()