import tkinter as tk
from tkinter import messagebox
import config
import dashboard
import pyodbc

def login():
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
        conn = get_connection()
        cursor = conn.cursor()
        sql = "EXEC SP_SEL_PUBLIC_NHANVIEN ?, ?"
        cursor.execute(sql, (username, password))

        result = cursor.fetchone()

        if result[0] != None:
            print(result)
            messagebox.showinfo("Success", "Login successful!")
            root.destroy()
            dashboard.open(manv, password)
        else:
            messagebox.showerror("Error", "Invalid username or password.")

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

root = tk.Tk()
root.title("Login")
root.geometry("300x200")
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

login_button = tk.Button(root, text="Login", width=10, command=login)
login_button.pack(pady=10)

root.mainloop()