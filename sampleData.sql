USE QLSVNhom
GO

-- Xóa dữ liệu cũ (Ngoại trừ NHANVIEN đã tạo bằng Python) để tránh lỗi trùng lặp khi chạy nhiều lần
DELETE FROM BANGDIEM;
DELETE FROM HOCPHAN;
DELETE FROM SINHVIEN;
DELETE FROM LOP;
GO

-- 1. Sample Data LOP
-- Admin không quản lý lớp nào, NV01 và NV02 quản lý lớp tương ứng
INSERT INTO LOP (MALOP, TENLOP, MANV)
VALUES
('K21HTTT', N'Hệ thống thông tin K21', 'NV01'),
('K21KHMT', N'Khoa học máy tính K21', 'NV02');
GO

-- 2. Sample Data SINHVIEN
-- Lưu ý: Mật khẩu ở đây được băm SHA1 trực tiếp để giả lập hành vi băm từ hệ thống
INSERT INTO SINHVIEN (MASV, HOTEN, NGAYSINH, DIACHI, MALOP, TENDN, MATKHAU)
VALUES
('SV01', N'Lê Minh C', '2003-05-15', N'TP.HCM', 'K21HTTT', 'lmc', HASHBYTES('SHA1', 'pass123')),
('SV02', N'Phạm Thu D', '2003-08-20', N'Đồng Nai', 'K21HTTT', 'ptd', HASHBYTES('SHA1', 'pass456')),
('SV03', N'Võ Tấn E', '2003-12-10', N'Bình Dương', 'K21KHMT', 'vte', HASHBYTES('SHA1', 'pass789'));
GO

-- 3. Sample Data HOCPHAN
INSERT INTO HOCPHAN (MAHP, TENHP, SOTC)
VALUES
('HP01', N'An toàn cơ sở dữ liệu', 4),
('HP02', N'Hệ điều hành', 4),
('HP03', N'Lập trình Java', 3);
GO