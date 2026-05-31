import tkinter as tk
from tkinter import messagebox
import mysql.connector
import re
import os

# ---------------- MYSQL CONNECTION ---------------- #
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="root",      # Change if needed
    database="vehicle_booking"
)

cur = conn.cursor(buffered=True)

# ---------------- CREATE TABLE ---------------- #
cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) UNIQUE,
    password VARCHAR(100),
    mobile VARCHAR(10),
    email VARCHAR(100)
)
""")
conn.commit()

# ---------------- WINDOW ---------------- #
BG_COLOR = "#D6EAF8"

root = tk.Tk()
root.title("Vehicle Booking")
root.state('zoomed')
root.configure(bg=BG_COLOR)

# --- LOAD LOGO ---
try:
    current_path = os.path.dirname(os.path.abspath(__file__))
    
    # 1. Load the original image
    raw_logo = tk.PhotoImage(file=os.path.join(current_path, "logo.png"))
    
    # 2. Shrink it down to fit the title nicely
    logo_image = raw_logo.subsample(4, 4) 
    
    # Set the small icon in the top left of the window
    root.iconphoto(False, raw_logo) 
except tk.TclError as e:
    print(f"⚠️ Warning: Image failed to load. Error: {e}")
    logo_image = None

# ---------------- FUNCTIONS ---------------- #
def toggle_password():
    if show_password_var.get():
        password_entry.config(show="")
    else:
        password_entry.config(show="*")


def validate():
    username = username_entry.get()
    password = password_entry.get()
    mobile = mobile_entry.get()
    email = email_entry.get()

    # ---------------- VALIDATIONS ---------------- #
    password_pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*[\W_]).{6,}$'
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    mobile_pattern = r'^[0-9]{10}$'

    # Username Empty Check
    if username == "":
        messagebox.showerror("Error", "Username cannot be empty")
        return

    # Password Validation
    if not re.match(password_pattern, password):
        messagebox.showerror(
            "Error",
            "Password must contain:\n"
            "• Minimum 6 characters\n"
            "• 1 uppercase letter\n"
            "• 1 lowercase letter\n"
            "• 1 special character"
        )
        return

    # Mobile Validation
    if not re.match(mobile_pattern, mobile):
        messagebox.showerror("Error", "Mobile number must contain exactly 10 digits")
        return

    # Email Validation
    if not re.match(email_pattern, email):
        messagebox.showerror("Error", "Enter valid Email ID\nExample: abc@gmail.com")
        return

    # ---------------- CHECK USER EXISTS ---------------- #
    check_sql = "SELECT * FROM users WHERE username = %s"
    cur.execute(check_sql, (username,))
    result = cur.fetchone()

    if result:
        messagebox.showerror("Registration Error", "User already registered")
        return

    # ---------------- INSERT DATA ---------------- #
    sql = """
    INSERT INTO users (username, password, mobile, email)
    VALUES (%s, %s, %s, %s)
    """
    values = (username, password, mobile, email)
    cur.execute(sql, values)
    conn.commit()

    # ---------------- SUCCESS MESSAGE ---------------- #
    messagebox.showinfo("Success", "Registration Successful")

    # ---------------- OPEN LOGIN PAGE ---------------- #
    root.destroy()
    import login


# ---------------- UI ELEMENTS ---------------- #

# MAIN TITLE (With Logo)
if logo_image:
    main_title = tk.Label(
        root,
        text="  VEHICLE BOOKING", 
        image=logo_image,
        compound="left",
        font=("Arial", 35, "bold"),
        bg=BG_COLOR,
        fg="darkblue"
    )
else:
    main_title = tk.Label(
        root,
        text="VEHICLE BOOKING", 
        font=("Arial", 35, "bold"),
        bg=BG_COLOR,
        fg="darkblue"
    )
main_title.pack(pady=(40, 10)) 

# SUBTITLE
sub_title = tk.Label(
    root,
    text="REGISTER HERE", 
    font=("Arial", 25, "bold"),
    #fg="#333333",
    bg=BG_COLOR
)
sub_title.pack(pady=(0, 20))


# ---------------- USERNAME ---------------- #
username_label = tk.Label(
    root,
    text="Username",
    font=("Arial", 16),
    bg=BG_COLOR
)
username_label.pack()

username_entry = tk.Entry(
    root,
    font=("Arial", 16),
    width=30
)
username_entry.pack(pady=10)


# ---------------- PASSWORD ---------------- #
password_label = tk.Label(
    root,
    text="Password",
    font=("Arial", 16),
    bg=BG_COLOR
)
password_label.pack()

password_entry = tk.Entry(
    root,
    font=("Arial", 16),
    width=30,
    show="*"
)
password_entry.pack(pady=10)


# ---------------- SHOW PASSWORD ---------------- #
show_password_var = tk.BooleanVar()
show_password_check = tk.Checkbutton(
    root,
    text="Show Password",
    variable=show_password_var,
    command=toggle_password,
    bg=BG_COLOR,
    font=("Arial", 12)
)
show_password_check.pack()


# ---------------- MOBILE NUMBER ---------------- #
mobile_label = tk.Label(
    root,
    text="Mobile Number",
    font=("Arial", 16),
    bg=BG_COLOR
)
mobile_label.pack(pady=(10, 0))

mobile_entry = tk.Entry(
    root,
    font=("Arial", 16),
    width=30
)
mobile_entry.pack(pady=10)


# ---------------- EMAIL ---------------- #
email_label = tk.Label(
    root,
    text="Email ID",
    font=("Arial", 16),
    bg=BG_COLOR
)
email_label.pack()

email_entry = tk.Entry(
    root,
    font=("Arial", 16),
    width=30
)
email_entry.pack(pady=10)


# ---------------- SUBMIT BUTTON ---------------- #
submit_button = tk.Button(
    root,
    text="SUBMIT",
    font=("Arial", 16, "bold"),
    width=20,
    bg="green",
    fg="white",
    command=validate
)
submit_button.pack(pady=30, ipady=8)

# ---------------- MAINLOOP ---------------- #
root.mainloop()