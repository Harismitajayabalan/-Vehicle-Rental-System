import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, timedelta
from db import conn, cur
import os

TITLE = "Vehicle Rental System"
BG_COLOR = "#D6EAF8"

# 1. Wrapped in a function so the Login page can send the username
def open_booking_page(logged_in_username=""):
    root = tk.Tk()
    root.title(TITLE)
    root.state("zoomed")
    root.configure(bg=BG_COLOR)

    # ================= ADDED: LOGO PREPARATION ================= #
    logo_image = None
    try:
        current_path = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_path, "logo.png")
        raw_logo = tk.PhotoImage(file=logo_path)
        logo_image = raw_logo.subsample(4, 4) 
        root.iconphoto(False, raw_logo) # Sets the top window icon
    except Exception as e:
        print(f"⚠️ Warning: Logo failed to load: {e}")
    # =========================================================== #

    # ---------------- VARIABLES ---------------- #
    customer_name_var = tk.StringVar()
    phone_var = tk.StringVar()
    vehicle_type_var = tk.StringVar()
    category_var = tk.StringVar()
    brand_var = tk.StringVar()
    model_var = tk.StringVar()
    days_var = tk.StringVar()
    
    # Using a dictionary to avoid global variable scope errors in Tkinter
    selected_vehicle = {"id": None}

    # 2. AUTO-FETCH LOGIC
    if logged_in_username:
        try:
            cur.execute("SELECT username, mobile FROM users WHERE username=%s", (logged_in_username,))
            user_data = cur.fetchone()
            if user_data:
                customer_name_var.set(user_data[0])  # Auto-fills Name
                phone_var.set(user_data[1])          # Auto-fills Phone
        except Exception as e:
            print(f"Database error fetching user: {e}")

    # ---------------- VALIDATION ---------------- #
    def validate():
        if not customer_name_var.get().strip() or not phone_var.get().isdigit():
            messagebox.showerror("Error", "Enter Valid Customer Name and Phone Number")
            return False
        if not vehicle_type_var.get() or not category_var.get() or not days_var.get():
            messagebox.showerror("Error", "Please fill all dropdowns")
            return False
        if not selected_vehicle["id"]:
            messagebox.showerror("Error", "Select Vehicle from Table")
            return False
        return True

    # ---------------- CATEGORY & MODELS UPDATE ---------------- #
    def update_categories(event=None):
        if vehicle_type_var.get() == "Car":
            category_combo["values"] = ["5 Seater", "7 Seater"]
        else:
            category_combo["values"] = ["Below 150cc", "150cc-250cc", "Above 250cc"]
        category_var.set("")
        brand_var.set("")
        model_var.set("")

    def update_models(event=None):
        cur.execute("SELECT DISTINCT model FROM vehicles WHERE brand=%s", (brand_var.get(),))
        model_combo["values"] = [i[0] for i in cur.fetchall()]

    # ---------------- SHOW VEHICLES ---------------- #
    def show_vehicles():
        vehicle_table.delete(*vehicle_table.get_children())
        cur.execute("""
            SELECT vehicle_id, brand, model, category, rent_per_day
            FROM vehicles
            WHERE vehicle_type=%s AND category=%s
            AND vehicle_id NOT IN (
                SELECT vehicle_id FROM bookings WHERE return_status = 'Not Returned'
            )
        """, (vehicle_type_var.get(), category_var.get()))
        
        rows = cur.fetchall()
        if not rows:
            messagebox.showinfo("No Data", "No vehicles available for this selection")
            return
            
        brands = set()
        for row in rows:
            vehicle_table.insert("", tk.END, values=row)
            brands.add(row[1])
        brand_combo["values"] = list(brands)

    def select_vehicle(event):
        selected = vehicle_table.focus()
        data = vehicle_table.item(selected, "values")
        if data:
            selected_vehicle["id"] = data[0]
            brand_var.set(data[1])
            model_var.set(data[2])

    # ---------------- CLEAR FORM FIELDS ---------------- #
    def clear_form():
        # Clears vehicle selection so the user can make another booking easily
        vehicle_type_var.set("")
        category_var.set("")
        brand_var.set("")
        model_var.set("")
        days_var.set("")
        selected_vehicle["id"] = None
        vehicle_table.delete(*vehicle_table.get_children())
        brand_combo["values"] = []
        model_combo["values"] = []
        category_combo["values"] = []

    # ---------------- BOOK VEHICLE ---------------- #
    def book_vehicle():
        if not validate(): return
        
        days = int(days_var.get())
        name = customer_name_var.get()
        phone = phone_var.get()
        booking_date = date.today()
        expected_return = booking_date + timedelta(days=days)

        cur.execute("SELECT vehicle_id, rent_per_day FROM vehicles WHERE vehicle_id=%s", (selected_vehicle["id"],))
        vehicle_results = cur.fetchall()
        
        if not vehicle_results: return
        vehicle_id = vehicle_results[0][0]
        rent = vehicle_results[0][1]
        total = rent * days

        confirmation_msg = (f"Please confirm details:\n\nCustomer: {name}\nPhone: {phone}\n"
                            f"Vehicle: {brand_var.get()} {model_var.get()}\n"
                            f"Booking Date: {booking_date}\nExpected Return: {expected_return}\nTotal: ₹{total}")
        
        if messagebox.askokcancel("Confirm Details", confirmation_msg):
            
            cur.execute("SELECT customer_id FROM customers WHERE phone=%s", (phone,))
            customer_results = cur.fetchall()
            
            if customer_results:
                customer_id = customer_results[0][0]
            else:
                cur.execute("INSERT INTO customers(customer_name, phone) VALUES (%s,%s)", (name, phone))
                conn.commit()
                customer_id = cur.lastrowid

            cur.execute("""
                INSERT INTO bookings (customer_id, vehicle_id, booking_date, booking_days, total_amount, return_status, actual_return_date, late_fine)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """, (customer_id, vehicle_id, booking_date, days, total, "Not Returned", expected_return, 0))
            conn.commit()
            
            # Show success status on the page
            status_label.config(text=f"Successfully Registered! Booking ID: {cur.lastrowid}", fg="green")
            root.update()
            
            # Show popup
            messagebox.showinfo("Success", f"Successfully Registered!\nYour Booking ID is: {cur.lastrowid}")
            
            # 1. FIXED: Removed root.destroy() and dashboard redirect so the user stays on the page
            clear_form()

    # ---------------- REDIRECT TO RETURN PAGE ---------------- #
    def go_to_return():
        try:
            import return_vehicle
            root.destroy()
            return_vehicle.open_return_page()
        except ImportError:
            messagebox.showerror("Error", "return_vehicle.py not found!")
        except Exception as e:
            print(f"Transition error: {e}")

    # ---------------- EXIT APP ---------------- #
    def exit_app():
        if messagebox.askyesno("Exit", "Are you sure you want to exit the booking page?"):
            root.destroy()
            # Optional: Return to dashboard or login here if desired
            # try:
            #     import dashboard
            # except ImportError:
            #     pass

    # ---------------- UI ---------------- #
    
    # Logo and Title Side-by-Side
    if logo_image:
        tk.Label(root, text="  VEHICLE BOOKING SYSTEM", image=logo_image, compound="left", 
                 font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=10)
    else:
        tk.Label(root, text="VEHICLE BOOKING SYSTEM", font=("Arial", 22, "bold"), bg=BG_COLOR).pack(pady=10)

    frame1 = tk.LabelFrame(root, text="Customer Details", bg=BG_COLOR, font=("Arial", 12, "bold"))
    frame1.pack(fill="x", padx=20, pady=5)
    
    tk.Label(frame1, text="Name:", bg=BG_COLOR).grid(row=0, column=0, padx=10, pady=5, sticky="e")
    tk.Entry(frame1, textvariable=customer_name_var, width=30).grid(row=0, column=1, pady=5)
    tk.Label(frame1, text="Phone:", bg=BG_COLOR).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    tk.Entry(frame1, textvariable=phone_var, width=30).grid(row=1, column=1, pady=5)

    frame2 = tk.LabelFrame(root, text="Vehicle Selection", bg=BG_COLOR, font=("Arial", 12, "bold"))
    frame2.pack(fill="x", padx=20, pady=5)
    tk.Label(frame2, text="Vehicle Type:", bg=BG_COLOR).grid(row=0, column=0, padx=10, pady=5, sticky="e")
    vehicle_type_combo = ttk.Combobox(frame2, textvariable=vehicle_type_var, values=["Car", "Bike"], state="readonly")
    vehicle_type_combo.grid(row=0, column=1, pady=5)
    vehicle_type_combo.bind("<<ComboboxSelected>>", update_categories)
    tk.Label(frame2, text="Category:", bg=BG_COLOR).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    category_combo = ttk.Combobox(frame2, textvariable=category_var, state="readonly")
    category_combo.grid(row=1, column=1, pady=5)
    tk.Button(frame2, text="Show Vehicles", command=show_vehicles, bg="blue", fg="white").grid(row=2, column=1, pady=10)

    table_frame = tk.Frame(root, bg=BG_COLOR)
    table_frame.pack(fill="both", expand=True, padx=20, pady=5)
    scrollbar = tk.Scrollbar(table_frame)
    scrollbar.pack(side="right", fill="y")
    vehicle_table = ttk.Treeview(table_frame, columns=("id", "brand", "model", "category", "rent"), show="headings", yscrollcommand=scrollbar.set)
    for col, text in zip(("id", "brand", "model", "category", "rent"), ("ID", "Brand", "Model", "Category", "Rent/Day")):
        vehicle_table.heading(col, text=text)
    vehicle_table.pack(fill="both", expand=True)
    scrollbar.config(command=vehicle_table.yview)
    vehicle_table.bind("<ButtonRelease-1>", select_vehicle)

    frame3 = tk.LabelFrame(root, text="Booking Details", bg=BG_COLOR, font=("Arial", 12, "bold"))
    frame3.pack(fill="x", padx=20, pady=5)
    tk.Label(frame3, text="Brand:", bg=BG_COLOR).grid(row=0, column=0, padx=10, pady=5, sticky="e")
    brand_combo = ttk.Combobox(frame3, textvariable=brand_var, state="readonly")
    brand_combo.grid(row=0, column=1, pady=5)
    brand_combo.bind("<<ComboboxSelected>>", update_models)
    tk.Label(frame3, text="Model:", bg=BG_COLOR).grid(row=1, column=0, padx=10, pady=5, sticky="e")
    model_combo = ttk.Combobox(frame3, textvariable=model_var, state="readonly")
    model_combo.grid(row=1, column=1, pady=5)
    tk.Label(frame3, text="Rental Days:", bg=BG_COLOR).grid(row=2, column=0, padx=10, pady=5, sticky="e")
    days_combo = ttk.Combobox(frame3, textvariable=days_var, values=["1","2","3","5","7","10","15","20","30"], state="readonly")
    days_combo.grid(row=2, column=1, pady=5)

    # ---------------- PERFECTLY ALIGNED BUTTONS ---------------- #
    btn_frame = tk.Frame(root, bg=BG_COLOR)
    btn_frame.pack(pady=20)
    
    # All buttons are now placed side-by-side using pack(side="left")
    tk.Button(btn_frame, text="BOOK VEHICLE", bg="green", fg="white", font=("Arial", 12, "bold"), width=15, command=book_vehicle).pack(side="left", padx=15)
    tk.Button(btn_frame, text="RETURN VEHICLE", bg="orange", fg="white", font=("Arial", 12, "bold"), width=15, command=go_to_return).pack(side="left", padx=15)
    # 2. ADDED: Exit Button
    tk.Button(btn_frame, text="EXIT", bg="red", fg="white", font=("Arial", 12, "bold"), width=15, command=exit_app).pack(side="left", padx=15)

    status_label = tk.Label(root, text="", font=("Arial", 16, "bold"), bg=BG_COLOR)
    status_label.pack(pady=10)

    root.mainloop()

# This is just for testing
if __name__ == "__main__":
    open_booking_page("")