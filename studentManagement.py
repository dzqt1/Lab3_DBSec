import tkinter as tk
from tkinter import ttk, messagebox
import config
import pyodbc

def panel(parent, manv, malop, app_controller):
    frame = tk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, text=f"Students in Class {malop}", font=("Arial", 14, "bold")).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("MASV", "HOTEN", "NGAYSINH", "DIACHI"), show='headings')
    tree.heading("MASV", text="Student ID")
    tree.heading("HOTEN", text="Student Name")
    tree.heading("NGAYSINH", text="Date of Birth")
    tree.heading("DIACHI", text="Address")
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    button_frame = tk.Frame(frame)
    button_frame.pack(pady=15)
    tk.Button(button_frame, text="Back to Classes", command=app_controller.show_class_panel, width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)
    
    tk.Button(button_frame, text="Add Student", command=add_student, width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)
    tk.Button(button_frame, text="Remove Student", command=remove_student, width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)
    tk.Button(button_frame, text="Update Student", command=update_student, width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)
    
    try:
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC SP_SEL_SV_BY_LOP ?", (malop,))
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3]))
    except Exception as e:
        messagebox.showerror("Database error", str(e))
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def add_student():
    messagebox.showinfo("Info", "Add Student functionality not implemented yet.")

def remove_student():
    messagebox.showinfo("Info", "Remove Student functionality not implemented yet.")

def update_student():
    messagebox.showinfo("Info", "Update Student functionality not implemented yet.")