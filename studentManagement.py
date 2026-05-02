import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import config
import pyodbc   
from datetime import datetime

def panel(parent, manv, malop, app_controller):
    frame = tk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True)
    global _malop
    _malop = malop
    tk.Label(frame, text=f"Students in Class {_malop}", font=("Arial", 14, "bold")).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("MASV", "HOTEN", "NGAYSINH", "DIACHI"), show='headings')
    tree.heading("MASV", text="Student ID")
    tree.heading("HOTEN", text="Student Name")
    tree.heading("NGAYSINH", text="Date of Birth")
    tree.heading("DIACHI", text="Address")
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    button_frame1 = tk.Frame(frame)
    button_frame1.pack(pady=5)

    button_frame2 = tk.Frame(frame)
    button_frame2.pack(pady=15)

    tk.Button(button_frame1, text="Add Student", command=lambda: add_student(tree), width=20, bg="#e0e0e0", fg="green").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame1, text="Remove Student", command=lambda: remove_student(tree), width=20, bg="#e0e0e0", fg="red").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame1, text="Update Student", command=lambda: update_student(tree), width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=5)
    
    tk.Button(button_frame2, text="Back to Classes", command=app_controller.show_class_panel, width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame2, text="Refresh List", command=lambda: refresh_student_list(tree), width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=5)
    tk.Button(button_frame2, text="Enter Grades", command=lambda: show_grade_panel(tree, app_controller), width=20, bg="#dff0d8").pack(side=tk.LEFT, padx=5)



    fetch_students(tree)

def add_student(tree):
    
    dialog = tk.Toplevel()
    dialog.title("Add New Student")
    dialog.geometry("300x300")

    dialog.transient() 
    dialog.grab_set()

    grid_frame = tk.Frame(dialog)
    grid_frame.pack(padx=20, pady=20)

    tk.Label(grid_frame, text="Student ID:").grid(row=0, column=0, padx=10, pady=10)
    student_id_entry = tk.Entry(grid_frame, width=25)
    student_id_entry.grid(row=0, column=1, padx=10, pady=10)

    tk.Label(grid_frame, text="Student Name:").grid(row=1, column=0, padx=10, pady=10)
    student_name_entry = tk.Entry(grid_frame, width=25)
    student_name_entry.grid(row=1, column=1, padx=10, pady=10)

    tk.Label(grid_frame, text="Date of Birth (dd/mm/yyyy):").grid(row=2, column=0, padx=10, pady=10)
    student_dob_entry = tk.Entry(grid_frame, width=25)
    student_dob_entry.grid(row=2, column=1, padx=10, pady=10)

    tk.Label(grid_frame, text="Address:").grid(row=3, column=0, padx=10, pady=10)
    student_address_entry = tk.Entry(grid_frame, width=25)
    student_address_entry.grid(row=3, column=1, padx=10, pady=10)

    def on_submit():
        student_id = student_id_entry.get().strip()
        student_name = student_name_entry.get().strip()
        student_dob_raw = student_dob_entry.get().strip()
        student_address = student_address_entry.get().strip()

        if not all([student_id, student_name, student_dob_raw, student_address]):
            messagebox.showerror("Input error", "All fields are required.")
            return
        
        try:
            dob_object = datetime.strptime(student_dob_raw, "%d/%m/%Y")
            student_dob = dob_object.strftime("%Y-%m-%d") # convert to ISO standard
        except ValueError:
            messagebox.showerror("Format Error", "Date of Birth must be in format: DD/MM/YYYY")
            return
        try:
            conn = config.get_connection()
            cursor = conn.cursor()
            cursor.execute("EXEC SP_INS_SINHVIEN ?, ?, ?, ?, ?, ?, ?", (student_id, student_name, student_dob, student_address, _malop, student_id, "123"))
            conn.commit()
            messagebox.showinfo("Info", f"Student {student_name} added successfully!")
        except Exception as e:
            messagebox.showerror("Database error", str(e))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

        refresh_student_list(tree)
        dialog.destroy()

    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)

    tk.Button(button_frame, text="Submit", command=on_submit, width=15, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=15, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=10)

