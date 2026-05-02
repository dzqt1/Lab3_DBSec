import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import config
import pyodbc

def panel(parent, manv, masv, malop, app_controller):
    frame = tk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True)
    global _masv
    _masv = masv
    global _manv
    _manv = manv
    tk.Label(frame, text=f"Grades for Student {_masv}", font=("Arial", 14, "bold")).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("MAMH", "TENMH", "DIEM"), show='headings')
    tree.heading("MAMH", text="Course ID")
    tree.heading("TENMH", text="Course Name")
    tree.heading("DIEM", text="Grade")
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    button_frame = tk.Frame(frame)
    button_frame.pack(pady=15)
    tk.Button(button_frame, text="Edit grade", command=lambda: edit_grade(tree), width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)
    tk.Button(button_frame, text="Confirm", command=lambda: on_confirm(tree), width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)
    tk.Button(button_frame, text="Back to Students", command=lambda: app_controller.show_student_panel(malop), width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)

    fetch_subjects(tree)

def on_confirm(tree):    
    try:
        conn = pyodbc.connect(config.CONNECTION_STRING)
        cursor = conn.cursor()
        for item in tree.get_children():
            mamh, tenmh, diem = tree.item(item, "values")
            if diem != "":
                cursor.execute("EXEC SP_INS_DIEM ?, ?, ?, ?", _masv, mamh, diem, _manv)
        conn.commit()
        messagebox.showinfo("Success", "Grades updated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to update grades: {e}")
    finally:
        cursor.close()
        conn.close()

def fetch_subjects(tree):
    try:
        conn = pyodbc.connect(config.CONNECTION_STRING)
        cursor = conn.cursor()
        cursor.execute("EXEC SP_SEL_HOCPHAN")
        rows = cursor.fetchall()
        tree.delete(*tree.get_children())
        for row in rows:
            tree.insert("", tk.END, values=(row[0], row[1], ""))
    except Exception as e:
        messagebox.showerror("Error", f"Failed to fetch subjects: {e}")
    finally:
        cursor.close()
        conn.close()

def edit_grade(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection error", "Please select a course to edit the grade.")
        return

    current_grade = tree.item(selected_item[0])['values'][2]
    new_grade = simpledialog.askstring("Edit Grade", "Enter new grade:", initialvalue=current_grade)
    if new_grade is not None:
        tree.set(selected_item, column="DIEM", value=new_grade)