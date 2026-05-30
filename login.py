import tkinter as tk
from tkinter import messagebox
import config
import dashboard
import adminDashboard
import pyodbc
import employeeService as es

def login(entry_username, entry_password, root):
    username = entry_username.get()
    password = entry_password.get()

    if not username or not password:
        messagebox.showerror("Error", "Please enter both username and password.")
        return
    
    if config.USE_MOCK:
        user = config.MOCK_STAFF.get(username)
        if user and user["MATKHAU"] == password:
            messagebox.showinfo("Success", "Login successful!")
            root.destroy()
            dashboard.open(user["MANV"], password)
        else:
            messagebox.showerror("Error", "Invalid username or password.")
        return
    
    try:
        employee = es.get_employee(username, password)
        if employee:
            messagebox.showinfo("Success", "Login successful!")
            root.destroy()
            if employee["MANV"].upper() == "ADMIN":
                adminDashboard.open_admin(employee["MANV"])
            else:
                dashboard.open(employee["MANV"], password)
        else:
            messagebox.showerror("Error", "Invalid username or password.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

def open():
    global root, entry_username, entry_password
    root = tk.Tk()
    root.title("Login")
    root.geometry("300x250")
    root.eval('tk::PlaceWindow . center')

    lbl_title = tk.Label(root, text="Login", font=("Arial", 16))
    lbl_title.pack(pady=5)

    frame = tk.Frame(root)
    frame.pack(pady=5)

    lbl_username = tk.Label(frame, text="Username:")
    lbl_username.grid(row=0, column=0, padx=5, pady=10, sticky="e")
    entry_username = tk.Entry(frame)
    entry_username.grid(row=0, column=1, padx=5, pady=10)

    lbl_password = tk.Label(frame, text="Password:")
    lbl_password.grid(row=1, column=0, padx=5, pady=10, sticky="e")
    entry_password = tk.Entry(frame, show="*")
    entry_password.grid(row=1, column=1, padx=5, pady=10)
    login_button = tk.Button(root, text="Login", width=10, command=lambda: login(entry_username, entry_password, root))    
    login_button.pack(pady=10)
    register_button = tk.Button(root, text="Register", width=10, command=lambda: [root.destroy(), __import__("register").open()])
    register_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    open()
