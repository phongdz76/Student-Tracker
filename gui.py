import tkinter as tk
from tkinter import ttk, messagebox
import threading
import urllib.request
import json
import sqlite3
import os
import random

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

class ModernStudentTrackerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quản lý Học sinh - Premium Edition")
        self.root.geometry("1100x650")
        
        self.colors = {
            "bg": "#f4f6f9",
            "panel": "#ffffff",
            "primary": "#3498db",
            "success": "#2ecc71",
            "danger": "#e74c3c",
            "warning": "#f1c40f",
            "text": "#2c3e50",
            "text_light": "#7f8c8d"
        }
        
        self.root.configure(bg=self.colors["bg"])
        
        self.setup_styles()
        
        self.db = DatabaseManager()
        self.danh_sach_hien_tai = []
        self.selected_id = None

        self.left_frame = tk.Frame(self.root, bg=self.colors["panel"], width=350)
        self.left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(20, 10), pady=20)
        self.left_frame.pack_propagate(False)
        
        self.right_frame = tk.Frame(self.root, bg=self.colors["bg"])
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 20), pady=20)

        self.tao_khung_nhap_lieu()
        self.tao_khung_danh_sach()
        
        self.tai_du_lieu_len_bang()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                        background=self.colors["panel"],
                        foreground=self.colors["text"],
                        rowheight=35,
                        fieldbackground=self.colors["panel"],
                        font=("Segoe UI", 10))
        style.map('Treeview', background=[('selected', self.colors["primary"])])
        style.configure("Treeview.Heading", 
                        background=self.colors["primary"],
                        foreground="white",
                        font=("Segoe UI", 11, "bold"),
                        relief="flat")
        style.configure("TLabel", 
                        background=self.colors["panel"], 
                        foreground=self.colors["text"], 
                        font=("Segoe UI", 11))

    def tao_khung_nhap_lieu(self):
        title_lbl = tk.Label(self.left_frame, text="THÔNG TIN HỌC SINH", 
                             bg=self.colors["panel"], fg=self.colors["text"], 
                             font=("Segoe UI", 16, "bold"))
        title_lbl.pack(pady=(20, 20))

        form_frame = tk.Frame(self.left_frame, bg=self.colors["panel"])
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20)

        self.entries = {}
        fields = [
            ("Tên học sinh:", "ten"),
            ("Tuổi/Lớp (vd 10A1):", "tuoi_lop"),
            ("Điểm Toán:", "toan"),
            ("Điểm Văn:", "van"),
            ("Điểm Anh:", "anh")
        ]

        for i, (label_text, key) in enumerate(fields):
            lbl = tk.Label(form_frame, text=label_text, bg=self.colors["panel"], fg=self.colors["text"], font=("Segoe UI", 10, "bold"))
            lbl.grid(row=i*2, column=0, sticky=tk.W, pady=(10, 2))
            
            ent = ttk.Entry(form_frame, font=("Segoe UI", 11), width=30)
            ent.grid(row=i*2+1, column=0, sticky=tk.W, ipady=5)
            self.entries[key] = ent

        btn_frame = tk.Frame(self.left_frame, bg=self.colors["panel"])
        btn_frame.pack(fill=tk.X, pady=20, padx=20)

        def create_button(parent, text, bg_color, command):
            btn = tk.Button(parent, text=text, bg=bg_color, fg="white", 
                            font=("Segoe UI", 10, "bold"), relief="flat", 
                            cursor="hand2", activebackground="#2c3e50", activeforeground="white",
                            command=command)
            return btn

        btn_them = create_button(btn_frame, "THÊM MỚI", self.colors["success"], self.them_hoc_sinh)
        btn_them.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        btn_sua = create_button(btn_frame, "CẬP NHẬT", self.colors["primary"], self.sua_hoc_sinh)
        btn_sua.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
        
        btn_xoa = create_button(btn_frame, "XÓA", self.colors["danger"], self.xoa_hoc_sinh)
        btn_xoa.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        btn_lam_moi = create_button(btn_frame, "LÀM MỚI", self.colors["text_light"], self.xoa_trang_form)
        btn_lam_moi.grid(row=1, column=1, sticky="ew", padx=5, pady=5)

        btn_api = create_button(btn_frame, "TẢI DỮ LIỆU TỪ API", self.colors["warning"], self.tai_du_lieu_tu_api)
        btn_api.config(fg=self.colors["text"])
        btn_api.grid(row=2, column=0, columnspan=2, sticky="ew", padx=5, pady=5)
        
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

    def tao_khung_danh_sach(self):
        header_frame = tk.Frame(self.right_frame, bg=self.colors["bg"])
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(header_frame, text="DANH SÁCH TỔNG HỢP", bg=self.colors["bg"], fg=self.colors["text"], font=("Segoe UI", 16, "bold")).pack(side=tk.LEFT)
        
        search_frame = tk.Frame(header_frame, bg=self.colors["panel"], padx=5, pady=5)
        search_frame.pack(side=tk.RIGHT)
        
        self.entry_tim_kiem = ttk.Entry(search_frame, font=("Segoe UI", 11), width=25)
        self.entry_tim_kiem.pack(side=tk.LEFT, padx=5)
        
        btn_tim = tk.Button(search_frame, text="TÌM KIẾM", bg=self.colors["primary"], fg="white", 
                            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", command=self.tim_kiem)
        btn_tim.pack(side=tk.LEFT, padx=5)

        btn_hien_tat_ca = tk.Button(search_frame, text="TẤT CẢ", bg=self.colors["text_light"], fg="white", 
                            font=("Segoe UI", 9, "bold"), relief="flat", cursor="hand2", command=self.tai_du_lieu_len_bang)
        btn_hien_tat_ca.pack(side=tk.LEFT, padx=5)

        table_container = tk.Frame(self.right_frame, bg=self.colors["panel"], bd=1, relief="flat")
        table_container.pack(fill=tk.BOTH, expand=True)

        columns = ("ID", "Tên", "Lớp", "Toán", "Văn", "Anh", "ĐTB", "Xếp loại")
        self.tree = ttk.Treeview(table_container, columns=columns, show="headings", selectmode="browse")
        
        widths = {"ID": 50, "Tên": 150, "Lớp": 80, "Toán": 60, "Văn": 60, "Anh": 60, "ĐTB": 60, "Xếp loại": 100}
        for col in columns:
            self.tree.heading(col, text=col.upper())
            self.tree.column(col, width=widths[col], anchor=tk.CENTER if col != "Tên" else tk.W)

        scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

        self.tree.bind("<ButtonRelease-1>", self.chon_dong_tren_bang)

    def tai_du_lieu_len_bang(self, danh_sach_loc=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        if danh_sach_loc is None:
            self.danh_sach_hien_tai = self.db.lay_danh_sach()
        else:
            self.danh_sach_hien_tai = danh_sach_loc
            
        for hs in self.danh_sach_hien_tai:
            self.tree.insert("", tk.END, values=(
                hs.id, hs.ten, hs.tuoi_lop, hs.toan, hs.van, hs.anh, hs.dtb, hs.xep_loai
            ))

    def xoa_trang_form(self):
        for key in self.entries:
            self.entries[key].delete(0, tk.END)
        self.selected_id = None

    def lay_du_lieu_tu_form(self):
        import re
        ten = self.entries["ten"].get().strip()
        tuoi_lop_raw = self.entries["tuoi_lop"].get().strip()
        
        if not ten or not tuoi_lop_raw:
            messagebox.showerror("Lỗi", "Tên và Tuổi/Lớp không được để trống!")
            return None
            
        tuoi_lop_hop_le = ""
        if tuoi_lop_raw.isdigit():
            gia_tri_int = int(tuoi_lop_raw)
            if 1 <= gia_tri_int <= 5:
                tuoi_lop_hop_le = f"Lớp {tuoi_lop_raw}"
            elif 13 <= gia_tri_int <= 18:
                tuoi_lop_hop_le = f"{tuoi_lop_raw} tuổi"
            else:
                is_lop = messagebox.askyesno(
                    "Xác nhận Tuổi hay Lớp", 
                    f"Bạn đã nhập số '{tuoi_lop_raw}'.\n\nĐây là LỚP hay TUỔI?\n- Chọn Yes: LỚP {tuoi_lop_raw}\n- Chọn No: {tuoi_lop_raw} TUỔI"
                )
                if is_lop:
                    if 1 <= gia_tri_int <= 12:
                        tuoi_lop_hop_le = f"Lớp {tuoi_lop_raw}"
                    else:
                        messagebox.showerror("Lỗi", "Lớp học chỉ từ lớp 1 đến lớp 12!")
                        return None
                else:
                    if 6 <= gia_tri_int <= 18:
                        tuoi_lop_hop_le = f"{tuoi_lop_raw} tuổi"
                    else:
                        messagebox.showerror("Lỗi", "Tuổi học sinh phải từ 6 đến 18!")
                        return None
        else:
            try:
                float(tuoi_lop_raw)
                messagebox.showerror("Lỗi", "Tuổi/Lớp không được nhập số thập phân/âm!")
                return None
            except ValueError:
                cac_so = re.findall(r'\d+', tuoi_lop_raw)
                if cac_so:
                    khoi_lop = int(cac_so[0])
                    if 1 <= khoi_lop <= 12:
                        tuoi_lop_hop_le = tuoi_lop_raw
                    else:
                        messagebox.showerror("Lỗi", "Lớp học chỉ từ lớp 1 đến lớp 12!")
                        return None
                else:
                    messagebox.showerror("Lỗi", "Tuổi/Lớp không hợp lệ (Phải chứa số, vd: 10A1)!")
                    return None
                    
        try:
            toan = float(self.entries["toan"].get().strip())
            van = float(self.entries["van"].get().strip())
            anh = float(self.entries["anh"].get().strip())
            if not (0 <= toan <= 10 and 0 <= van <= 10 and 0 <= anh <= 10):
                raise ValueError
        except ValueError:
            messagebox.showerror("Lỗi", "Điểm phải là số và nằm trong khoảng 0-10!")
            return None

        return Student(ten, tuoi_lop_hop_le, toan, van, anh, student_id=self.selected_id)

    def them_hoc_sinh(self):
        hs_moi = self.lay_du_lieu_tu_form()
        if hs_moi:
            self.db.luu_hoc_sinh(hs_moi)
            messagebox.showinfo("Thành công", f"Đã thêm học sinh {hs_moi.ten}!")
            self.tai_du_lieu_len_bang()
            self.xoa_trang_form()

    def chon_dong_tren_bang(self, event):
        selected_item = self.tree.focus()
        if not selected_item: return
        values = self.tree.item(selected_item, "values")
        self.xoa_trang_form()
        self.selected_id = int(values[0])
        self.entries["ten"].insert(0, values[1])
        self.entries["tuoi_lop"].insert(0, values[2])
        self.entries["toan"].insert(0, values[3])
        self.entries["van"].insert(0, values[4])
        self.entries["anh"].insert(0, values[5])

    def sua_hoc_sinh(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một học sinh trong bảng!")
            return
        hs_sua = self.lay_du_lieu_tu_form()
        if hs_sua:
            self.db.cap_nhat_hoc_sinh(hs_sua)
            messagebox.showinfo("Thành công", "Đã cập nhật thông tin thành công!")
            self.tai_du_lieu_len_bang()
            self.xoa_trang_form()

    def xoa_hoc_sinh(self):
        if not self.selected_id:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một học sinh trong bảng!")
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc chắn muốn xóa học sinh này không?"):
            self.db.xoa_hoc_sinh(self.selected_id)
            messagebox.showinfo("Thành công", "Đã xóa học sinh!")
            self.tai_du_lieu_len_bang()
            self.xoa_trang_form()

    def tim_kiem(self):
        tu_khoa = self.entry_tim_kiem.get().strip().lower()
        if not tu_khoa:
            self.tai_du_lieu_len_bang()
            return
        danh_sach_loc = [hs for hs in self.db.lay_danh_sach() if tu_khoa in hs.ten.lower()]
        if not danh_sach_loc:
            messagebox.showinfo("Kết quả", "Không tìm thấy học sinh nào phù hợp!")
        self.tai_du_lieu_len_bang(danh_sach_loc)

    def tai_du_lieu_tu_api(self):
        tra_loi = messagebox.askyesno("Xác nhận", "Chức năng này sẽ tải ngẫu nhiên danh sách học sinh mẫu từ Internet.\nBạn có muốn tiếp tục?")
        if not tra_loi: return

        threading.Thread(target=self._xu_ly_api_ngam, daemon=True).start()
        self.root.title("Quản lý Học sinh - Đang tải dữ liệu từ API...")

    def _xu_ly_api_ngam(self):
        try:
            url = "https://jsonplaceholder.typicode.com/users"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=5)
            data = json.loads(response.read().decode('utf-8'))
            
            so_luong = 0
            for user in data:
                ten_api = user.get("name", "Vô danh")
                tuoi_lop = f"Lớp {random.randint(1, 12)}"
                toan = round(random.uniform(4.0, 10.0), 1)
                van = round(random.uniform(4.0, 10.0), 1)
                anh = round(random.uniform(4.0, 10.0), 1)
                
                hs_moi = Student(ten_api, tuoi_lop, toan, van, anh)
                self.db.luu_hoc_sinh(hs_moi)
                so_luong += 1

            self.root.after(0, self._api_hoan_thanh, so_luong, None)
        except Exception as e:
            self.root.after(0, self._api_hoan_thanh, 0, str(e))

    def _api_hoan_thanh(self, so_luong, loi):
        self.root.title("Quản lý Học sinh - Premium Edition")
        if loi:
            messagebox.showerror("Lỗi API", f"Lỗi khi tải dữ liệu từ mạng:\n{loi}")
        else:
            messagebox.showinfo("Thành công", f"Đã nhập thêm {so_luong} học sinh mẫu từ Internet!")
            self.tai_du_lieu_len_bang()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernStudentTrackerGUI(root)
    root.mainloop()
