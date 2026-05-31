import tkinter as tk
from tkinter import messagebox
from db import conn, cur
import os

# ---------------- WINDOW ---------------- #
TITLE = "Vehicle Booking"
BG_COLOR = "#D6EAF8"

root = tk.Tk()
root.title(TITLE)
root.state('zoomed')
root.configure(bg=BG_COLOR)

# --- LOAD LOGO ---
try:
    current_path = os.path.dirname(os.path.abspath(__file__))
    logo_path = os.path.join(current_path, "logo.png")
    raw_logo = tk.PhotoImage(file=logo_path)
    logo_image = raw_logo.subsample(4, 4) 
    root.iconphoto(False, raw_logo) 
except tk.TclError as e:
    print(f"⚠️ Warning: Image failed to load: {e}")
    logo_image = None

# ---------------- VARIABLES ---------------- #
username_var = tk.StringVar()
password_var = tk.StringVar()

# ---------------- FUNCTIONS ---------------- #
def login_user():
    username = username_var.get()
    password = password_var.get()

    # Database check
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cur.fetchone()

    if user:  # (Or `if bcrypt.checkpw(...)` if you implemented the security fix)
        messagebox.showinfo("Success", "Login Successful")
        root.destroy()  # Close the login window
        
        # Redirect to Dashboard instead of Booking
        try:
            import dashboard
            dashboard.open_dashboard(username)  # Passes the username to the dashboard
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load dashboard: {e}")

def open_register():
    root.destroy()
    try:
        import register
        register.open_register_page() 
    except:
        messagebox.showerror("Error", "Register page (register.py) not found!")

def toggle_password():
    password_entry.config(show="" if show_password_var.get() else "*")

# ---------------- UI ELEMENTS ---------------- #
if logo_image:
    tk.Label(root, text="  VEHICLE BOOKING", image=logo_image, compound="left", 
             font=("Arial", 35, "bold"), bg=BG_COLOR, fg="darkblue").pack(pady=(60, 10))
else:
    tk.Label(root, text="VEHICLE BOOKING", font=("Arial", 35, "bold"), bg=BG_COLOR, fg="darkblue").pack(pady=(60, 10))

tk.Label(root, text=" LOGIN ", font=("Arial", 25, "bold"), fg="#333333", bg=BG_COLOR).pack(pady=(0, 40))

tk.Label(root, text="Username", font=("Arial", 16), bg=BG_COLOR).pack()
tk.Entry(root, textvariable=username_var, font=("Arial", 16), width=30).pack(pady=10)

tk.Label(root, text="Password", font=("Arial", 16), bg=BG_COLOR).pack()
password_entry = tk.Entry(root, textvariable=password_var, show="*", font=("Arial", 16), width=30)
password_entry.pack(pady=10)

show_password_var = tk.IntVar()
tk.Checkbutton(root, text="Show Password", variable=show_password_var, command=toggle_password, 
               font=("Arial", 13), bg=BG_COLOR).pack()

btn_frame = tk.Frame(root, bg=BG_COLOR)
btn_frame.pack(pady=30)

tk.Button(btn_frame, text="LOGIN", font=("Arial", 16, "bold"), width=20, bg="blue", 
          fg="white", command=login_user).pack(pady=10, ipady=8)

tk.Button(btn_frame, text="REGISTER", font=("Arial", 16, "bold"), width=20, bg="green", 
          fg="white", command=open_register).pack(pady=10, ipady=8)

# Start the app
root.mainloop()