import tkinter as tk
from tkinter import ttk
import classManagement
import studentManagement
import scoreManagement

def open(manv, raw_password):
    dash = tk.Tk()
    dash.title("Staff Dashboard")
    dash.geometry("700x500")
    dash.eval('tk::PlaceWindow . center')
    
    #Header
    header_frame = tk.Frame(dash, bg="lightblue", height=40)
    header_frame.pack(fill=tk.X)
    tk.Label(header_frame, text=f"Staff ID: {manv}", bg="lightblue").pack(pady=10)
    
    notebook = ttk.Notebook(dash)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    tab_class = classManagement.panel(notebook, manv)
    tab_std =  studentManagement.panel(notebook, manv)
    tab_score = scoreManagement.panel(notebook, manv)
    
    notebook.add(tab_class, text = "1. Class Management")
    notebook.add(tab_std, text = "2. Student Management")
    notebook.add(tab_score, text = "3. Score Management")

    dash.mainloop()