-- =====================================================================
-- schema.sql  |  Bài tập lớn Công nghệ phần mềm - Đề tài 3: Quản lý nhà sách
-- Tạo CSDL + bảng + dữ liệu mẫu + tài khoản mẫu.
-- Chạy:  mysql -u root -p < schema.sql
-- Chạy lại được nhiều lần: các bảng của dự án sẽ bị xoá và tạo lại
-- (mất dữ liệu đã nhập thêm), CSDL khác trên máy không bị ảnh hưởng.
-- Yêu cầu: MySQL 8.0.16+ hoặc MariaDB 10.2+ (để ràng buộc CHECK có tác dụng).
-- =====================================================================

CREATE DATABASE IF NOT EXISTS nha_sach
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nha_sach;
SET NAMES utf8mb4;

-- Xoá bảng cũ theo thứ tự ngược với khoá ngoại
DROP TABLE IF EXISTS chi_tiet_don_hang;
DROP TABLE IF EXISTS don_hang;
DROP TABLE IF EXISTS chi_tiet_phieu_nhap;
DROP TABLE IF EXISTS phieu_nhap;
DROP TABLE IF EXISTS sach;
DROP TABLE IF EXISTS the_loai;
DROP TABLE IF EXISTS quy_dinh;
DROP TABLE IF EXISTS nguoi_dung;

