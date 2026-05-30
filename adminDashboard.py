import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import config
import pyodbc
import employeeService
import os

class AdminDashboard(tk.Tk):
    def __init__(self, manv):
        super().__init__()
        self.title("Admin Dashboard - Quản Lý Nhân Viên")
        self.geometry("900x500")
        self.eval('tk::PlaceWindow . center')
        self.manv = manv

        # Header
        header_frame = tk.Frame(self, bg="#ffc107", height=40)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text=f"WELCOME ADMIN: {manv}", bg="#ffc107", font=("Arial", 12, "bold")).pack(pady=10)

        # Treeview danh sách nhân viên
        self.tree = ttk.Treeview(self, columns=("MANV", "HOTEN", "EMAIL", "TENDN", "PUBKEY"), show='headings')
        self.tree.heading("MANV", text="Employee ID")
        self.tree.heading("HOTEN", text="Full Name")
        self.tree.heading("EMAIL", text="Email")
        self.tree.heading("TENDN", text="LOGIN NAME")
        self.tree.heading("PUBKEY", text="Public Key")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Nút chức năng
        btn_frame = tk.Frame(self)
        btn_frame.pack(pady=15)

        tk.Button(btn_frame, text="Add Employee", command=self.add_employee, width=15, bg="#d9edf7").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Remove Employee", command=self.delete_employee, width=15, bg="#f2dede").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="View Salary", command=self.view_salary, width=18, bg="#dff0d8").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Update Salary", command=self.update_salary, width=15, bg="#fcf8e3").pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="Log Out", command=self.logout, width=15).pack(side=tk.LEFT, padx=10)

        self.load_data()

    def load_data(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        try:
            conn = pyodbc.connect(config.CONNECTION_STRING)
            cursor = conn.cursor()
            cursor.execute("EXEC SP_GET_ALL_NHANVIEN")
            for row in cursor.fetchall():
                # Bỏ qua dòng của chính Admin
                if row[0] == "ADMIN": 
                    continue
                self.tree.insert("", tk.END, values=(row[0], row[1], row[2], row[3], row[4]))
        except Exception as e:
            messagebox.showerror("Database Error:", str(e))
        finally:
            if 'cursor' in locals(): cursor.close()
            if 'conn' in locals(): conn.close()

    def add_employee(self):
        # Tạo cửa sổ con mới
        dialog = tk.Toplevel(self)
        dialog.title("Thêm Nhân Viên Mới")
        dialog.geometry("450x450")
        dialog.transient(self) # Giữ cửa sổ này luôn ở trên cửa sổ chính
        dialog.grab_set()      # Chặn tương tác với cửa sổ chính cho đến khi đóng form

        # Tiêu đề Form
        tk.Label(dialog, text="ĐIỀN THÔNG TIN NHÂN VIÊN", font=("Arial", 14, "bold"), fg="#333").grid(row=0, column=0, columnspan=2, pady=15)

        # Định nghĩa các trường nhập liệu
        fields = ["Mã NV:", "Họ Tên:", "Email:", "Tên Đăng Nhập:", "Mật Khẩu:", "Lương Cơ Bản:"]
        entries = {}

        # Vòng lặp vẽ các Lable và Entry
        for i, field in enumerate(fields, start=1):
            tk.Label(dialog, text=field, font=("Arial", 11)).grid(row=i, column=0, padx=20, pady=10, sticky="e")
            entry = tk.Entry(dialog, width=30, font=("Arial", 11))
            
            # Ẩn ký tự nếu là mật khẩu
            if field == "Mật Khẩu:":
                entry.config(show="*")
                
            entry.grid(row=i, column=1, padx=10, pady=10)
            entries[field] = entry

        # Hàm xử lý khi bấm nút "Lưu"
        def on_submit():
            manv = entries["Mã NV:"].get().strip()
            hoten = entries["Họ Tên:"].get().strip()
            email = entries["Email:"].get().strip()
            tendn = entries["Tên Đăng Nhập:"].get().strip()
            mk = entries["Mật Khẩu:"].get()
            luong = entries["Lương Cơ Bản:"].get().strip()

            # Kiểm tra dữ liệu rỗng
            if not all([manv, hoten, tendn, mk, luong]):
                messagebox.showwarning("Thiếu thông tin", "Vui lòng điền đầy đủ các trường bắt buộc (bao gồm lương)!", parent=dialog)
                return
            
            # Kiểm tra lương phải là số
            if not luong.isdigit():
                messagebox.showwarning("Lỗi định dạng", "Lương cơ bản chỉ được chứa chữ số!", parent=dialog)
                return

            try:
                # Gọi hàm create_employee (đã được cập nhật ở Bước 1)
                employeeService.create_employee(manv, hoten, email, tendn, mk, luong)
                messagebox.showinfo("Thành công", f"Đã thêm nhân viên {manv} và mã hóa lương RSA thành công!", parent=dialog)
                self.load_data() # Tải lại bảng danh sách
                dialog.destroy() # Đóng cửa sổ Form
            except Exception as e:
                messagebox.showerror("Lỗi CSDL", f"Không thể thêm nhân viên:\n{str(e)}", parent=dialog)

        # Bố cục nút bấm
        btn_frame = tk.Frame(dialog)
        btn_frame.grid(row=len(fields)+1, column=0, columnspan=2, pady=25)
        
        tk.Button(btn_frame, text="Lưu Nhân Viên", command=on_submit, bg="#4CAF50", fg="white", font=("Arial", 11, "bold"), width=15).pack(side=tk.LEFT, padx=15)
        tk.Button(btn_frame, text="Hủy Bỏ", command=dialog.destroy, bg="#f44336", fg="white", font=("Arial", 11, "bold"), width=15).pack(side=tk.LEFT, padx=15)

    def delete_employee(self):
        selected = self.tree.selection()
        if not selected: return
        manv = self.tree.item(selected[0], "values")[0]
        pubkey = self.tree.item(selected[0], "values")[4]

        if messagebox.askyesno("Confirm", f"Delete {manv}?"):
            try:
                conn = pyodbc.connect(config.CONNECTION_STRING)
                cursor = conn.cursor()
                cursor.execute("EXEC SP_DEL_NHANVIEN ?", (manv,))
                conn.commit()
                
                # Xóa file PEM nếu tồn tại
                pem_path = f"./pem/{pubkey}.pem"
                if os.path.exists(pem_path):
                    os.remove(pem_path)

                messagebox.showinfo("Successfully", "Employee deleted.")
                self.load_data()
            except Exception as e:
                messagebox.showerror("Error: ", str(e))
            finally:
                if 'cursor' in locals(): cursor.close()
                if 'conn' in locals(): conn.close()

    def view_salary(self):
        selected = self.tree.selection()
        if not selected: return
        
        tendn = self.tree.item(selected[0], "values")[3]
        hoten = self.tree.item(selected[0], "values")[1]

        # Do không thể phục hồi mã băm SHA1, Admin phải biết mật khẩu để tạo Private Key
        mk = simpledialog.askstring("Decryption", f"Please enter password of {tendn} to see salary:", show="*")
        if not mk: return

        emp_data = employeeService.get_employee(tendn, mk)
        if emp_data:
            luong = emp_data.get("LUONGCB")
            messagebox.showinfo("Salary ", f"Employee: {hoten}\nSalary (decrypted): {luong} VND")
        else:
            messagebox.showerror("Decrypt Error: ", "Miss match password. The Private Key cannot be recreated to decrypt the salary.!")

    def update_salary(self):
        selected = self.tree.selection()
        if not selected: return
        
        manv = self.tree.item(selected[0], "values")[0]
        hoten = self.tree.item(selected[0], "values")[1]

        new_salary = simpledialog.askstring("Update Salary", f"Enter new salary for {hoten}:")
        if new_salary:
            # Hàm này tự load Public Key từ file PEM và mã hóa, không cần mật khẩu
            employeeService.update_salary(manv, new_salary)
            messagebox.showinfo("Successfully", "Salary updated.")
            self.load_data()

    def logout(self):
        self.destroy()
        # Mở lại màn hình login (Cần import lazy để tránh import vòng/circular import)
        import login
        login.open_login()

def open_admin(manv):
    app = AdminDashboard(manv)
    app.mainloop()