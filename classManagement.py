import tkinter as tk
from tkinter import ttk, messagebox
import config
import pyodbc

def panel(parent, manv, app_controller):
    frame = tk.Frame(parent)
    frame.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame, text="Your Classes", font=("Arial", 14, "bold")).pack(pady=10)

    tree = ttk.Treeview(frame, columns=("MALOP", "TENLOP"), show='headings')
    tree.heading("MALOP", text="Class ID")
    tree.heading("TENLOP", text="Class Name")
    tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    try:
        conn = config.get_connection()
        cursor = conn.cursor()
        cursor.execute("EXEC SP_SEL_LOP_BY_NV ?", (manv,))
        for row in cursor.fetchall():
            tree.insert("", tk.END, values=(row[0], row[1]))
    except Exception as e:
        messagebox.showerror("Database error", str(e))
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

    btn_frame = tk.Frame(frame)
    btn_frame.pack(pady=15)

    def manage_students():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a class first!")
            return
        malop = tree.item(selected[0], "values")[0]
        app_controller.show_student_panel(malop)

    def enter_scores():
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a class first!")
            return
        malop = tree.item(selected[0], "values")[0]
        app_controller.show_score_panel(malop)

    tk.Button(btn_frame, text="Manage Students", command=manage_students, width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)
    tk.Button(btn_frame, text="Enter Grades", command=enter_scores, width=20, bg="#e0e0e0").pack(side=tk.LEFT, padx=15)