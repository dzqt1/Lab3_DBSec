import pyodbc

CONNECTION_STRING = (
    r'DRIVER={SQL Server};'
    r'SERVER=DESKTOP-IST84F2\SQLEXPRESS;'
    r'DATABASE=QLSVNhom;'
    r'UID=qlsv;'
    r'PWD=123'
)

USE_MOCK = False
# ================= MOCK DATA =================
MOCK_STAFF = {
    "NVA": {"MATKHAU": "123", "MANV": "NV01", "TENDN": "Nguyễn Văn A"},
    "TTB": {"MATKHAU": "123", "MANV": "NV02", "TENDN": "Trần Thị B"}
}

MOCK_CLASS = [
    ("L01", "Công nghệ thông tin 1", "NV01"),
    ("L02", "Công nghệ phần mềm 1", "NV01"),
    ("L03", "Hệ thống thông tin 1", "NV02")
]

MOCK_STD = [
    ("SV01", "Lê Văn C", "L01"),
    ("SV02", "Phạm Thị D", "L01"),
    ("SV03", "Hoàng Văn E", "L02"),
    ("SV04", "Ngô Thị F", "L03")
]

MOCK_BANGDIEM = []


def get_connection():
    return pyodbc.connect(CONNECTION_STRING)