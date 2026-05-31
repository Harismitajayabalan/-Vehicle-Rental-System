import tkinter as tk
from PIL import Image, ImageTk
import os

TITLE = "Vehicle Booking"

root = tk.Tk()
root.title(TITLE)

# Maximize window
root.state('zoomed')
root.update_idletasks() # Ensures screen dimensions are captured accurately

# Get screen size to center items
screen_width = root.winfo_width()
screen_height = root.winfo_height()

# ---------------- THE CANVAS ---------------- #
# We use a canvas instead of a Frame to allow true transparency
canvas = tk.Canvas(root, width=screen_width, height=screen_height, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# ---------------- IMAGE PATHS ---------------- #
current_path = os.path.dirname(os.path.abspath(__file__))

# --- 1. FULL-SCREEN BACKGROUND IMAGE ---
try:
    bg_image_path = os.path.join(current_path, "car.png")
    bg_img = Image.open(bg_image_path)
    
    # Resize to fit the screen
    bg_img = bg_img.resize((screen_width, screen_height))
    bg_photo = ImageTk.PhotoImage(bg_img)

    # Paint the background image onto the canvas
    canvas.create_image(0, 0, image=bg_photo, anchor="nw")
except Exception as e:
    print(f"⚠️ Warning: 'car.png' failed to load. Error: {e}")
    canvas.configure(bg="#D6EAF8") # Fallback color


# --- 2. LOAD TITLE LOGO ---
try:
    current_path = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_path, "logo.png")
    raw_logo = tk.PhotoImage(file=logo_path)
    logo_image = raw_logo.subsample(4, 4) 
    root.iconphoto(False, raw_logo) 
except tk.TclError as e:
    print(f"⚠️ Warning: 'logo.png' failed to load. Error: {e}")
    logo_image = None


# ---------------- FUNCTIONS ---------------- #
def open_login():
    root.destroy()
    import login

def open_register():
    root.destroy()
    import register


# ---------------- UI ELEMENTS ON CANVAS ---------------- #

# Calculate exact center of the screen
center_x = screen_width // 2
center_y = screen_height // 2

# --- TITLE WITH LOGO ---
# Because we are drawing text on a Canvas, there is NO background box!
if logo_image:
    # Draw Logo to the left
    canvas.create_image(center_x - 320, center_y - 120, image=logo_image, anchor="center")
    
    # Draw Text to the right (Changed to White for better contrast against dark car images)
    canvas.create_text(center_x + 30, center_y - 120, 
                       text="VEHICLE RENTAL SYSTEM", 
                       font=("Arial", 33, "bold"), 
                       fill="darkblue") 
else:
    canvas.create_text(center_x, center_y - 120, 
                       text="VEHICLE RENTAL SYSTEM", 
                       font=("Arial", 33, "bold"), 
                       fill="darkblue")

# --- BUTTONS ---
login_button = tk.Button(
    root,
    text="LOGIN",
    font=("Arial", 16, "bold"),
    width=20,
    bg="blue",
    fg="white",
    command=open_login
)
# Embed the button onto the canvas
canvas.create_window(center_x, center_y, window=login_button, height=50)


register_button = tk.Button(
    root,
    text="REGISTER",
    font=("Arial", 16, "bold"),
    width=20,
    bg="green",
    fg="white",
    command=open_register
)
# Embed the second button just below the first
canvas.create_window(center_x, center_y + 80, window=register_button, height=50)

# Start the application
root.mainloop()