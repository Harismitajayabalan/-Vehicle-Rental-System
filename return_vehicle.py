import tkinter as tk
from tkinter import messagebox
from datetime import date, timedelta
from db import conn, cur  # Assumes a separate db.py file handles database connectivity

TITLE = "Vehicle Booking - Return"
BG_COLOR = "#D6EAF8"

def open_return_page():
    """
    Initializes and opens the Vehicle Return GUI window.
    Handles database validation, late fine calculation, and record updating.
    """
    root = tk.Tk()
    root.title(TITLE)
    root.state("zoomed")  # Launch in full-screen/maximized mode
    root.configure(bg=BG_COLOR)

    # ASSET LOADING
    
    logo_image = None
    try:
        # Load and scale down the application logo
        logo_path = r"D:\Desktop\PYTHON\VS\VS\logo.png"
        raw_logo = tk.PhotoImage(file=logo_path)
        logo_image = raw_logo.subsample(4, 4) 
        root.iconphoto(False, raw_logo) 
    except Exception as e:
        # Graceful fallback if the image file is missing or path is incorrect
        print(f"⚠️ Warning: Image failed to load. Error: {e}")

    
    # STATE VARIABLES
    
    booking_id_var = tk.StringVar() # Binds to the Booking ID input field
    today_date = date.today()       # Standardizes the return date to system time

    
    # CORE BUSINESS LOGIC & DATABASE OPERATIONS
    
    def return_vehicle():
        """
        Processes the vehicle return transaction.
        Validates ID, calculates late fines based on vehicle type, 
        and updates the database records.
        """
        booking_id = booking_id_var.get()
        
        # 1. Input Validation
        if not booking_id.isdigit():
            messagebox.showerror("Error", "Please enter a valid numeric Booking ID")
            return

        actual_return_date = date.today()

        # 2. Fetch existing booking records
        cur.execute("""
            SELECT booking_date, booking_days, total_amount, vehicle_id, return_status 
            FROM bookings 
            WHERE booking_id=%s
        """, (booking_id,))

        booking = cur.fetchone()

        if booking:
            # Unpack the database record
            booking_date, booking_days, total_amount, vehicle_id, status = booking

            # 3. State Check to prevent double-returns
            if status == "Returned":
                messagebox.showinfo("Already Returned", "This vehicle has already been returned.")
                return
                
            expected_return = booking_date + timedelta(days=booking_days)

            # 4. Fetch vehicle metadata to determine fine tier
            cur.execute("SELECT vehicle_type FROM vehicles WHERE vehicle_id=%s", (vehicle_id,))
            vehicle_type_result = cur.fetchone()
            
            if not vehicle_type_result:
                messagebox.showerror("Error", "Vehicle data missing from database.")
                return
                
            vehicle_type = vehicle_type_result[0]

            # 5. Fine Calculation Logic
            late_days = (actual_return_date - expected_return).days

            if late_days > 0:
                # Tiered fine system based on vehicle category
                fine = late_days * 1000 if vehicle_type == "Car" else late_days * 500
            else:
                fine = 0

            final_amount = total_amount + fine

            # 6. Database Update Transaction
            cur.execute("""
                UPDATE bookings
                SET return_status=%s, late_fine=%s, actual_return_date=%s
                WHERE booking_id=%s
            """, ("Returned", fine, actual_return_date, booking_id))

            conn.commit()

            # 7. Update UI with Success Receipt
            result_label.config(
                text=f"✅ Vehicle Returned Successfully!\n\n"
                     f"Expected Return: {expected_return}\n"
                     f"Actual Return: {actual_return_date}\n\n"
                     f"Late Days: {max(0, late_days)}\n"
                     f"Late Fine: ₹{fine}\n\n"
                     f"Final Amount to Pay: ₹{final_amount}",
                fg="green"
            )
        else:
            messagebox.showerror("Error", "Booking ID not found in database!")

    def exit_app():
        """Safely closes the application window after user confirmation."""
        if messagebox.askyesno("Exit", "Are you sure you want to close this page?"):
            root.destroy()
    
    # USER INTERFACE RENDERING
    
    # Header Section (Logo + Titles)
    if logo_image:
        tk.Label(root, text="  VEHICLE BOOKING", image=logo_image, compound="left", 
                 font=("Arial", 25, "bold"), bg=BG_COLOR, fg="darkblue").pack(pady=(55, 10))
    else:
        tk.Label(root, text="VEHICLE BOOKING", font=("Arial", 25, "bold"), 
                 bg=BG_COLOR, fg="darkblue").pack(pady=(55, 10))

    tk.Label(root, text="RETURN VEHICLE", font=("Arial", 20, "bold"), bg=BG_COLOR).pack(pady=(0, 20))

    # Input Section: Booking ID
    frame1 = tk.Frame(root, bg=BG_COLOR)
    frame1.pack(pady=15)

    tk.Label(frame1, text="Booking ID:", font=("Arial", 16, "bold"), bg=BG_COLOR).grid(row=0, column=0, padx=10, pady=10)
    tk.Entry(frame1, textvariable=booking_id_var, font=("Arial", 16), width=20).grid(row=0, column=1, padx=10, pady=10)

    # Display Section: Return Date
    frame2 = tk.Frame(root, bg=BG_COLOR)
    frame2.pack(pady=15)

    tk.Label(frame2, text="Return Date (Today):", font=("Arial", 16, "bold"), bg=BG_COLOR).grid(row=0, column=0, padx=10, pady=10)
    tk.Label(frame2, text=str(today_date), font=("Arial", 16, "bold"), fg="darkblue", bg=BG_COLOR).grid(row=0, column=1, padx=10, pady=10)

    # Action Buttons Section
    btn_frame = tk.Frame(root, bg=BG_COLOR)
    btn_frame.pack(pady=40) 

    tk.Button(btn_frame, text="Process Return", font=("Arial", 16, "bold"),
              command=return_vehicle, bg="orange", fg="white", width=20).pack(pady=15, ipady=8) 

    tk.Button(btn_frame, text="Exit", font=("Arial", 16, "bold"),
              command=exit_app, bg="red", fg="white", width=20).pack(pady=15, ipady=8) 

    # Dynamic Status Display Output
    result_label = tk.Label(root, text="", font=("Arial", 16, "bold"), bg=BG_COLOR)
    result_label.pack(pady=20)

    # Start the GUI event loop
    root.mainloop()

# Allows module to be run directly for testing without launching the full app
if __name__ == "__main__":
    open_return_page()