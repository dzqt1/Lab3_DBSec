import tkinter as tk
import classManagement
import studentManagement
#import scoreManagement

class Dashboard(tk.Tk):
    def __init__(self, manv, raw_password):
        super().__init__()
        self.title("Staff Dashboard")
        self.geometry("1000x600")
        self.eval('tk::PlaceWindow . center')
        self.manv = manv

        # Header
        header_frame = tk.Frame(self, bg="lightblue", height=40)
        header_frame.pack(fill=tk.X)
        tk.Label(header_frame, text=f"Staff ID: {manv}", bg="lightblue", font=("Arial", 10, "bold")).pack(pady=10)

        # Container Frame to hold all panels
        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        # Show initial panel
        self.show_class_panel()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    def show_class_panel(self):
        self.clear_container()
        classManagement.panel(self.container, self.manv, self)

    def show_student_panel(self, malop):
        self.clear_container()
        studentManagement.panel(self.container, self.manv, malop, self)

    #def show_score_panel(self, malop):
    #    self.clear_container()
    #    scoreManagement.panel(self.container, self.manv, malop, self)

def open(manv, raw_password):
    app = Dashboard(manv, raw_password)
    app.mainloop()