def remove_student(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection error", "Please select a student to remove.")
        return

    student_id = tree.item(selected_item[0])['values'][0]

    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to remove student {student_id}?")
    if not confirm:
        return

    try:
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC SP_DEL_SINHVIEN ?", (student_id,))
        conn.commit()
        messagebox.showinfo("Info", f"Student {student_id} removed successfully!")
    except Exception as e:
        messagebox.showerror("Database error", str(e))
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

    refresh_student_list(tree)

def update_student(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection error", "Please select a student to update.")
        return
        
    dialog = tk.Toplevel()
    dialog.title("Update Student Information")
    dialog.geometry("300x300")

    dialog.transient()
    dialog.grab_set()

    grid_frame = tk.Frame(dialog)
    grid_frame.pack(padx=20, pady=20)

    tk.Label(grid_frame, text="Student ID:").grid(row=0, column=0, padx=10, pady=10)
    student_id_entry = tk.Entry(grid_frame, width=25)
    student_id_entry.grid(row=0, column=1, padx=10, pady=10)
    student_id_entry.insert(0, tree.item(selected_item[0])['values'][0])
    student_id_entry.config(state='disabled')

    tk.Label(grid_frame, text="Student Name:").grid(row=1, column=0, padx=10, pady=10)
    student_name_entry = tk.Entry(grid_frame, width=25)
    student_name_entry.grid(row=1, column=1, padx=10, pady=10)
    student_name_entry.insert(0, tree.item(selected_item[0])['values'][1])

    tk.Label(grid_frame, text="Date of Birth:").grid(row=2, column=0, padx=10, pady=10)
    student_dob_entry = tk.Entry(grid_frame, width=25)
    student_dob_entry.grid(row=2, column=1, padx=10, pady=10)
    student_dob_entry.insert(0, tree.item(selected_item[0])['values'][2])

    tk.Label(grid_frame, text="Address:").grid(row=3, column=0, padx=10, pady=10)
    student_address_entry = tk.Entry(grid_frame, width=25)
    student_address_entry.grid(row=3, column=1, padx=10, pady=10)
    student_address_entry.insert(0, tree.item(selected_item[0])['values'][3])

    def on_submit():
        student_id = student_id_entry.get().strip()
        student_name = student_name_entry.get().strip()
        student_dob = student_dob_entry.get().strip()
        student_address = student_address_entry.get().strip()

        if not all([student_name, student_dob, student_address]):
            messagebox.showerror("Input error", "All fields except Student ID are required.")
            return

        try:
            conn = config.get_connection()
            cursor = conn.cursor()
            cursor.execute("EXEC SP_UPD_SINHVIEN ?, ?, ?, ?", (student_id, student_name, student_dob, student_address))
            conn.commit()
            messagebox.showinfo("Info", f"Student {student_id} updated successfully!")
        except Exception as e:
            messagebox.showerror("Database error", str(e))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

        refresh_student_list(tree)
        dialog.destroy()
    
    button_frame = tk.Frame(dialog)
    button_frame.pack(pady=10)
    tk.Button(button_frame, text="Submit", command=on_submit, width=15, bg="#4CAF50", fg="white").pack(side=tk.LEFT, padx=10)
    tk.Button(button_frame, text="Cancel", command=dialog.destroy, width=15, bg="#f44336", fg="white").pack(side=tk.LEFT, padx=10)
    
    refresh_student_list(tree)

def fetch_students(tree):
    try:
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC SP_SEL_SV_BY_LOP ?", (_malop,))
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3]))
    except Exception as e:
        messagebox.showerror("Database error", str(e))
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def refresh_student_list(tree):
    for item in tree.get_children():
        tree.delete(item)
    fetch_students(tree)

def show_grade_panel(tree, app_controller):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection error", "Please select a student to manage grades.")
        return

    masv = tree.item(selected_item[0])['values'][0]
    app_controller.show_grade_panel(masv, _malop)