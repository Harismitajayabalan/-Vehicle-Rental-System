import tkinter as tk
from tkinter import messagebox
import os

TITLE = "Dashboard - Vehicle Rental System"
BG_COLOR = "#D6EAF8"

def open_dashboard(username="User"):
    root = tk.Tk()
    root.title(TITLE)
    root.state("zoomed")
    root.configure(bg=BG_COLOR)

    # ================= LOAD LOGO ================= #
    logo_image = None
    try:
        current_path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_path, "logo.png")
        raw_logo = tk.PhotoImage(file=logo_path)
        logo_image = raw_logo.subsample(4, 4) 
        root.iconphoto(False, raw_logo) 
    except Exception as e:
        print(f"⚠️ Warning: Image failed to load. Error: {e}")
    # =============================================== #

    # ---------------- NAVIGATION FUNCTIONS ---------------- #
    def go_to_booking():
        root.destroy()
        try:
            import booking
            # Pass the username from the dashboard to the booking page!
            booking.open_booking_page(username)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open booking page: {e}")

    def go_to_return():
        root.destroy()
        try:
            import return_vehicle
            return_vehicle.open_return_page()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open return page: {e}")

    def logout():
        if messagebox.askyesno("Logout", "Are you sure you want to log out?"):
            root.destroy()
            # This simply closes the dashboard. 
            # If you want to reopen login, you can import login here.
            messagebox.showinfo("Logged Out", "You have successfully logged out.")

    # ---------------- UI ELEMENTS ---------------- #
    # Header Frame
    header_frame = tk.Frame(root, bg=BG_COLOR)
    header_frame.pack(fill="x", pady=(40, 20))

    if logo_image:
        tk.Label(header_frame, text="  VEHICLE RENTAL SYSTEM", image=logo_image, compound="left", 
                 font=("Arial", 35, "bold"), bg=BG_COLOR, fg="darkblue").pack()
    else:
        tk.Label(header_frame, text="VEHICLE RENTAL SYSTEM", font=("Arial", 35, "bold"), 
                 bg=BG_COLOR, fg="darkblue").pack()

    # Welcome Message (Personalized with the username!)
    tk.Label(root, text=f"Welcome, {username}!", font=("Arial", 22, "bold"), 
             bg=BG_COLOR, fg="#333333").pack(pady=10)
    
    tk.Label(root, text="Please select an option below:", font=("Arial", 16), 
             bg=BG_COLOR, fg="#555555").pack(pady=10)

    # Buttons Frame
    btn_frame = tk.Frame(root, bg=BG_COLOR)
    btn_frame.pack(pady=40)

    # Navigation Buttons
    tk.Button(btn_frame, text="Book a Vehicle", font=("Arial", 18, "bold"), 
              bg="green", fg="white", width=25, command=go_to_booking).pack(pady=15, ipady=12)
    
    tk.Button(btn_frame, text="Return a Vehicle", font=("Arial", 18, "bold"), 
              bg="orange", fg="white", width=25, command=go_to_return).pack(pady=15, ipady=12)
    
    tk.Button(btn_frame, text="Logout", font=("Arial", 18, "bold"), 
              bg="red", fg="white", width=25, command=logout).pack(pady=15, ipady=12)

    root.mainloop()

# Allows you to test this page individually
if __name__ == "__main__":
    open_dashboard("TestAdmin")