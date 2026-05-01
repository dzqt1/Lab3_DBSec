USE QLSVNhom
GO

-- C. --

-- decrease compatibility_level to use RSA_512 --
alter database QLSVNhom set compatibility_level = 120;

-- 1. insert nv --
create procedure SP_INS_PUBLIC_NHANVIEN
	@MANV varchar(20),
	@HOTEN nvarchar(100),
	@EMAIL varchar(20),
	@LUONGCB int,
	@TENDN varchar(100),
	@MK varchar(20)
with encryption
as
begin
	begin try

		-- hash mk --
		declare @MK_HASHED varbinary(MAX) = HASHBYTES('SHA1', @MK);

		-- encrypt luong --
		declare @CreateKeySQL nvarchar(MAX) = '
			if exists (select * from sys.asymmetric_keys where name = ''' + @MANV + ''' )
			begin
				drop asymmetric key ' + QUOTENAME(@MANV) + '
			end
			create asymmetric key ' + QUOTENAME(@MANV) + '
			with ALGORITHM = RSA_512
			encryption by password = N''' + @MK + ''';
		';
		exec sp_executesql @CreateKeySQL
		declare @LUONG varbinary(MAX) = ENCRYPTBYASYMKEY(ASYMKEY_ID(@MANV), CONVERT(varchar(50), @LUONGCB));

		-- insert data --
		insert into NHANVIEN (MANV, HOTEN, EMAIL, LUONG, TENDN, MATKHAU, PUBKEY)
		values (@MANV, @HOTEN, @EMAIL, @LUONG, @TENDN, @MK_HASHED, @MANV);

		print 'Insert to NHANVIEN successfully'

	end try
	begin catch

		declare @ERROR nvarchar(4000) = ERROR_MESSAGE();
		print 'Error: ' + @ERROR;

	end catch
end

-- 2. select nv --
create procedure SP_SEL_PUBLIC_NHANVIEN
	@TENDN varchar(20),
	@MK varchar(20)
with encryption
as
begin
	declare @MK_Hashed varbinary(MAX) = HASHBYTES('SHA1', @MK);
	select nv.MANV, nv.HOTEN, nv.EMAIL,
		   CAST (
				CONVERT(varchar(50), 
					DECRYPTBYASYMKEY(ASYMKEY_ID(nv.MANV), nv.LUONG, CONVERT(nvarchar(50), @MK))
				)
		   as int) as LUONGCB
	from NHANVIEN nv
	where nv.TENDN = @TENDN and nv.MATKHAU = @MK_Hashed
end

-- D. --

-- 1. SP Login
CREATE PROCEDURE SP_LOGIN_NHANVIEN
    @MANV VARCHAR(20),
    @MATKHAU VARCHAR(100) 
AS
BEGIN
    SELECT MANV, HOTEN 
    FROM NHANVIEN 
    WHERE MANV = @MANV AND MATKHAU = HASHBYTES('SHA1', CONVERT(VARCHAR, @MATKHAU))
END
GO

-- 2. SP select class
CREATE PROCEDURE SP_SEL_LOP_BY_NV
    @MANV VARCHAR(20)
AS
BEGIN
    SELECT l.MALOP, l.TENLOP
    FROM LOP l 
    WHERE l.MANV = @MANV
END
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
end

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
end

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
end

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
end