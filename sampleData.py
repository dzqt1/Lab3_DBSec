import employeeService
import os

def init_data():
    # Đảm bảo thư mục lưu khóa tồn tại
    if not os.path.exists("./pem"):
        os.makedirs("./pem")

    print("Đang tạo nhân viên và sinh khóa RSA (file .pem)...")
    
    # 1. Tạo nhân viên Admin theo yêu cầu
    employeeService.create_employee("ADMIN", "Quản trị viên", "admin@hcmus.edu.vn", "admin", "abcd12", 0)
    employeeService.update_salary("ADMIN", "15000000") # Cập nhật và mã hóa lương
    
    # 2. Tạo nhân viên NV01
    employeeService.create_employee("NV01", "Nguyễn Văn A", "nva@hcmus.edu.vn", "nva", "abcd12", "5000000")
    employeeService.update_salary("NV01", "3000000")
    
    # 3. Tạo nhân viên NV02
    employeeService.create_employee("NV02", "Trần Thị B", "ttb@hcmus.edu.vn", "ttb", "abcd12", "5000000")
    employeeService.update_salary("NV02", "4000000")
    
    print("Khởi tạo nhân viên thành công! Vui lòng kiểm tra thư mục 'pem/'.")

if __name__ == "__main__":
    init_data()