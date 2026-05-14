import sqlite3
import os
import re

class Student:
    def __init__(self, ten, tuoi_lop, toan, van, anh, student_id=None):
        self.id = student_id
        self.ten = ten
        self.tuoi_lop = tuoi_lop
        self.toan = toan
        self.van = van
        self.anh = anh
        self.dtb = self.tinh_dtb()
        self.xep_loai = self.tinh_xep_loai()

    def tinh_dtb(self):
        return round((self.toan + self.van + self.anh) / 3, 2)

    def tinh_xep_loai(self):
        if self.dtb >= 8.0: return "Giỏi"
        elif self.dtb >= 6.5: return "Khá"
        elif self.dtb >= 5.0: return "Trung bình"
        else: return "Yếu"

class DatabaseManager:
    def __init__(self, db_name='hoc_sinh.db'):
        thu_muc_code = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(thu_muc_code, db_name)
        self.tao_bang_neu_chua_co()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def tao_bang_neu_chua_co(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hoc_sinh (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ten TEXT, tuoi_lop TEXT, toan REAL, van REAL, anh REAL, dtb REAL, xep_loai TEXT
            )
        ''')
        conn.commit()
        conn.close()

    def luu_hoc_sinh(self, student):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO hoc_sinh (ten, tuoi_lop, toan, van, anh, dtb, xep_loai)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (student.ten, student.tuoi_lop, student.toan, student.van, student.anh, student.dtb, student.xep_loai))
        conn.commit()
        conn.close()

    def cap_nhat_hoc_sinh(self, student):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE hoc_sinh 
            SET ten=?, tuoi_lop=?, toan=?, van=?, anh=?, dtb=?, xep_loai=?
            WHERE id=?
        ''', (student.ten, student.tuoi_lop, student.toan, student.van, student.anh, student.dtb, student.xep_loai, student.id))
        conn.commit()
        conn.close()

    def xoa_hoc_sinh(self, student_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM hoc_sinh WHERE id=?', (student_id,))
        conn.commit()
        conn.close()

    def lay_danh_sach(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM hoc_sinh')
        rows = cursor.fetchall()
        conn.close()
        
        danh_sach = []
        for row in rows:
            hs = Student(row[1], row[2], row[3], row[4], row[5], student_id=row[0])
            danh_sach.append(hs)
        return danh_sach

class InputValidator:
    @staticmethod
    def nhap_khong_rong(prompt, mac_dinh=None):
        while True:
            gia_tri = input(prompt).strip()
            if gia_tri:
                return gia_tri
            if mac_dinh is not None:
                return mac_dinh
            print("Lỗi: Bạn không được để trống thông tin này!")

    @staticmethod
    def nhap_so_luong_hoc_sinh():
        while True:
            gia_tri = input("Nhập số lượng học sinh: ").strip()
            try:
                n = int(gia_tri)
                if n > 0: return n
                print("Lỗi: Số lượng học sinh phải lớn hơn 0!")
            except ValueError:
                print("Lỗi: Bạn phải nhập số nguyên dương (ví dụ 3)!")

    @staticmethod
    def nhap_diem(ten_mon, mac_dinh=None):
        while True:
            try:
                if mac_dinh is None:
                    gia_tri = input(f"Nhập điểm {ten_mon} (0-10): ").strip()
                else:
                    gia_tri = input(f"Nhập điểm {ten_mon} (0-10, Enter để giữ {mac_dinh}): ").strip()
                if gia_tri == "" and mac_dinh is not None:
                    return mac_dinh
                diem = float(gia_tri)
                if 0 <= diem <= 10:
                    return diem
                print("Lỗi: Điểm phải nằm trong khoảng từ 0 đến 10!")
            except ValueError:
                print("Lỗi: Bạn chưa nhập số. Hãy nhập một con số (ví dụ 8 hoặc 8.5)!")

    @staticmethod
    def nhap_tuoi_hoac_lop(mac_dinh=None):
        while True:
            if mac_dinh is None:
                gia_tri = input("Nhập tuổi hoặc lớp (ví dụ: 15, 10A1): ").strip()
            else:
                gia_tri = input(f"Nhập tuổi hoặc lớp (Enter để giữ '{mac_dinh}'): ").strip()
            if gia_tri == "" and mac_dinh is not None:
                return mac_dinh
            if gia_tri == "":
                print("Lỗi: Bạn không được để trống thông tin này!")
            elif gia_tri.isdigit(): 
                gia_tri_int = int(gia_tri)
                if 1 <= gia_tri_int <= 5:
                    return f"Lớp {gia_tri}"
                if 13 <= gia_tri_int <= 18:
                    return f"{gia_tri} tuổi"
                kieu = input(f"   => Số '{gia_tri}' này là Tuổi hay Lớp? (Gõ 'T' cho Tuổi, 'L' cho Lớp): ").strip().upper()
                if kieu == 'T':
                    tuoi = int(gia_tri)
                    if 6 <= tuoi <= 18: return f"{gia_tri} tuổi"
                    else: print("Lỗi: Tuổi học sinh đi học phải từ 6 đến 18!")
                elif kieu == 'L':
                    lop = int(gia_tri)
                    if 1 <= lop <= 12: return f"Lớp {gia_tri}"
                    else: print("Lỗi: Lớp học chỉ từ lớp 1 đến lớp 12!")
                else: print("Lỗi: Bạn phải gõ T hoặc L. Vui lòng nhập lại từ đầu!")
            else:
                try:
                    float(gia_tri)
                    print("Lỗi: Không được nhập số thập phân/số âm!")
                except ValueError:
                    cac_so = re.findall(r'\d+', gia_tri)
                    if cac_so:
                        khoi_lop = int(cac_so[0])
                        if 1 <= khoi_lop <= 12: return gia_tri
                        else: print("Lỗi: Lớp học chỉ từ lớp 1 đến lớp 12!")
                    else: print("Lỗi: Tên lớp không hợp lệ (Phải chứa số từ 1-12, ví dụ: 10A1, Lớp 9)!")

class StudentTrackerApp:
    def __init__(self):
        self.db = DatabaseManager()

    def nhap_hoc_sinh_moi(self):
        n = InputValidator.nhap_so_luong_hoc_sinh()
        so_luong_da_luu = 0
        for i in range(n):
            print(f"\n--- Nhập thông tin cho học sinh thứ {i+1} ---")
            ten = InputValidator.nhap_khong_rong("Nhập tên học sinh: ")
            tuoi_lop = InputValidator.nhap_tuoi_hoac_lop()
            toan = InputValidator.nhap_diem("Toán")
            van = InputValidator.nhap_diem("Văn")
            anh = InputValidator.nhap_diem("Anh")
            
            student = Student(ten, tuoi_lop, toan, van, anh)
            print(f"-> Điểm trung bình của {student.ten} là: {student.dtb} ({student.xep_loai})")
            
            self.db.luu_hoc_sinh(student)
            so_luong_da_luu += 1
            
        print(f"\nĐã lưu thành công {so_luong_da_luu} học sinh vào Database!")

    def hien_thi_danh_sach(self):
        danh_sach = self.db.lay_danh_sach()
        print("\n" + "="*50)
        print("DANH SÁCH HỌC SINH".center(50))
        print("="*50)
        if not danh_sach:
            print("Danh sách hiện đang trống!")
        else:
            for i, hs in enumerate(danh_sach):
                print(f"{i+1}. Tên: {hs.ten} | Tuổi/Lớp: {hs.tuoi_lop} | ĐTB: {hs.dtb} | Xếp loại: {hs.xep_loai}")
        print("="*50)

    def chon_hoc_sinh_theo_ten(self, danh_sach):
        if not danh_sach:
            print("Danh sách hiện đang trống!")
            return None

        ten_can_tim = InputValidator.nhap_khong_rong("Nhập tên học sinh cần chọn: ")
        chi_so_trung = [i for i, hs in enumerate(danh_sach) if hs.ten.lower() == ten_can_tim.lower()]

        if not chi_so_trung:
            print(f"Không tìm thấy học sinh nào tên là '{ten_can_tim}'.")
            return None

        if len(chi_so_trung) == 1:
            return chi_so_trung[0]

        print("\nTìm thấy nhiều học sinh trùng tên:")
        for stt, i in enumerate(chi_so_trung, start=1):
            hs = danh_sach[i]
            print(f"{stt}. Tên: {hs.ten} | Tuổi/Lớp: {hs.tuoi_lop} | ĐTB: {hs.dtb} | Xếp loại: {hs.xep_loai}")

        while True:
            chon = InputValidator.nhap_khong_rong("Chọn số thứ tự để thao tác: ")
            if chon.isdigit():
                vi_tri = int(chon) - 1
                if 0 <= vi_tri < len(chi_so_trung):
                    return chi_so_trung[vi_tri]
            print("Lỗi: Vui lòng chọn đúng số thứ tự trong danh sách trên!")

    def tim_kiem_hoc_sinh(self):
        danh_sach = self.db.lay_danh_sach()
        print("\n--- TÌM KIẾM HỌC SINH ---")
        ten_can_tim = InputValidator.nhap_khong_rong("Nhập tên hoặc một phần tên học sinh cần tìm: ")
        da_tim_thay = False
        
        for hs in danh_sach:
            if ten_can_tim.lower() in hs.ten.lower():
                print("\n>>> Đã tìm thấy học sinh:")
                print(f"- Tên: {hs.ten}")
                print(f"- Tuổi/Lớp: {hs.tuoi_lop}")
                print(f"- Điểm Toán: {hs.toan}, Văn: {hs.van}, Anh: {hs.anh}")
                print(f"- Điểm trung bình: {hs.dtb} ({hs.xep_loai})")
                da_tim_thay = True
                
        if not da_tim_thay:
            print(f"\nKhông tìm thấy học sinh nào tên là '{ten_can_tim}'.")

    def sua_hoc_sinh(self):
        danh_sach = self.db.lay_danh_sach()
        print("\n--- SỬA THÔNG TIN HỌC SINH ---")
        chi_so = self.chon_hoc_sinh_theo_ten(danh_sach)
        if chi_so is None:
            return

        hs_cu = danh_sach[chi_so]
        
        print(f"Nhập thông tin mới cho học sinh '{hs_cu.ten}' (Enter để giữ nguyên):")
        ten = InputValidator.nhap_khong_rong(
            f"Nhập tên học sinh (Enter để giữ '{hs_cu.ten}'): ",
            mac_dinh=hs_cu.ten
        )
        tuoi_lop = InputValidator.nhap_tuoi_hoac_lop(mac_dinh=hs_cu.tuoi_lop)
        toan = InputValidator.nhap_diem("Toán", mac_dinh=hs_cu.toan)
        van = InputValidator.nhap_diem("Văn", mac_dinh=hs_cu.van)
        anh = InputValidator.nhap_diem("Anh", mac_dinh=hs_cu.anh)

        hs_moi = Student(ten, tuoi_lop, toan, van, anh, student_id=hs_cu.id)
        self.db.cap_nhat_hoc_sinh(hs_moi)
        print("Đã cập nhật thông tin học sinh vào Database.")

    def xoa_hoc_sinh(self):
        danh_sach = self.db.lay_danh_sach()
        print("\n--- XÓA HỌC SINH ---")
        chi_so = self.chon_hoc_sinh_theo_ten(danh_sach)
        if chi_so is None:
            return

        hs = danh_sach[chi_so]
        xac_nhan = InputValidator.nhap_khong_rong(f"Bạn có chắc muốn xóa '{hs.ten}'? (Y/N): ").strip().upper()
        if xac_nhan == "Y":
            self.db.xoa_hoc_sinh(hs.id)
            print("Đã xóa học sinh khỏi Database.")
        else:
            print("Đã hủy thao tác xóa.")

    def hien_thi_menu(self):
        print("\n" + "="*40)
        print("PHẦN MỀM QUẢN LÝ HỌC SINH".center(40))
        print("="*40)
        print("1. Thêm học sinh mới")
        print("2. Hiển thị danh sách")
        print("3. Tìm kiếm học sinh theo tên")
        print("4. Sửa thông tin học sinh")
        print("5. Xóa học sinh")
        print("6. Thoát chương trình")
        print("="*40)

    def run(self):
        while True:
            self.hien_thi_menu()
            lua_chon = InputValidator.nhap_khong_rong("Vui lòng chọn tính năng (1-6): ")
            
            if lua_chon == '1': self.nhap_hoc_sinh_moi()
            elif lua_chon == '2': self.hien_thi_danh_sach()
            elif lua_chon == '3': self.tim_kiem_hoc_sinh()
            elif lua_chon == '4': self.sua_hoc_sinh()
            elif lua_chon == '5': self.xoa_hoc_sinh()
            elif lua_chon == '6':
                print("\nCảm ơn bạn đã sử dụng chương trình. Tạm biệt!")
                break
            else:
                print("\nLựa chọn không hợp lệ. Vui lòng chỉ nhập số từ 1 đến 6!")

if __name__ == "__main__":
    app = StudentTrackerApp()
    app.run()
