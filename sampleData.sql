USE QLSVNhom
GO

-- 1. Sample Data NHANVIEN
EXEC SP_INS_PUBLIC_NHANVIEN 
    @MANV = 'NV01', 
    @HOTEN = N'Nguyễn A', 
    @EMAIL = 'nva@hcmus.edu.vn', 
    @LUONGCB = 3000000, 
    @TENDN = 'nva', 
    @MK = 'abcd12';

EXEC SP_INS_PUBLIC_NHANVIEN 
    @MANV = 'NV02', 
    @HOTEN = N'Trần Thị B', 
    @EMAIL = 'ttb@hcmus.edu.vn', 
    @LUONGCB = 4000000, 
    @TENDN = 'ttb', 
    @MK = 'abcd12';
GO

-- 2. Sample Data LOP
INSERT INTO LOP (MALOP, TENLOP, MANV)
VALUES
('K21HTTT', N'Hệ thống thông tin K21', 'NV01'),
('K21KHMT', N'Khoa học máy tính K21', 'NV02');
GO

-- 3. Sample Data SINHVIEN
INSERT INTO SINHVIEN (MASV, HOTEN, NGAYSINH, DIACHI, MALOP, TENDN, MATKHAU)
VALUES
('SV01', N'Lê Minh C', '2003-05-15', N'TP.HCM', 'K21HTTT', 'lmc', CONVERT(VARBINARY, 'pass123')),
('SV02', N'Phạm Thu D', '2003-08-20', N'Đồng Nai', 'K21HTTT', 'ptd', CONVERT(VARBINARY, 'pass456')),
('SV03', N'Võ Tấn E', '2003-12-10', N'Bình Dương', 'K21KHMT', 'vte', CONVERT(VARBINARY, 'pass789'));
GO

-- 4. Sample Data HOCPHAN
INSERT INTO HOCPHAN (MAHP, TENHP, SOTC)
VALUES
('HP01', N'An toàn cơ sở dữ liệu', 4),
('HP02', N'Hệ điều hành', 4),
('HP03', N'Lập trình Java', 3);
GO