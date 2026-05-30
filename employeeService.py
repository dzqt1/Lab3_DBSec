import config
import pyodbc
import math
import random
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def is_prime_miller_rabin(n, k=20):
    """Kiểm tra số nguyên tố bằng Miller-Rabin"""
    if n == 2 or n == 3: return True
    if n % 2 == 0 or n < 2: return False
    
    r, d = 0, n - 1
    while d % 2 == 0:
        r += 1
        d //= 2
        
    for _ in range(k):
        a = random.randrange(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(r - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def get_deterministic_prime(bits):

    # Sinh số ngẫu nhiên có độ dài bits và đảm bảo bit cao nhất là 1 để đạt đủ độ dài
    candidate = random.getrandbits(bits)
    candidate |= (1 << bits - 1) | 1

    while not is_prime_miller_rabin(candidate):
        candidate += 2
    return candidate

def generate_rsa_keys(mk, key_size=2048):

    # Tạo seed từ mk
    mk_bytes = mk.encode('utf-8')
    seed_hash = hashlib.sha256(mk_bytes).digest()
    seed_int = int.from_bytes(seed_hash, byteorder='big')

    # Gán seed cho hàm random
    random.seed(seed_int)

    prime_size = key_size // 2

    p = get_deterministic_prime(prime_size)
    q = get_deterministic_prime(prime_size)
    while q == p:
        q = get_deterministic_prime(prime_size)

    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    d = pow(e, -1, phi)

    return (n, e), (n, d)

def export_public_key(n, e, manv):
    public_numbers = rsa.RSAPublicNumbers(e, n)
    standard_public_key = public_numbers.public_key()

    pem_bytes = standard_public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    path = "./pem/"
    file_name = f"{path}PUB_{manv}.pem"

    with open(file_name, 'wb') as f:
        f.write(pem_bytes)
    
    return file_name

def load_public_key(pub):
    file_name = f"./pem/{pub}.pem"
    with open(file_name, 'rb') as f:
        pem_data = f.read()
    
    public_key = serialization.load_pem_public_key(pem_data)
    public_numbers = public_key.public_numbers()
    return (public_numbers.n, public_numbers.e)
    
def encrypt_salary(salary, public_key):
    n, e = public_key
    salary_int = int.from_bytes(salary.encode('utf-8'), byteorder='big')
    encrypted_int = pow(salary_int, e, n)
    return encrypted_int.to_bytes((encrypted_int.bit_length() + 7) // 8, byteorder='big')

def decrypt_salary(encrypted_salary, mk):
    public_key, private_key = generate_rsa_keys(mk)
    n, d = private_key
    encrypted_int = int.from_bytes(encrypted_salary, byteorder='big')
    decrypted_int = pow(encrypted_int, d, n)
    decrypted_bytes = decrypted_int.to_bytes((decrypted_int.bit_length() + 7) // 8, byteorder='big')
    return decrypted_bytes.decode('utf-8')

def encrypt_score(score: float, public_key):
    n, e = public_key
    score_str = f"{score:.2f}"
    score_int = int.from_bytes(score_str.encode('utf-8'), byteorder='big')
    encrypted_int = pow(score_int, e, n)
    return encrypted_int.to_bytes((encrypted_int.bit_length() + 7) // 8, byteorder='big')

def decrypt_score(encrypted_score, mk):
    public_key, private_key = generate_rsa_keys(mk)
    n, d = private_key
    encrypted_int = int.from_bytes(encrypted_score, byteorder='big')
    decrypted_int = pow(encrypted_int, d, n)
    decrypted_bytes = decrypted_int.to_bytes((decrypted_int.bit_length() + 7) // 8, byteorder='big')
    return float(decrypted_bytes.decode('utf-8'))
    
def create_employee(manv, hoten, email, tendn, mk, luong):
    try:
        conn = pyodbc.connect(config.CONNECTION_STRING)
        cursor = conn.cursor()
        
        # 1. Sinh khóa RSA và lưu file
        public_key, private_key = generate_rsa_keys(mk)
        export_public_key(public_key[0], public_key[1], manv)
        
        # 2. Băm mật khẩu (SHA1)
        mk_hashed = hashlib.sha1(mk.encode('utf-8')).digest()
        
        # 3. Mã hóa lương ngay bằng Public Key vừa sinh ra
        encrypted_salary = encrypt_salary(str(luong), public_key)

        # 4. Lưu tất cả vào CSDL (Gọi SP đúng chuẩn của đề bài yêu cầu)
        cursor.execute("EXEC SP_INS_PUBLIC_ENCRYPT_NHANVIEN ?, ?, ?, ?, ?, ?, ?", 
                       manv, hoten, email, bytearray(encrypted_salary), tendn, bytearray(mk_hashed), f"PUB_{manv}")
        conn.commit()
    except Exception as e:
        print(f"Error saving employee: {e}")
        raise e  # Ném lỗi ra để màn hình giao diện (UI) bắt được và hiện thông báo
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def get_employee(tendn, mk):
    try:
        conn = pyodbc.connect(config.CONNECTION_STRING)
        cursor = conn.cursor()

        cursor.execute("EXEC SP_SEL_PUBLIC_ENCRYPT_NHANVIEN ?, ?", tendn, mk)
        row = cursor.fetchone()
        if row:
            if row[3] is None:
                decrypted_salary = None
            else:
                decrypted_salary = decrypt_salary(row[3], mk)
            return {
                "MANV": row[0],
                "HOTEN": row[1],
                "EMAIL": row[2],
                "LUONGCB": decrypted_salary,
                "PUBKEY": row[4]
            }
        else:
            return None
    except Exception as e:
        print(f"Error retrieving employee: {e}")
        return None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def get_employee_by_manv(manv):
    try:
        conn = pyodbc.connect(config.CONNECTION_STRING)
        cursor = conn.cursor()

        cursor.execute("EXEC SP_SEL_PUBLIC_ENCRYPT_NHANVIEN_BY_MANV ?", manv)
        row = cursor.fetchone()
        if row:
            return {
                "MANV": row[0],
                "HOTEN": row[1],
                "EMAIL": row[2],
                "PUBKEY": row[3]
            }
        else: return None
    except Exception as e:
        print(f"Error retrieving employee by MANV: {e}")
        return None
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

def update_salary(manv, new_salary):
    employee = get_employee_by_manv(manv)
    pub = employee["PUBKEY"]
    try:
        conn = pyodbc.connect(config.CONNECTION_STRING)
        cursor = conn.cursor()

        public_key = load_public_key(pub)
        encrypted_salary = encrypt_salary(new_salary, public_key)

        cursor.execute("EXEC SP_UPD_PUBLIC_ENCRYPT_LUONG ?, ?", manv, encrypted_salary)
        conn.commit()
    except Exception as e:
        print(f"Error updating salary: {e}")
    finally:
        if 'cursor' in locals(): cursor.close()
        if 'conn' in locals(): conn.close()

''' 
-- FOR TESTING PURPOSES ONLY --

[Tạo nhân viên mới]
if __name__ == "__main__":
    manv = "TEST001"
    mk = "test123"
    hoten = "Test Employee 1"
    email = "test@example.com"
    tendn = "test1"
    create_employee(manv, hoten, email, tendn, mk)
    update_salary(manv, "15000000")
    employee = get_employee(tendn, mk)
    print(employee)

[Mã hóa và giải mã điểm số]
if __name__ == "__main__":
    score = 8.5
    mk = "test123"
    public_key, private_key = generate_rsa_keys(mk)
    encrypted_score = encrypt_score(score, public_key)
    decrypted_score = decrypt_score(encrypted_score, mk)
    print(f"Original Score: {score}")
    print(f"Encrypted Score: {encrypted_score}")
    print(f"Decrypted Score: {decrypted_score}")

'''

'''
** Các hàm sử dụng cho chương trình: **

Cho nhân viên:
- create_employee(manv, hoten, email, tendn, mk): Tạo nhân viên mới với thông tin đã cho.
- get_employee(tendn, mk): Lấy thông tin nhân viên theo TENDN và MK (bao gồm lương đã giải mã) -> Dùng cho nhân viên xem thông tin cá nhân

Cho admin:
- get_employee_by_manv(manv): Lấy thông tin nhân viên theo MANV (không bao gồm lương và mật khẩu) -> Dùng cho admin cập nhật lương
- update_salary(manv, new_salary): Cập nhật lương mới cho nhân viên. Lương sẽ được mã hóa trước khi lưu vào DB


** Các hàm hỗ trợ: **

Tạo khóa
- is_prime_miller_rabin(n, k=20): Kiểm tra n có phải là số nguyên tố hay không bằng thuật toán Miller-Rabin với k lần kiểm tra -> Dùng để sinh số nguyên tố cho RSA
- get_deterministic_prime(bits): Sinh một số nguyên tố có độ dài bits một cách xác định dựa trên seed được tạo từ mật khẩu -> Dùng để sinh p, q cho RSA
- generate_rsa_keys(mk, key_size=2048): Sinh cặp khóa RSA dựa trên seed là mk -> Dùng để tạo khóa công khai và riêng tư cho nhân viên

Lưu và load khóa công khai
- export_public_key(n, e, manv): Xuất khóa công khai ra file PEM với tên định dạng PUB_[MANV].pem -> Dùng để lưu khóa công khai của nhân viên
- load_public_key(pub): Tải khóa công khai từ file PEM dựa trên tên pub -> Dùng để lấy khóa công khai khi cần mã hóa lương

Mã hóa và giải mã lương
- encrypt_salary(salary, public_key): Mã hóa lương bằng khóa công khai
- decrypt_salary(encrypted_salary, mk): Giải mã lương bằng khóa riêng tư được sinh từ mk

Mã hóa và giải mã điểm số
- encrypt_score(score, public_key): Mã hóa điểm số bằng khóa công khai
- decrypt_score(encrypted_score, mk): Giải mã điểm số bằng khóa riêng tư được sinh từ mk

'''