USE QLSVNhom;
GO

-- C. Cấu hình mức độ tương thích để dùng RSA_512
ALTER DATABASE QLSVNhom SET COMPATIBILITY_LEVEL = 120;
GO

-- 1. SP Chèn nhân viên có mã hóa lương bằng RSA
CREATE OR ALTER PROCEDURE SP_INS_PUBLIC_NHANVIEN
    @MANV varchar(20),
    @HOTEN nvarchar(100),
    @EMAIL varchar(20),
    @LUONGCB int,
    @TENDN varchar(100),
    @MK varchar(20)
WITH ENCRYPTION
AS
BEGIN
    BEGIN TRY
        -- Hash mật khẩu
        DECLARE @MK_HASHED varbinary(MAX) = HASHBYTES('SHA1', @MK);

        -- Tạo Asymmetric Key động cho từng nhân viên
        DECLARE @CreateKeySQL nvarchar(MAX) = '
            IF EXISTS (SELECT * FROM sys.asymmetric_keys WHERE name = ''' + @MANV + ''')
            BEGIN
                DROP ASYMMETRIC KEY ' + QUOTENAME(@MANV) + '
            END
            CREATE ASYMMETRIC KEY ' + QUOTENAME(@MANV) + '
            WITH ALGORITHM = RSA_512
            ENCRYPTION BY PASSWORD = N''' + @MK + ''';';
        
        EXEC sp_executesql @CreateKeySQL;

        -- Mã hóa lương
        DECLARE @LUONG varbinary(MAX) = ENCRYPTBYASYMKEY(ASYMKEY_ID(@MANV), CONVERT(varchar(50), @LUONGCB));

        -- Insert dữ liệu
        INSERT INTO NHANVIEN (MANV, HOTEN, EMAIL, LUONG, TENDN, MATKHAU, PUBKEY)
        VALUES (@MANV, @HOTEN, @EMAIL, @LUONG, @TENDN, @MK_HASHED, @MANV);

        PRINT 'Insert to NHANVIEN successfully';
    END TRY
    BEGIN CATCH
        DECLARE @ERROR nvarchar(4000) = ERROR_MESSAGE();
        PRINT 'Error: ' + @ERROR;
    END CATCH
END;
GO

-- 2. SP Lấy thông tin nhân viên (Giải mã lương)
CREATE OR ALTER PROCEDURE SP_SEL_PUBLIC_NHANVIEN
    @TENDN varchar(20),
    @MK varchar(20)
WITH ENCRYPTION
AS
BEGIN
    DECLARE @MK_Hashed_Login varbinary(MAX) = HASHBYTES('SHA1', @MK);
    
    SELECT nv.MANV, nv.HOTEN, nv.EMAIL,
           CAST(
                CONVERT(varchar(50), 
                    DECRYPTBYASYMKEY(ASYMKEY_ID(nv.MANV), nv.LUONG, CONVERT(nvarchar(50), @MK))
                )
           AS int) AS LUONGCB
    FROM NHANVIEN nv
    WHERE nv.TENDN = @TENDN AND nv.MATKHAU = @MK_Hashed_Login;
END;
GO

-- D. 1. SP Login
CREATE OR ALTER PROCEDURE SP_LOGIN_NHANVIEN
    @MANV VARCHAR(20),
    @MATKHAU VARCHAR(100) 
AS
BEGIN
    SELECT MANV, HOTEN 
    FROM NHANVIEN 
    WHERE MANV = @MANV AND MATKHAU = HASHBYTES('SHA1', CONVERT(VARCHAR, @MATKHAU));
END;
GO

-- 2. SP Select Class
CREATE PROCEDURE SP_SEL_LOP_BY_NV
    @MANV VARCHAR(20)
AS
BEGIN
    SELECT l.MALOP, l.TENLOP
    FROM LOP l 
    WHERE l.MANV = @MANV;
END;
GO

CREATE PROCEDURE SP_SEL_LOP_OTHER
    @MANV VARCHAR(20)
WITH ENCRYPTION
AS
BEGIN
    SELECT MALOP, TENLOP 
    FROM LOP 
    WHERE MANV IS NULL OR MANV != @MANV;
END;
GO

CREATE OR ALTER PROCEDURE SP_ASSIGN_LOP
    @MANV VARCHAR(20),
    @MALOP VARCHAR(20)
