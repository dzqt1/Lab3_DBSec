import tkinter as tk
from tkinter import ttk, messagebox
import config

def panel(parent, manv, app_controller):
    # Main container
    main_frame = tk.Frame(parent)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Layout Trái/Phải ---
    left_frame = tk.LabelFrame(main_frame, text="My Assigned Classes", font=("Arial", 12, "bold"))
    left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

    right_frame = tk.LabelFrame(main_frame, text="Other / Unassigned Classes", font=("Arial", 12, "bold"))
    right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

    # --- Khởi tạo Treeviews ---
    cols = ("MALOP", "TENLOP")
    
    tree_my = ttk.Treeview(left_frame, columns=cols, show='headings', height=12)
    tree_my.heading("MALOP", text="Class ID")
    tree_my.heading("TENLOP", text="Class Name")
    tree_my.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tree_other = ttk.Treeview(right_frame, columns=cols, show='headings', height=12)
    tree_other.heading("MALOP", text="Class ID")
    tree_other.heading("TENLOP", text="Class Name")
    tree_other.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # --- Load Data bằng Stored Procedures ---
    def load_data():
        for item in tree_my.get_children(): tree_my.delete(item)
        for item in tree_other.get_children(): tree_other.delete(item)
        
        try:
            conn = config.get_connection()
            cursor = conn.cursor()
            
            # Load lớp đang quản lý (Sử dụng SP)
            cursor.execute("EXEC SP_SEL_LOP_BY_NV ?", (manv,))
            for row in cursor.fetchall():
                tree_my.insert("", tk.END, values=(row[0], row[1]))
                
            # Load lớp không quản lý (Sử dụng SP)
            cursor.execute("EXEC SP_SEL_LOP_OTHER ?", (manv,))
            for row in cursor.fetchall():
                tree_other.insert("", tk.END, values=(row[0], row[1]))
                
        except Exception as e:
            messagebox.showerror("Database error", str(e))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    load_data() 

    # --- Các hàm xử lý chức năng ---
    def view_class(tree):
        selected = tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Please select a class to view!")
            return
        
        malop = tree.item(selected[0], "values")[0]
        tenlop = tree.item(selected[0], "values")[1]

        top = tk.Toplevel(parent)
        top.title(f"Class Details - {malop}")
        top.geometry("600x400")
        top.grab_set()

        tk.Label(top, text=f"Class ID: {malop}", font=("Arial", 12, "bold")).pack(pady=5)
        tk.Label(top, text=f"Class Name: {tenlop}", font=("Arial", 12)).pack(pady=5)
        tk.Label(top, text="Student List:", font=("Arial", 10, "italic")).pack(anchor=tk.W, padx=10)
        
        tree_sv = ttk.Treeview(top, columns=("MASV", "HOTEN", "NGAYSINH", "DIACHI"), show='headings')
        tree_sv.heading("MASV", text="Student ID")
        tree_sv.heading("HOTEN", text="Full Name")
        tree_sv.heading("NGAYSINH", text="DOB")
        tree_sv.heading("DIACHI", text="Address")
        tree_sv.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        try:
            conn = config.get_connection()
            cursor = conn.cursor()
            cursor.execute("EXEC SP_SEL_SV_BY_LOP ?", (malop,))
            for row in cursor.fetchall():
                ngaysinh_str = str(row[2])[:10] if row[2] else ""
                tree_sv.insert("", tk.END, values=(row[0], row[1], ngaysinh_str, row[3]))
        except Exception as e:
            messagebox.showerror("Database error", str(e))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def add_to_management():
        selected = tree_other.selection()
        if not selected: return
        malop = tree_other.item(selected[0], "values")[0]
        try:
            conn = config.get_connection()
            cursor = conn.cursor()
            # Assign to me (Sử dụng SP)
            cursor.execute("EXEC SP_ASSIGN_LOP ?, ?", (manv, malop))
            conn.commit()
            load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def remove_from_management():
        selected = tree_my.selection()
        if not selected: return
        malop = tree_my.item(selected[0], "values")[0]
        try:
            conn = config.get_connection()
            cursor = conn.cursor()
            # Unassign (Sử dụng SP)
            cursor.execute("EXEC SP_UNASSIGN_LOP ?", (malop,))
            conn.commit()
            load_data()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_class_db():
        selected = tree_my.selection()
        if not selected: return
        malop = tree_my.item(selected[0], "values")[0]
        if messagebox.askyesno("Confirm", f"Are you sure you want to permanently delete class '{malop}' from the Database?"):
            try:
                conn = config.get_connection()
                cursor = conn.cursor()
                # Delete from DB (Sử dụng SP)
                cursor.execute("EXEC SP_DEL_LOP ?", (malop,))
                conn.commit()
                load_data()
                messagebox.showinfo("Success", "Class deleted successfully.")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot delete. Check if there are students still enrolled in this class.\n\nDetails: {e}")

    def edit_class():
        selected = tree_my.selection()
        if not selected: return
        malop = tree_my.item(selected[0], "values")[0]
        old_name = tree_my.item(selected[0], "values")[1]

        top = tk.Toplevel(parent)
        top.title("Edit Class Info")
        top.geometry("300x150")
        top.grab_set()

        tk.Label(top, text=f"Class ID: {malop}", font=("Arial", 10, "bold")).pack(pady=5)
        tk.Label(top, text="New Class Name:").pack()
        entry_name = tk.Entry(top, width=30)
        entry_name.insert(0, old_name)
        entry_name.pack(pady=5)

        def save():
            new_name = entry_name.get()
            try:
                conn = config.get_connection()
                cursor = conn.cursor()
                # Edit class name (Sử dụng SP)
                cursor.execute("EXEC SP_UPD_LOP ?, ?", (malop, new_name))
                conn.commit()
                load_data()
                top.destroy()
                messagebox.showinfo("Success", "Class information updated.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(top, text="Save Changes", command=save, bg="lightgreen").pack(pady=10)

    # --- Điều hướng sang Quản lý sinh viên & Nhập điểm ---
    def go_manage_students():
        selected = tree_my.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an ASSIGNED class to manage students!")
            return
        malop = tree_my.item(selected[0], "values")[0]
        app_controller.show_student_panel(malop)

    def go_enter_scores():
        selected = tree_my.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an ASSIGNED class to enter scores!")
            return
        malop = tree_my.item(selected[0], "values")[0]
        app_controller.show_score_panel(malop)

    # --- Bố cục các nút bấm ---
    
    # 1. Bảng nút cho "My Assigned Classes"
    btn_frame_my = tk.Frame(left_frame)
    btn_frame_my.pack(fill=tk.X, pady=10, padx=10)
    
    for i in range(3):
        btn_frame_my.grid_columnconfigure(i, weight=1)

    tk.Button(btn_frame_my, text="View Details", command=lambda: view_class(tree_my), width=15).grid(row=0, column=0, padx=5, pady=5)
    tk.Button(btn_frame_my, text="Edit Class", command=edit_class, width=15).grid(row=0, column=1, padx=5, pady=5)
    tk.Button(btn_frame_my, text="Manage Students", command=go_manage_students, width=15, bg="#d9edf7").grid(row=0, column=2, padx=5, pady=5)

    tk.Button(btn_frame_my, text="Unassign", command=remove_from_management, width=15).grid(row=1, column=0, padx=5, pady=5)
    tk.Button(btn_frame_my, text="Delete from DB", command=delete_class_db, width=15, fg="red").grid(row=1, column=1, padx=5, pady=5)
    tk.Button(btn_frame_my, text="Enter Grades", command=go_enter_scores, width=15, bg="#dff0d8").grid(row=1, column=2, padx=5, pady=5)

    # 2. Bảng nút cho "Other Classes"
    btn_frame_other = tk.Frame(right_frame)
    btn_frame_other.pack(fill=tk.X, pady=10, padx=10)
    
    tk.Button(btn_frame_other, text="View Details", command=lambda: view_class(tree_other), width=15).pack(side=tk.LEFT, padx=5)
    tk.Button(btn_frame_other, text="Assign to Me", command=add_to_management, width=15
              ).pack(side=tk.LEFT, padx=5)

    return main_frame