-- ---------------------------------------------------------------------
-- 1. Người dùng (4 vai trò dùng chung một bảng)
-- ---------------------------------------------------------------------
CREATE TABLE nguoi_dung (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  ten_dang_nhap VARCHAR(50)  NOT NULL UNIQUE,
  mat_khau_hash VARCHAR(255) NOT NULL,           -- băm bằng werkzeug.security, KHÔNG lưu mật khẩu thô
  ho_ten        VARCHAR(100) NOT NULL,
  vai_tro       ENUM('KHACH','NHANVIEN','QUANLY','QUANTRI') NOT NULL
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 2. Quy định (YC5): 3 giá trị có thể sửa, KHÔNG viết cứng trong code
-- ---------------------------------------------------------------------
CREATE TABLE quy_dinh (
  ten     VARCHAR(50)  PRIMARY KEY,
  gia_tri INT          NOT NULL,
  mo_ta   VARCHAR(255) NULL,
  CONSTRAINT ck_quy_dinh_gia_tri CHECK (gia_tri >= 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 3. Thể loại, Sách (YC1, YC3, YC5)
-- ---------------------------------------------------------------------
CREATE TABLE the_loai (
  id  INT AUTO_INCREMENT PRIMARY KEY,
  ten VARCHAR(100) NOT NULL UNIQUE
) ENGINE=InnoDB;

CREATE TABLE sach (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  ma_vach      VARCHAR(13)  NOT NULL UNIQUE,     -- mã vạch cho máy quét (YC3)
  ten          VARCHAR(200) NOT NULL,
  the_loai_id  INT          NOT NULL,
  tac_gia      VARCHAR(100) NOT NULL,
  don_gia      INT          NOT NULL,            -- giá bán hiện tại (VND)
  so_luong_ton INT          NOT NULL DEFAULT 0,
  CONSTRAINT fk_sach_the_loai FOREIGN KEY (the_loai_id) REFERENCES the_loai(id),
  CONSTRAINT ck_sach_don_gia  CHECK (don_gia >= 0),
  CONSTRAINT ck_sach_ton      CHECK (so_luong_ton >= 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 4. Phiếu nhập sách (YC1)
--    Luật "nhập >= nhap_toi_thieu, tồn < nguong_ton_de_nhap" phụ thuộc bảng
--    quy_dinh nên kiểm tra trong code Flask, không đặt CHECK cố định ở đây.
-- ---------------------------------------------------------------------
CREATE TABLE phieu_nhap (
  id               INT AUTO_INCREMENT PRIMARY KEY,
  ngay_nhap        DATE NOT NULL,
  nguoi_quan_ly_id INT  NOT NULL,
  CONSTRAINT fk_pn_quan_ly FOREIGN KEY (nguoi_quan_ly_id) REFERENCES nguoi_dung(id)
) ENGINE=InnoDB;

CREATE TABLE chi_tiet_phieu_nhap (
  phieu_nhap_id INT NOT NULL,
  sach_id       INT NOT NULL,
  so_luong      INT NOT NULL,
  PRIMARY KEY (phieu_nhap_id, sach_id),
  CONSTRAINT fk_ctpn_phieu FOREIGN KEY (phieu_nhap_id) REFERENCES phieu_nhap(id) ON DELETE CASCADE,
  CONSTRAINT fk_ctpn_sach  FOREIGN KEY (sach_id)       REFERENCES sach(id),
  CONSTRAINT ck_ctpn_so_luong CHECK (so_luong > 0)
) ENGINE=InnoDB;

-- ---------------------------------------------------------------------
-- 5. Đơn hàng dùng chung cho đơn online (YC2) và hoá đơn tại quầy (YC3)
--    kenh         : ONLINE (khách đặt trên web) | QUAY (nhân viên bán tại quầy)
--    hinh_thuc_tt : TRUC_TIEP (trả tại nhà sách) | ONLINE (trả trước, giao miễn phí)
--    trang_thai   : CHO_LAY | HOAN_TAT | DA_HUY
--    han_lay_sach : chỉ có giá trị với đơn TRUC_TIEP đặt online; còn lại để NULL.
--    Tổng tiền KHÔNG lưu: tính bằng SUM(so_luong * don_gia) của chi_tiet_don_hang.
-- ---------------------------------------------------------------------
CREATE TABLE don_hang (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  kenh         ENUM('ONLINE','QUAY')            NOT NULL,
  khach_id     INT          NULL,               -- NULL nếu khách vãng lai mua tại quầy
  ten_khach    VARCHAR(100) NOT NULL,           -- "Họ tên khách hàng" trên hoá đơn
  nhan_vien_id INT          NULL,               -- "Nhân viên thanh toán"; NULL khi khách tự thanh toán online
  hinh_thuc_tt ENUM('TRUC_TIEP','ONLINE')       NOT NULL,
  trang_thai   ENUM('CHO_LAY','HOAN_TAT','DA_HUY') NOT NULL,
  ngay_tao     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- "Ngày lập hoá đơn" / giờ đặt
  han_lay_sach DATETIME NULL,
  CONSTRAINT fk_dh_khach     FOREIGN KEY (khach_id)     REFERENCES nguoi_dung(id),
  CONSTRAINT fk_dh_nhan_vien FOREIGN KEY (nhan_vien_id) REFERENCES nguoi_dung(id),
  CONSTRAINT ck_dh_han_lay   CHECK (hinh_thuc_tt = 'TRUC_TIEP' OR han_lay_sach IS NULL)
) ENGINE=InnoDB;
CREATE INDEX idx_don_hang_huy ON don_hang (trang_thai, han_lay_sach);
CREATE INDEX idx_don_hang_ngay ON don_hang (ngay_tao);

CREATE TABLE chi_tiet_don_hang (
  don_hang_id INT NOT NULL,
  sach_id     INT NOT NULL,
  so_luong    INT NOT NULL,
  don_gia     INT NOT NULL,                     -- CHỐT giá tại thời điểm bán, không lấy lại từ bảng sach
  PRIMARY KEY (don_hang_id, sach_id),
  CONSTRAINT fk_ctdh_don_hang FOREIGN KEY (don_hang_id) REFERENCES don_hang(id),
  CONSTRAINT fk_ctdh_sach     FOREIGN KEY (sach_id)     REFERENCES sach(id),
  CONSTRAINT ck_ctdh_so_luong CHECK (so_luong > 0),
  CONSTRAINT ck_ctdh_don_gia  CHECK (don_gia >= 0)
) ENGINE=InnoDB;


-- =====================================================================
-- DỮ LIỆU MẪU
-- =====================================================================

-- Tài khoản mẫu (mật khẩu của TẤT CẢ tài khoản: 123456)
INSERT INTO nguoi_dung (ten_dang_nhap, mat_khau_hash, ho_ten, vai_tro) VALUES
  ('quantri', 'pbkdf2:sha256:1000000$ZZ4wPO10qIa9Gd3E$7164e9d454e638b8b380d07d1c3a5d9d4da77235750d783a283c4a531727cc6f', 'Nguyễn Văn Quản Trị', 'QUANTRI'),
  ('quanly', 'pbkdf2:sha256:1000000$QxA8vD20ph8l4ERO$406b689c1c9273e346494f6e13b70b4073bdc45555910fa4301aab40acc157f5', 'Trần Thị Quản Lý', 'QUANLY'),
  ('nhanvien', 'pbkdf2:sha256:1000000$pPOs3bce9xS0jyek$ded72140e726b153d6982691453ddc887568aeb0a48a85f170472b3e607dc6bc', 'Lê Văn Bán Hàng', 'NHANVIEN'),
  ('khachhang', 'pbkdf2:sha256:1000000$hK4RaNYOoOusdVLC$c208c76897854a1b61cda40abed0a921304fdb381c2fdc87d194dd1962ddcefa', 'Phạm Thị Khách Hàng', 'KHACH'),
  ('khachhang2', 'pbkdf2:sha256:1000000$CfqiycapzFCHTrya$c15e1d6d2bbd81adf5f5c217f1253226ec87a1f645850f650abc265859b76006', 'Hoàng Văn Khách Hai', 'KHACH');

-- Quy định mặc định theo đề bài
INSERT INTO quy_dinh (ten, gia_tri, mo_ta) VALUES
  ('nhap_toi_thieu', 150, 'Số cuốn nhập tối thiểu cho mỗi đầu sách trong phiếu nhập'),
  ('nguong_ton_de_nhap', 300, 'Chỉ được nhập đầu sách có tồn kho ÍT HƠN mức này'),
  ('gio_huy_don', 48, 'Số giờ giữ đơn thanh toán trực tiếp; quá hạn mà khách chưa lấy sách thì tự huỷ');

-- 5 thể loại
INSERT INTO the_loai (ten) VALUES
  ('Văn học'),
  ('Thiếu nhi'),
  ('Kinh tế'),
  ('Kỹ năng sống'),
  ('Khoa học');

-- 20 đầu sách. Cố ý có đủ trường hợp để thử luật nhập sách:
--   tồn >= 300 (không được nhập): Mắt biếc 320, Dế Mèn 450, Cha giàu cha nghèo 500, Đắc nhân tâm 380, Nghĩ giàu và làm giàu 340
--   tồn = 300 (biên, KHÔNG được nhập): Truyện Kiều;  tồn = 299 (biên, được nhập): Tôi thấy hoa vàng trên cỏ xanh
--   tồn = 0 (hết hàng, thử báo lỗi khi bán/đặt): Vũ trụ (Cosmos)
-- Mã vạch là mã GIẢ (đúng dạng EAN-13) chỉ để thử máy quét/nhập tay.
INSERT INTO sach (ma_vach, ten, the_loai_id, tac_gia, don_gia, so_luong_ton) VALUES
  ('8936000000011', 'Mắt biếc', 1, 'Nguyễn Nhật Ánh', 95000, 320),
  ('8936000000028', 'Số đỏ', 1, 'Vũ Trọng Phụng', 68000, 150),
  ('8936000000035', 'Tắt đèn', 1, 'Ngô Tất Tố', 52000, 280),
  ('8936000000042', 'Truyện Kiều', 1, 'Nguyễn Du', 75000, 300),
  ('8936000000059', 'Dế Mèn phiêu lưu ký', 2, 'Tô Hoài', 62000, 450),
  ('8936000000066', 'Hoàng tử bé', 2, 'Antoine de Saint-Exupéry', 58000, 90),
  ('8936000000073', 'Kính vạn hoa', 2, 'Nguyễn Nhật Ánh', 85000, 40),
  ('8936000000080', 'Tôi thấy hoa vàng trên cỏ xanh', 2, 'Nguyễn Nhật Ánh', 98000, 299),
  ('8936000000097', 'Cha giàu cha nghèo', 3, 'Robert T. Kiyosaki', 89000, 500),
  ('8936000000103', 'Nhà đầu tư thông minh', 3, 'Benjamin Graham', 165000, 120),
  ('8936000000110', 'Từ tốt đến vĩ đại', 3, 'Jim Collins', 139000, 60),
  ('8936000000127', 'Khởi nghiệp tinh gọn', 3, 'Eric Ries', 128000, 210),
  ('8936000000134', 'Đắc nhân tâm', 4, 'Dale Carnegie', 86000, 380),
  ('8936000000141', '7 thói quen của người thành đạt', 4, 'Stephen R. Covey', 118000, 25),
  ('8936000000158', 'Atomic Habits - Thói quen nguyên tử', 4, 'James Clear', 145000, 175),
  ('8936000000165', 'Nghĩ giàu và làm giàu', 4, 'Napoleon Hill', 79000, 340),
  ('8936000000172', 'Lược sử thời gian', 5, 'Stephen Hawking', 110000, 70),
  ('8936000000189', 'Vũ trụ trong vỏ hạt dẻ', 5, 'Stephen Hawking', 125000, 15),
  ('8936000000196', 'Sapiens: Lược sử loài người', 5, 'Yuval Noah Harari', 189000, 260),
  ('8936000000202', 'Vũ trụ (Cosmos)', 5, 'Carl Sagan', 155000, 0);