WITH ENCRYPTION
AS
BEGIN
    UPDATE LOP 
    SET MANV = @MANV 
    WHERE MALOP = @MALOP;
END;
GO

CREATE OR ALTER PROCEDURE SP_UNASSIGN_LOP
    @MALOP VARCHAR(20)
WITH ENCRYPTION
AS
BEGIN
    UPDATE LOP 
    SET MANV = NULL 
    WHERE MALOP = @MALOP;
END;
GO

CREATE PROCEDURE SP_DEL_LOP
    @MALOP VARCHAR(20)
WITH ENCRYPTION
AS
BEGIN
    DELETE FROM LOP 
    WHERE MALOP = @MALOP;
END;
GO

-- 3. SP select student
create procedure SP_SEL_SV_BY_LOP
	@MALOP varchar(20)
with encryption
as
begin
	select sv.MASV, sv.HOTEN, sv.NGAYSINH, sv.DIACHI
	from SINHVIEN sv
	where sv.MALOP = @MALOP
end;
go



-- 4. SP add student
create procedure SP_INS_SINHVIEN
    @MASV varchar(20),
    @HOTEN nvarchar(100),
    @NGAYSINH datetime,
    @DIACHI nvarchar(200),
    @MALOP varchar(20),
    @TENDN varchar(100),
    @MK varchar(20)
with encryption
as
begin
    begin try

        -- hash mk --
        declare @MK_HASHED varbinary(MAX) = HASHBYTES('SHA1', @MK);

        -- insert data --
        insert into SINHVIEN (MASV, HOTEN, NGAYSINH, DIACHI, MALOP, TENDN, MATKHAU)
        values (@MASV, @HOTEN, @NGAYSINH, @DIACHI, @MALOP, @TENDN, @MK_HASHED);

        print 'Insert to SINHVIEN successfully'

    end try
    begin catch

        declare @ERROR nvarchar(4000) = ERROR_MESSAGE();
        print 'Error: ' + @ERROR;

    end catch
end;
go

-- 5. SP delete student
create procedure SP_DEL_SINHVIEN
	@MASV varchar(20)
with encryption
as
begin
	begin try

		delete from SINHVIEN where MASV = @MASV;

		print 'Delete student successfully'

	end try
	begin catch

		declare @ERROR nvarchar(4000) = ERROR_MESSAGE();
		print 'Error: ' + @ERROR;

	end catch
end;
go

-- 6. SP update student
create procedure SP_UPD_SINHVIEN
	@MASV varchar(20),
	@HOTEN nvarchar(100),
	@NGAYSINH datetime,
	@DIACHI nvarchar(200)
with encryption
as
begin
	begin try

		update SINHVIEN 
		set HOTEN = @HOTEN, NGAYSINH = @NGAYSINH, DIACHI = @DIACHI
		where MASV = @MASV;

		print 'Update student successfully'

	end try
	begin catch

		declare @ERROR nvarchar(4000) = ERROR_MESSAGE();
		print 'Error: ' + @ERROR;

	end catch
end;
go

-- 7. SP insert score
create procedure SP_INS_DIEM
	@MASV varchar(20),
	@MONHOC varchar(50),
	@DIEM float,
	@PUBKEY varchar(20)
with encryption
as
begin
	begin try
		declare @DIEM_ENCRYPTED varbinary(MAX) = ENCRYPTBYASYMKEY(ASYMKEY_ID(@PUBKEY), CONVERT(varchar(50), @DIEM));
		insert into BANGDIEM (MASV, MAHP, DIEMTHI) values (@MASV, @MONHOC, @DIEM_ENCRYPTED);

		print 'Insert score successfully'

	end try
	begin catch

		declare @ERROR nvarchar(4000) = ERROR_MESSAGE();
		print 'Error: ' + @ERROR;

	end catch
end;

-- 8. SP select score
create procedure SP_SEL_DIEM_BY_SV
	@MASV varchar(20),
	@PUBKEY varchar(20),
	@MK nvarchar(50)
with encryption
as
begin
	select MAHP, 
	CAST(
		CONVERT(varchar(50), 
			DECRYPTBYASYMKEY(ASYMKEY_ID(@PUBKEY), DIEMTHI, @MK)
		)
	AS float) AS DIEMTHI
	from BANGDIEM
	where MASV = @MASV
end;