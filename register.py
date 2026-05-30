import tkinter as tk
from tkinter import messagebox
import employeeService as es
import login

def register():
    manv = entry_manv.get()
    username = entry_username.get()
    password = entry_password.get()
    confirm_password = entry_confirmPassword.get()
    fullname = entry_fullname.get()
    email = entry_email.get()

    if not manv or not username or not password or not confirm_password or not fullname or not email:
        messagebox.showerror("Error", "Please fill in all fields.")
        return

    if password != confirm_password:
        messagebox.showerror("Error", "Passwords do not match.")
        return
    
    try:
        es.create_employee(manv, fullname, email, username, password)
        messagebox.showinfo("Success", "Registration successful! You can now log in.")
        root.destroy()
        login.open()
    except Exception as e:
        messagebox.showerror("Error", f"Registration failed: {e}")

def open():
    global root, entry_manv, entry_username, entry_password, entry_confirmPassword, entry_fullname, entry_email
    root = tk.Tk()
    root.title("Registration")
    root.geometry("300x400")
    root.eval('tk::PlaceWindow . center')

    lbl_title = tk.Label(root, text="Registration", font=("Arial", 16))
    lbl_title.pack(pady=5)

    frame = tk.Frame(root)
    frame.pack(pady=5)

    lbl_manv = tk.Label(frame, text="Employee ID:")
    lbl_manv.grid(row=0, column=0, padx=5, pady=10, sticky="e")
    entry_manv = tk.Entry(frame)
    entry_manv.grid(row=0, column=1, padx=5, pady=10)

    lbl_username = tk.Label(frame, text="Username:")
    lbl_username.grid(row=1, column=0, padx=5, pady=10, sticky="e")
    entry_username = tk.Entry(frame)
    entry_username.grid(row=1, column=1, padx=5, pady=10)

    lbl_password = tk.Label(frame, text="Password:")
    lbl_password.grid(row=2, column=0, padx=5, pady=10, sticky="e")
    entry_password = tk.Entry(frame, show="*")
    entry_password.grid(row=2, column=1, padx=5, pady=10)

    lbl_confirmPassword = tk.Label(frame, text="Confirm Password:")
    lbl_confirmPassword.grid(row=3, column=0, padx=5, pady=10, sticky="e")
    entry_confirmPassword = tk.Entry(frame, show="*")
    entry_confirmPassword.grid(row=3, column=1, padx=5, pady=10)

    lbl_fullname = tk.Label(frame, text="Full Name:")
    lbl_fullname.grid(row=4, column=0, padx=5, pady=10, sticky="e")
    entry_fullname = tk.Entry(frame)
    entry_fullname.grid(row=4, column=1, padx=5, pady=10)

    lbl_email = tk.Label(frame, text="Email:")
    lbl_email.grid(row=5, column=0, padx=5, pady=10, sticky="e")
    entry_email = tk.Entry(frame)
    entry_email.grid(row=5, column=1, padx=5, pady=10)

    register_button = tk.Button(root, text="Register", width=15, command=register)
    register_button.pack(pady=10)

    login_button = tk.Button(root, text="Back to Login", width=15, command=lambda: [root.destroy(), login.open()])
    login_button.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    open()