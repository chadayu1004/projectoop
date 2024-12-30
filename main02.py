import tkinter as tk
import io
import time
import subprocess
import tkinter.messagebox as messagebox
import webbrowser
from tkinter import Toplevel, Label 
from tkinter import messagebox
from tkinter import ttk, filedialog
from tkinter import font
from tkinter import PhotoImage
from PIL import Image, ImageTk
import base64
from server import(
    search_books_by_title,
    search_books_by_isbn, 
    search_books_by_category,
    search_edit_books_by_title,
    search_edit_books_by_isbn,
    get_cover_image,
    test_connection, 
    book_testim, 
    br_get_smartcard_data,
    rt_get_smartcard_data,
    borrow_book_from_db,
    check_return_flag,
    check_book_stock,
    update_book_stock,
    check_borrow_duplicate,
    insert_book,
    update_book,
    fetch_borrowed_books,
    update_book_status,
    get_borrow_max_data,
    get_remain_borrow,
    staff_admin,
    check_member_status
    )

class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("โปรแกรมจัดการห้องสมุด")
        self.root.geometry("450x600")
        self.process = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        # Initialize Book first
        self.book = Book(self, self.root, None, None)  # Create book first
        self.staff = Staff(self.root, self, self.book)  # Now we can safely create self.staff
        self.member = Member(self, self.root, self.book)  # Pass self.book to Member
        self.book.member = self.member  # Update self.member in Book
        self.library = Library(self.root, self.book)
        self.book.library = self.library
        
        self.initialize_main_menu()

        self.results_frame = None  # Will be set when needed
        self.results_tree = None  # Will be set when needed

    def initialize_main_menu(self):
        # ตั้งค่าขนาดหน้าต่างและป้องกันการปรับขนาดหน้าต่าง
        self.root.geometry("450x600")
        self.root.resizable(False, False)
        
        # สร้างและกำหนดค่าป้ายกำกับหัวเรื่อง
        self.header = ttk.Label(self.root, text="โปรแกรมจัดการห้องสมุด", font=("Arial", 20))
        self.header.pack(pady=20)

        # โหลดภาพและแสดงผลเฉพาะในหน้านี้
        image = Image.open("main_menu.png")
        image = image.resize((200, 200), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(image)

        self.image_label = ttk.Label(self.root, image=self.image)
        self.image_label.pack(pady=5)

        # สร้างป้ายกำกับหัวข้อย่อย
        self.subheader = ttk.Label(self.root, text="กรุณาเลือกเมนูที่ต้องการใช้งาน", font=("Arial", 14))
        self.subheader.pack(pady=5)

        # สร้างเฟรมสำหรับปุ่มเมนู
        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=20)

        # สร้างปุ่มเมนูต่างๆ
        self.search_button = ttk.Button(self.button_frame, text="ค้นหา/ยืม หนังสือ", width=25, command=self.book.show_search_form)
        self.search_button.grid(row=0, column=0, padx=10, pady=10)

        self.borrow_return_button = ttk.Button(self.button_frame, text="คืนหนังสือ", width=25, command=self.member.borrow_return_books)
        self.borrow_return_button.grid(row=1, column=0, padx=10, pady=10)

        self.staff_button = ttk.Button(self.button_frame, text="สำหรับเจ้าหน้าที่", width=25, command=self.staffmain)
        self.staff_button.grid(row=2, column=0, padx=10, pady=10)

        # สร้างเฟรมล่างสำหรับปุ่มต่างๆ
        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.pack(side="bottom", fill="x", pady=10)

        # ปุ่มสถานะการเชื่อมต่อ
        self.easter_egg_button = ttk.Button(self.bottom_frame, text="สถานะการเชื่อมต่อ", width=15, command=self.test_db_connection)
        self.easter_egg_button.pack(side="left", padx=20)

        # ปุ่ม Resource
        self.resource_button = ttk.Button(self.bottom_frame, text="SQL Web Socket", width=15, command=self.SQL_Web_Socket)
        self.resource_button.pack(side="left", padx=20, expand=True)

        # ปุ่มเกี่ยวกับ
        self.about_button = ttk.Button(self.bottom_frame, text="เกี่ยวกับ", width=15, command=self.open_about)
        self.about_button.pack(side="right", padx=20)


    def read_card(self):
        try:
            # เริ่มการตรวจสอบเครื่องอ่านบัตร โดยหน่วงเวลา 3 วินาที
            for _ in range(3):  # ตรวจสอบ 3 ครั้ง โดยหน่วงเวลาทุก 1 วินาที
                card_data = rt_get_smartcard_data()
                if card_data:
                    break
                time.sleep(1)  # รอ 1 วินาที

            # ถ้าไม่พบเครื่องอ่านบัตรหลังจากหน่วงเวลาแล้ว
            if not card_data:
                messagebox.showerror("Error", "ไม่พบเครื่องอ่านบัตร กรุณาลองใหม่อีกครั้ง")
                return

            # ตรวจสอบว่าข้อมูลจากบัตรมีอยู่จริง
            if isinstance(card_data, tuple) and len(card_data) >= 4:
                pid = card_data[0]  # ดึงเลขบัตรประชาชน
                prefix = card_data[1]  # ดึงคำนำหน้า
                first_name = card_data[2]  # ดึงชื่อ
                last_name = card_data[3]  # ดึงนามสกุล

                # ตรวจสอบสมาชิก
                is_member = check_member_status(pid)

                if not is_member:
                    messagebox.showerror("Error", "ไม่พบข้อมูลสมาชิก กรุณาติดต่อเจ้าหน้าที่")
                    return

                # ดึงข้อมูลจำนวนหนังสือสูงสุดที่ยืมได้และจำนวนหนังสือที่ยืมไปแล้ว
                borrow_max_data = get_borrow_max_data(pid)
                remain_data = get_remain_borrow(pid)

                borrow_max = "ไม่ทราบ"
                remain_borrow = "ไม่ทราบ"

                if borrow_max_data:
                    borrow_max = borrow_max_data[0][0]

                if remain_data:
                    remain_borrow = remain_data[0][0]

                # Update UI elements
                def update_entry(field, value):
                    entry = self.member.entries.get(field)
                    if entry:
                        entry.config(state="normal")
                        entry.delete(0, tk.END)
                        entry.insert(0, value)
                        entry.config(state="readonly")

                update_entry("เลขบัตรประชาชน:", pid)
                update_entry("คำนำหน้า:", prefix)
                update_entry("ชื่อ:", first_name)
                update_entry("นามสกุล:", last_name)
                update_entry("ยืมได้สูงสุด:", borrow_max)
                update_entry("ยืมได้อีก:", remain_borrow)

                # ดึงข้อมูลการยืมหนังสือ
                borrowed_books = fetch_borrowed_books(pid)

                # ล้างข้อมูลใน Treeview
                for item in self.member.data_tree.get_children():
                    self.member.data_tree.delete(item)

                # เพิ่มข้อมูลการยืมหนังสือเข้าไปใน Treeview
                for book in borrowed_books:
                    self.member.data_tree.insert("", "end", values=(
                        book[0],  # ISBN ของหนังสือ
                        book[1],  # ชื่อหนังสือ
                        book[2],  # รายละเอียดหรือหมวดหมู่หนังสือ
                        book[3],  # วันที่ยืม
                        book[4]   # วันที่ต้องคืน
                    ))

            else:
                # แสดงข้อความข้อผิดพลาดหากไม่สามารถอ่านข้อมูลจากบัตรได้
                messagebox.showerror("Error", "ไม่พบข้อมูล กรุณาเสียบบัตร")

        except Exception as e:
            # จัดการกับข้อผิดพลาดที่ไม่คาดคิด
            error_msg = "ไม่พบเครื่องอ่านบัตร" if "No readers" in str(e) else f"ไม่พบข้อมูลสมาชิก กรุณาติดต่อเจ้าหน้าที่\n{str(e)}"
            messagebox.showerror("Error", error_msg)


    def close_window(self):
        # ฟังก์ชันปิดหน้าต่าง (ยังไม่มีการทำงานจริง)
        self.root.destroy()

    def show_regulations(self):
        # Create a new window to display borrowing regulations
        regulations_window = tk.Toplevel(self.root)  # Assuming `self.root` is the main Tk window
        regulations_window.title("กฎระเบียบการยืม")
        regulations_window.geometry("600x600")  # Adjust the window size as needed

        # Define font sizes for regular text and header
        regulations_font = font.Font(size=12)
        header_font = font.Font(size=16, weight="bold")

        # Create a label for the header "กฎระเบียบการยืม"
        header_label = ttk.Label(regulations_window, text="กฎระเบียบการยืม", font=header_font)
        header_label.pack(pady=10)  # Add padding on top

        # Load an image (make sure the file 'role_library.png' is in the correct directory)
        image = PhotoImage(file="role_library.png")

        # Create a label for the image and place it above the text
        image_label = ttk.Label(regulations_window, image=image)
        image_label.image = image  # Keep a reference to the image to prevent garbage collection
        image_label.pack(pady=10)

        # Create a label to display borrowing regulations
        regulations_text = """
        1. ยืมหนังสือได้ไม่เกินสามเล่ม
        2. หนังสือหนึ่งเรื่อง สามารถยืมได้หนึ่งเล่มเท่านั้น
        3. มีกำหนดยืม 1 วัน ต้องคืนภายในวันที่กำหนด
        4. ค่าปรับวันละ 10 บาท หากมีข้อสงสัย ให้ติดต่อบรรณารักษ์ เพื่อรับข้อมูลเพิ่มเติม
        """
        regulations_label = ttk.Label(regulations_window, text=regulations_text, justify="left", padding=(10, 10), font=regulations_font)
        regulations_label.pack(fill="both", expand=True)

        # Create a button to close the regulations window
        close_button = ttk.Button(regulations_window, text="ปิดหน้าต่าง", command=regulations_window.destroy)
        close_button.pack(pady=10)
 

    def test_db_connection(self):
        try:
            result = test_connection()
            messagebox.showinfo("สถานะเซิร์ฟเวอร์", result)
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

    def staffmain(self):
        # เรียก clear_window เพื่อล้างหน้าต่างก่อน
        self.clear_window()

        # กำหนดขนาดของหน้าต่าง
        self.root.geometry("350x500")

        # กำหนดกริดโครงร่าง
        self.root.grid_rowconfigure(0, weight=1)  # ทำให้แถวแรกยืดได้
        self.root.grid_rowconfigure(8, weight=1)  # ทำให้แถวสุดท้ายยืดได้
        self.root.grid_columnconfigure(0, weight=1)  # ทำให้คอลัมน์กลางยืดได้

        # ข้อความหัวเรื่อง
        self.title_label = ttk.Label(self.root, text="เข้าสู่ระบบเจ้าหน้าที่", font=("Arial", 14, "bold"))
        self.title_label.grid(row=0, column=0, pady=10, padx=40, sticky="n")

        image_path = "user_icon.png"  # Replace with your image path
        image = Image.open(image_path)
        image = image.resize((200, 150), Image.Resampling.LANCZOS) 
        self.image = ImageTk.PhotoImage(image)
        self.image_label = ttk.Label(self.root, image=self.image)
        self.image_label.grid(row=1, column=0, pady=5, padx=40, sticky="n")

        # ข้อความคำแนะนำ
        self.instruction_label = ttk.Label(self.root, text="กรุณา Login ด้วยชื่อผู้ใช้และรหัสผ่าน", font=("Arial", 12))
        self.instruction_label.grid(row=2, column=0, pady=5, padx=40, sticky="n")

        # ป้ายกำกับและช่องกรอกชื่อผู้ใช้
        self.username_label = ttk.Label(self.root, text="ชื่อผู้ใช้", font=("Arial", 12))
        self.username_label.grid(row=3, column=0, pady=5, padx=40, sticky="nw")

        self.username_entry = ttk.Entry(self.root, font=("Arial", 12), width=30)
        self.username_entry.grid(row=4, column=0, pady=5, padx=40, sticky="ew")  # Align to left and expand

        # ป้ายกำกับและช่องกรอกรหัสผ่าน
        self.password_label = ttk.Label(self.root, text="รหัสผ่าน", font=("Arial", 12))
        self.password_label.grid(row=5, column=0, pady=5, padx=40, sticky="nw")

        self.password_entry = ttk.Entry(self.root, show='*', font=("Arial", 12), width=30)
        self.password_entry.grid(row=6, column=0, pady=5, padx=40, sticky="ew")  # Align to left and expand

        # ปุ่มเข้าสู่ระบบ
        self.login_button = ttk.Button(self.root, text="เข้าสู่ระบบ", command=self.login)
        self.login_button.grid(row=7, column=0, pady=(5, 5), padx=40, sticky="ew")  # Align to left and expand
        self.login_button.config(style='TButton')

        # ปุ่มกลับไปหน้าแรก
        self.back_button = ttk.Button(self.root, text="กลับไปหน้าแรก", command=self.book.reset_to_main_menu)
        self.back_button.grid(row=8, column=0, pady=(5, 5), padx=40, sticky="ew")  # Align to left and expand
        self.back_button.config(style='TButton')


    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        # เรียกใช้ฟังก์ชันจาก server เพื่อตรวจสอบข้อมูลการเข้าสู่ระบบ
        if staff_admin(username, password):
            messagebox.showinfo("เข้าสู่ระบบ", "เข้าสู่ระบบสำเร็จ!")
            # ดำเนินการต่อไปยังหน้า admin panel หรือเมนูหลัก
            self.staff.staff_add_book()
        else:
            messagebox.showerror("เข้าสู่ระบบ", "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง.")


    def show_navbar(self):
        # สร้างเฟรมสำหรับแถบนำทาง (Navbar)
        navbar_frame = ttk.Frame(self.root, padding=5)
        navbar_frame.pack(fill=tk.X)


        # เพิ่มปุ่มในแถบนำทางสำหรับการนำทาง
        add_book_button = ttk.Button(navbar_frame, text="เพิ่มหนังสือ", command=self.staff.show_add_book_form)
        add_book_button.pack(side=tk.LEFT, padx=10, pady=10)

        edit_book_button = ttk.Button(navbar_frame, text="แก้ไขหนังสือ", command=self.staff.search_books_edit_books)
        edit_book_button.pack(side=tk.LEFT, padx=10, pady=10)





    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        # Reset frames and widgets to None
        self.results_frame = None
        self.book.results_tree = None
        self.book.search_frame = None

    def SQL_Web_Socket(self):
        batch_file_path = r"library_oob.bat"  # กำหนดที่อยู่ของไฟล์ Batch
        
        # แสดงกล่องข้อความก่อนรันไฟล์ Batch
        # messagebox.showinfo("Information", "กำลังเปิด CMD เพื่อรันไฟล์ Batch...")

        try:
            # เปิด CMD และรันไฟล์ Batch
            self.process = subprocess.Popen(
                ['cmd.exe', '/k', batch_file_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE  # เปิดใหม่ในหน้าต่างใหม่
            )
            # แสดงกล่องข้อความหลังจากไฟล์ Batch เริ่มรัน
            # messagebox.showinfo("Information", "CMD เปิดแล้ว กำลังรันไฟล์ Batch!")
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถรันไฟล์ Batch ได้: {str(e)}")

    def on_close(self):
        # แสดงกล่องข้อความยืนยันก่อนปิดโปรแกรม
        if messagebox.askokcancel("Quit", "คุณแน่ใจว่าต้องการปิดโปรแกรม?"):
            if self.process is not None:
                # ปิด subprocess
                self.process.terminate()
                self.process = None  # ตั้งค่าให้เป็น None เพื่อไม่ให้เกิดข้อผิดพลาดในอนาคต
            
            self.root.destroy()  # ปิดหน้าต่างโปรแกรม


    def open_about(self):
        # สร้างหน้าต่างใหม่
        about_window = Toplevel(self.root)
        about_window.title("เกี่ยวกับ")

        # ป้ายชื่อหัวข้อสำหรับส่วนเกี่ยวกับ
        header_label = ttk.Label(about_window, text="เกี่ยวกับ", font=("Arial", 16, "bold"))
        header_label.pack(pady=10)

        # สร้างเฟรมเพื่อจัดเรียงเนื้อหาให้อยู่ตรงกลาง
        frame = ttk.Frame(about_window)
        frame.pack(expand=True)

        # เพิ่มป้ายชื่อสำหรับเนื้อหา
        about_text = (
            "โปรแกรมจัดการห้องสมุด เป็นส่วนหนึ่งของรายวิชา 4122309 การเขียนโปรแกรมเชิงวัตถุ\n\n"
            "จัดทำโดย:\n"
            f"{'สหกาญจน์ คลองสามสิบ'.ljust(40)}   6430122115302\n"
            f"{'ชฏายุ    แก้วมณี'.ljust(40)}       6430122115304\n"
            f"{'สรศักดิ์   ทรงแก้ว'.ljust(40)}      6430122115306\n\n"
            "เสนอโดย:\n"
            "อ.นัฐพงศ์ ส่งเนียม\n"
            "คณะวิทยาศาสตร์และเทคโนโลยี มหาวิทยาลัยราชภัฏพระนคร\n\n"
            "ท่านสามารถดาวน์โหลดเล่มโครงงาน และวิธีการใช้งานโปรแกรมได้ที่นี่\n"
        )

        # แสดงข้อความเกี่ยวกับ
        about_label = ttk.Label(frame, text=about_text, justify="center", padding=(10, 10))
        about_label.pack()

        # ลิงก์ URL สำหรับดาวน์โหลดโครงการ
        url = "https://shorturl.at/KHVqb"
        link_label = ttk.Label(frame, text=url, font=("Arial", 12, "underline"), foreground="blue", cursor="hand2")

        # จัดป้ายลิงก์ให้อยู่ตรงกลางพร้อมเว้นระยะ
        link_label.pack(pady=5)
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new(url))

        # โหลดและแสดงภาพ QR Code
        try:
            original_image = Image.open("qr-manual.png")
            size = (100, 100)  # ขนาดที่ต้องการ (100x100)
            resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
            qr_image = ImageTk.PhotoImage(resized_image)

            # เพิ่มภาพ QR Code
            qr_label = ttk.Label(frame, image=qr_image)
            qr_label.image = qr_image  # เก็บอ้างอิงเพื่อหลีกเลี่ยงการเก็บขยะ
            qr_label.pack(pady=10)
        except Exception as e:
            error_label = ttk.Label(frame, text="ไม่สามารถโหลด QR Code ได้", foreground="red")
            error_label.pack(pady=10)

        # เพิ่มปุ่มปิด
        close_button = ttk.Button(about_window, text="ปิด", command=about_window.destroy)
        close_button.pack(pady=10)  # เพิ่มระยะเว้นเพื่อให้ดูสบายตา

class Member:
    def __init__(self, library_gui, root, book):
        self.library_gui = library_gui
        self.root = root
        self.book = book
        self.borrow_frame = None

    def borrow_return_books(self):
        # เรียกใช้งานฟังก์ชัน clear_window เพื่อล้างหน้าต่างก่อน
        self.library_gui.clear_window()

        # ตั้งค่าขนาดหน้าต่าง
        self.root.geometry("1200x700")

        # สร้าง frame หลักสำหรับจัดระเบียบเลย์เอาต์
        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill='both')

        # สร้าง frame สำหรับข้อมูล (ด้านขวา)
        info_frame = ttk.Frame(main_frame, padding=20)
        info_frame.grid(row=0, column=1, sticky="nsew")

        # สร้าง frame สำหรับรูปภาพและปุ่มอ่านบัตร (ด้านซ้าย)
        image_frame = ttk.Frame(main_frame, padding=20)
        image_frame.grid(row=0, column=0, sticky="nsew")

        # ป้ายชื่อเรื่อง
        title_label = ttk.Label(info_frame, text="คืนหนังสือ", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=15)

        # ช่องกรอกข้อมูล
        labels = ["เลขบัตรประชาชน:", "คำนำหน้า:", "ชื่อ:", "นามสกุล:", "ยืมได้สูงสุด:", "ยืมได้อีก:"]
        self.entries = {}  # Initialize entries once

        for i, text in enumerate(labels):
            label = ttk.Label(info_frame, text=text, font=("Arial", 12))
            label.grid(row=i+1, column=0, sticky="e", padx=(0, 10), pady=5)
            entry = ttk.Entry(info_frame, font=("Arial", 12), state='readonly')
            entry.grid(row=i+1, column=1, padx=(10, 0), pady=5, sticky="w")
            self.entries[text] = entry

        # คำแนะนำ (อยู่ด้านบนตาราง)
        instructions_label = ttk.Label(info_frame, text="หนังสือที่ท่านยืม", font=("Arial", 12, "bold"))
        instructions_label.grid(row=11, column=0, columnspan=2, pady=10, sticky="w")

        # โหลดและแสดงภาพ
        img = Image.open("istock.png")
        img = img.resize((400, 400))  # ปรับขนาดภาพเป็น 4 นิ้ว (100 พิกเซลต่อ นิ้ว)
        img = ImageTk.PhotoImage(img)
        image_label = ttk.Label(image_frame, image=img)
        image_label.image = img
        image_label.pack(pady=5)

        # คำแนะนำ (อยู่ด้านบนของปุ่ม)
        instructions_label = ttk.Label(
            image_frame, 
            text="โปรดเสียบบัตรประชาชนเพื่ออ่านข้อมูลจากบัตร", 
            font=("Arial", 10, "bold")
        )
        instructions_label.pack(side="top", pady=(0, 5))  # เพิ่มระยะห่างด้านล่าง

        # ปุ่มอ่านบัตร (จัดกลางใต้รูป และลดขนาดปุ่มตามตัวอักษร)
        read_card_button = ttk.Button(
            image_frame, 
            text="อ่านบัตร",
            command=self.library_gui.read_card
        )
        read_card_button.pack(side="top", pady=5)

        # ตารางข้อมูล
        self.data_tree = ttk.Treeview(info_frame, columns=("BookID", "Title", "Category", "BorrowDate", "ReturnDate"), show='headings')
        self.data_tree.heading("BookID", text="เลขหนังสือ")
        self.data_tree.heading("Title", text="ชื่อหนังสือ")
        self.data_tree.heading("Category", text="หมวดหมู่")
        self.data_tree.heading("BorrowDate", text="วันที่ยืม")
        self.data_tree.heading("ReturnDate", text="วันที่ต้องคืน")

        self.data_tree.column("BookID", width=100, anchor="center")
        self.data_tree.column("Title", width=200, anchor="w")
        self.data_tree.column("Category", width=150, anchor="w")
        self.data_tree.column("BorrowDate", width=100, anchor="center")
        self.data_tree.column("ReturnDate", width=100, anchor="center")

        self.data_tree.grid(row=12, column=0, columnspan=2, pady=10, sticky="nsew")

        # ปุ่มคืนหนังสือและปิดหน้าต่าง
        button_frame = ttk.Frame(info_frame, padding=10)
        button_frame.grid(row=13, column=0, columnspan=2, sticky="e")

        # ปุ่มกลับไปหน้าแรก
        close_button = ttk.Button(button_frame, text="ย้อนกลับไปหน้าแรก", command=self.book.reset_to_main_menu)
        close_button.pack(side="left", padx=10)

        # ปุ่มยืนยันการคืนหนังสือ
        return_button = ttk.Button(button_frame, text="ยืนยันการคืนหนังสือ", command=self.return_book)
        return_button.pack(side="left", padx=10)

        # ปุ่มกฎระเบียบการยืม
        regulations_button = ttk.Button(button_frame, text="กฎระเบียบในการยืม", command=self.library_gui.show_regulations)
        regulations_button.pack(side="left", padx=10)

        # ทำให้ Treeview ขยายตามขนาดของหน้าต่าง
        info_frame.grid_rowconfigure(12, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)  # เพิ่มน้ำหนักให้กับคอลัมน์ที่ 1 สำหรับข้อมูล


    def return_book(self):
        # ดึงข้อมูลหนังสือที่ต้องการคืนจาก Treeview
        selected_item = self.data_tree.selection()
        if selected_item:
            book_data = self.data_tree.item(selected_item, "values")
            isbn = book_data[0]

            # อัปเดตสถานะการคืนหนังสือในฐานข้อมูล
            update_book_status(isbn)

            # อัปเดตสต็อกหนังสือ
            update_book_stock(isbn, increment=True)

            # ลบหนังสือออกจาก Treeview หลังคืนหนังสือสำเร็จ
            self.data_tree.delete(selected_item)

            messagebox.showinfo("Success", "หนังสือถูกคืนสำเร็จ")
        else:
            messagebox.showwarning("Warning", "กรุณาเลือกหนังสือที่จะคืน")


    def borrow_book(self, book_title, book_isbn):
        # Clear the window before proceeding
        self.library_gui.clear_window()

        # Set window size
        self.root.geometry('600x550')
        
        # Create a frame for borrowing books
        borrow_frame = ttk.Frame(self.root, padding="20")
        borrow_frame.pack(fill=tk.BOTH, expand=True)

        # Create a left frame for the image
        left_frame = ttk.Frame(borrow_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Load and display the image
        image = Image.open("istock.png")
        inches = 3
        dpi = 96
        size = (int(inches * dpi), int(inches * dpi))
        image = image.resize(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        image_label = ttk.Label(left_frame, image=photo)
        image_label.photo = photo
        image_label.pack(pady=10)

        # Create a right frame for instructions and ID card fields
        right_frame = ttk.Frame(borrow_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Add instructions
        card_instructions_label = ttk.Label(right_frame, text="กรุณาเสียบบัตรประชาชน", font=("Arial", 14))
        card_instructions_label.pack(pady=10)
        press_button_label = ttk.Label(right_frame, text="จากนั้นกดปุ่ม อ่านข้อมูล")
        press_button_label.pack(pady=10)

        # Add button to read card data
        read_card_button = ttk.Button(right_frame, text="อ่านข้อมูล", command=self.process_card_data)
        read_card_button.pack(pady=10)

        # Update the layout of the window
        self.root.update_idletasks()
        # Adjust the window size to fit content
        self.root.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")

        # Add fields for ID card number, first name, and last name
        self.card_id_var = tk.StringVar()
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()

        # Create StringVar for ISBN
        self.isbn_var = tk.StringVar()
        self.isbn_var.set(book_isbn)

        self.title_var = tk.StringVar()
        self.title_var.set(book_title)

        # Create label for ISBN
        isbn_label = ttk.Label(right_frame, text="หมายเลข ISBN:")
        isbn_label.pack(pady=5)

        # Create entry field for ISBN
        self.isbn_entry = ttk.Entry(right_frame, textvariable=self.isbn_var, state='readonly')
        self.isbn_entry.pack(pady=5)

        # Create label for title
        title_label = ttk.Label(right_frame, text="ชื่อหนังสือ:")
        title_label.pack(pady=5)

        # Create entry field for title
        self.book_name_entry = ttk.Entry(right_frame, textvariable=self.title_var, state='readonly')
        self.book_name_entry.pack(pady=5)

        card_id_label = ttk.Label(right_frame, text="หมายเลขบัตรประชาชน:")
        card_id_label.pack(pady=5)
        self.card_id_entry = ttk.Entry(right_frame, textvariable=self.card_id_var, state='readonly')
        self.card_id_entry.pack(pady=5)

        first_name_label = ttk.Label(right_frame, text="ชื่อ:")
        first_name_label.pack(pady=5)
        self.first_name_entry = ttk.Entry(right_frame, textvariable=self.first_name_var, state='readonly')
        self.first_name_entry.pack(pady=5)

        last_name_label = ttk.Label(right_frame, text="นามสกุล:")
        last_name_label.pack(pady=5)
        self.last_name_entry = ttk.Entry(right_frame, textvariable=self.last_name_var, state='readonly')
        self.last_name_entry.pack(pady=5)

        # สร้างเฟรมสำหรับปุ่มยืนยันและปุ่มกลับไปหน้าแรก
        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        # ปุ่มยืนยันการยืม
        confirm_button = ttk.Button(
            buttons_frame, text="ยืนยันการยืม",
            command=self.book.confirm_borrowing)
        confirm_button.pack(side=tk.LEFT, padx=5)

        # ปุ่มกลับไปหน้าแรก
        back_button = ttk.Button(
            buttons_frame, text="กลับไปหน้าแรก",
            command=self.book.reset_to_main_menu)  # เปลี่ยนเป็น self.reset_to_main_menu
        back_button.pack(side=tk.LEFT, padx=5)


    def process_card_data(self):
        try:
            # อ่านข้อมูลจากบัตรประชาชน
            cid, prefix, first_name, last_name = br_get_smartcard_data()

            # ตรวจสอบว่าข้อมูลได้รับการเรียกคืนหรือไม่
            if not (cid and prefix and first_name and last_name):
                raise ValueError("ข้อมูลไม่ครบถ้วน")

            # ตั้งค่าเนื้อหาฟิลด์
            self.card_id_var.set(cid)
            self.first_name_var.set(first_name)
            self.last_name_var.set(last_name)

        except ValueError as ve:
            messagebox.showerror("ข้อผิดพลาด", str(ve))
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", "ไม่พบข้อมูล กรุณาเสียบบัตร")


class Book:
    def __init__(self, library_gui, root, staff, member):
        self.library_gui = library_gui
        self.root = root
        self.library = None
        self.staff = staff
        self.member = member
        self.search_frame = None
        self.results_tree = None

    def initialize_search_frame(self):
        # Create and prepare the search form
        if not hasattr(self, 'search_frame') or self.search_frame is None:
            self.search_frame = ttk.Frame(self.library_gui.root, padding="10")
            
            self.search_header = ttk.Label(self.search_frame, text="ค้นหาหนังสือ", font=("Arial", 18))
            self.search_header.pack(pady=10)

            # Load image
            image = Image.open("search_pic.png")
            image = image.resize((int(1.50 * 90), int(1.25 * 90)), Image.Resampling.LANCZOS)  # Resize image
            image = ImageTk.PhotoImage(image)
            
            image_label = ttk.Label(self.search_frame, image=image)
            image_label.image = image  # Keep a reference to avoid garbage collection
            image_label.pack(pady=10)

            self.search_header = ttk.Label(self.search_frame, text="กรอกข้อมูลหนังสือที่ต้องการค้นหา", font=("Arial", 14))
            self.search_header.pack(pady=10)

            self.search_subheader = ttk.Label(
                self.search_frame,
                text="กรอกเงื่อนไขอย่างใดอย่างหนึ่งเท่านั้น\nคุณสามารถค้นหาโดยใช้คำใดคำหนึ่งของหนังสือได้",
                font=("Arial", 10),
                anchor="center",
                justify="center"
            )
            self.search_subheader.pack(pady=10)

            self.form_frame = ttk.Frame(self.search_frame)
            self.form_frame.pack(pady=10)

            ttk.Label(self.form_frame, text="ชื่อหนังสือ:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
            self.book_name_entry = ttk.Entry(self.form_frame, width=40)
            self.book_name_entry.grid(row=0, column=1, padx=5, pady=5)

            ttk.Label(self.form_frame, text="เลข ISBN:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.isbn_entry = ttk.Entry(self.form_frame, width=40)
            self.isbn_entry.grid(row=1, column=1, padx=5, pady=5)

            ttk.Label(self.form_frame, text="หมวดหมู่หนังสือ:", font=("Arial", 12)).grid(row=2, column=0, padx=5, pady=5, sticky="w")
            self.category = ttk.Combobox(self.form_frame, width=37, values=[
                "เบ็ตเตล็ดหรือความรู้ทั่วไป (Generalities)", "ปรัชญา (Philosophy)", "ศาสนา (Religion)",
                "สังคมศาสตร์ (Social Sciences)", "ภาษาศาสตร์ (Language)", "วิทยาศาสตร์ (Science)",
                "วิทยาศาสตร์ประยุกต์ หรือเทคโนโลยี (Technology)", "ศิลปกรรมและการบันเทิง (Arts and recreation)",
                "วรรณคดี (Literature)", "ประวัติศาสตร์และภูมิศาสตร์ (History and geography)"
            ])
            self.category.grid(row=2, column=1, padx=5, pady=5, sticky="w")

            self.button_frame_search = ttk.Frame(self.search_frame)
            self.button_frame_search.pack(pady=10)

            self.search_back_button = ttk.Button(self.button_frame_search, text="กลับ", command=self.reset_to_main_menu, width=10, padding=(5, 5))
            self.search_back_button.grid(row=0, column=0, padx=10)

            self.search_submit_button = ttk.Button(self.button_frame_search, text="ค้นหา", command=self.search_books, width=10, padding=(5, 5))
            self.search_submit_button.grid(row=0, column=1, padx=10)

            self.search_frame.pack(fill="both", expand=True)

    def show_search_form(self):
        if not hasattr(self, 'search_frame') or self.search_frame is None:
            self.initialize_search_frame()

        # Hide the main menu buttons by referencing the LibraryGUI instance
        self.library_gui.header.pack_forget()
        self.library_gui.subheader.pack_forget()
        self.library_gui.button_frame.pack_forget()
        self.library_gui.staff_button.pack_forget()
        self.library_gui.easter_egg_button.pack_forget()
        self.library_gui.resource_button.pack_forget()
        self.library_gui.about_button.pack_forget()
        self.library_gui.image_label.pack_forget()

        # Show the search form
        self.search_frame.pack(fill="both", expand=True)

    def reset_to_main_menu(self):
        self.library_gui.clear_window()
        self.library_gui.initialize_main_menu()


    def on_book_select(self, event):
        selected_item = self.library.results_tree.selection()[0]
        book_details = self.library.results_tree.item(selected_item, "values")
        self.show_book_details(book_details)


    def search_books(self):
        book_name = self.book_name_entry.get()
        isbn = self.isbn_entry.get()
        category = self.category.get()

        # ตรวจสอบหากมีการกรอกข้อมูลมากกว่าหนึ่งเงื่อนไข
        search_criteria_count = sum([bool(book_name), bool(isbn), bool(category)])
        
        if search_criteria_count > 1:
            messagebox.showwarning("คำเตือน", "กรุณากรอกข้อมูลเพียงตัวเลือกเดียวเท่านั้น")
            return

        # ลบผลลัพธ์เก่าก่อนเพิ่มผลลัพธ์ใหม่
        for row in self.library.results_tree.get_children():
            self.library.results_tree.delete(row)

        # ค้นหาหนังสือ
        if book_name:
            result = search_books_by_title(book_name)
        elif isbn:
            result = search_books_by_isbn(isbn)
        elif category:
            category_map = {
                "เบ็ตเตล็ดหรือความรู้ทั่วไป (Generalities)": "000",
                "ปรัชญา (Philosophy)": "100",
                "ศาสนา (Religion)": "200",
                "สังคมศาสตร์ (Social Sciences)": "300",
                "ภาษาศาสตร์ (Language)": "400",
                "วิทยาศาสตร์ (Science)": "500",
                "วิทยาศาสตร์ประยุกต์ หรือเทคโนโลยี (Technology)": "600",
                "ศิลปกรรมและการบันเทิง (Arts and recreation)": "700",
                "วรรณคดี (Literature)": "800",
                "ประวัติศาสตร์และภูมิศาสตร์ (History and geography)": "900"
            }
            catalog_num = category_map.get(category, "")
            result = search_books_by_category(catalog_num)
        else:
            messagebox.showinfo("ผลการค้นหา", "กรุณากรอกข้อมูลอย่างน้อย 1 เงื่อนไขเพื่อค้นหา")
            return

        # ตรวจสอบผลการค้นหา
        if isinstance(result, str) and "Error in connection" in result:
            messagebox.showerror("ข้อผิดพลาด", result)
        elif isinstance(result, str):
            messagebox.showinfo("ผลการค้นหา", result)
        else:
            if not result:  # ตรวจสอบว่าผลลัพธ์มีหรือไม่
                messagebox.showinfo("ผลการค้นหา", "ไม่พบผลลัพธ์ตามเงื่อนไขที่กำหนด")
            else:
                for index, book in enumerate(result):
                    self.library.results_tree.insert("", "end", values=(
                        index + 1,
                        book.get('book_on', 'N/A'),
                        book.get('book_title', 'N/A'),
                        book.get('book_isbn', 'N/A'),
                        book.get('book_publisher', 'N/A'),
                        book.get('catalog_name', 'N/A'),
                        book.get('book_detail', 'N/A')
                    ))

        # ซ่อน search_frame และแสดง results_frame
        self.search_frame.pack_forget()
        self.library.results_frame.pack(fill="both", expand=True)
  


    def show_book_details(self, book_details):
        # Create a new window
        details_window = tk.Toplevel(self.root)
        details_window.title("รายละเอียดหนังสือ")
        details_window.geometry("900x600")
        details_window.resizable(True, True)

        # Create a main frame for book details
        details_frame = ttk.Frame(details_window, padding="20")
        details_frame.pack(fill="both", expand=True)

        # Retrieve the book cover image using the ISBN as an identifier
        image = book_testim(book_details[3])

        # Create a frame for the content of the book
        content_frame = ttk.Frame(details_frame)
        content_frame.grid(row=0, column=0, sticky="nsew")

        # Display the book cover image
        if image:
            try:
                # Resize to 2 inches (96 DPI)
                size = (int(2 * 96), int(2 * 96))
                image = image.resize(size, Image.Resampling.LANCZOS)
                img = ImageTk.PhotoImage(image)

                panel = ttk.Label(content_frame, image=img)
                panel.image = img  # Keep a reference to avoid garbage collection
                panel.grid(row=0, column=0, rowspan=6, padx=(0, 20), pady=10, sticky="nw")
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการแสดงภาพ: {e}")
                ttk.Label(content_frame, text="ไม่สามารถแสดงรูปภาพปกหนังสือ", font=("Arial", 12, "bold"), foreground="red").grid(row=0, column=0, rowspan=6, padx=(0, 20), pady=10, sticky="nw")
        else:
            ttk.Label(content_frame, text="ไม่พบรูปภาพปกหนังสือ", font=("Arial", 12, "bold"), foreground="red").grid(row=0, column=0, rowspan=6, padx=(0, 20), pady=10, sticky="nw")

        # Show book details
        details = [
            ("ชื่อหนังสือ", book_details[2]),
            ("ISBN", book_details[3]),
            ("สำนักพิมพ์", book_details[4]),
            ("หมวดหมู่", book_details[5])
        ]
        for idx, (label, value) in enumerate(details):
            ttk.Label(content_frame, text=f"{label}: {value}", font=("Arial", 12, "bold")).grid(row=idx, column=1, sticky="w", pady=(0, 5))

        # Show book summary
        summary_text = book_details[6] if len(book_details) > 6 else "ไม่มีข้อมูลเรื่องย่อ"
        summary_text = "\n\n".join(["    " + para for para in summary_text.split("\n")])

        ttk.Label(content_frame, text="เนื้อหาภายใน:", font=("Arial", 12, "bold")).grid(row=len(details), column=1, sticky="nw", pady=(10, 0))

        summary_textbox = tk.Text(content_frame, wrap="word", font=("Arial", 12), height=10, width=60, bd=0)
        summary_textbox.insert("1.0", summary_text)
        summary_textbox.config(state="disabled")  # Disable editing
        summary_textbox.grid(row=len(details)+1, column=1, pady=10, sticky="w")

        # Create a frame for buttons
        button_frame = ttk.Frame(details_window)
        button_frame.pack(side="bottom", padx=20, pady=10, fill="x")

        # Create a "Borrow Book" button
        borrow_button = ttk.Button(
            button_frame,
            text="ยืมหนังสือเล่มนี้",
            command=lambda: self.member.borrow_book(book_details[2], book_details[3])
        )
        borrow_button.pack(side="left", padx=4, pady=10)

        # Create a "Back to Search" button
        back_button = ttk.Button(
            button_frame,
            text="กลับไปหน้าแรก",
            command=details_window.destroy  # Close the current window
        )
        back_button.pack(side="left", padx=4, pady=10)


    def confirm_borrowing(self):
        # ดึงค่าเลขบัตรประชาชนและ ISBN จาก input fields
        pid = self.member.card_id_var.get()
        book_isbn = self.member.isbn_var.get()

        # ตรวจสอบให้แน่ใจว่ามีข้อมูลเลขบัตรประชาชนและ ISBN หนังสือ
        if not pid:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลเลขบัตรประชาชน")
            return

        if not book_isbn:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกข้อมูล ISBN หนังสือ")
            return

        # ตรวจสอบ return_flag จากฐานข้อมูล (ต้องเรียก check_return_flag ก่อน)
        return_flag = check_return_flag(pid)  # ฟังก์ชันนี้ตรวจสอบว่าผู้ใช้มีหนังสือที่ยังไม่ได้คืนหรือไม่
        if return_flag == -1:
            messagebox.showerror("ข้อผิดพลาดฐานข้อมูล", "ไม่สามารถตรวจสอบข้อมูลการยืมได้ กรุณาลองใหม่")
            return
        
        # ตรวจสอบว่าผู้ใช้มีหนังสือที่ยังไม่ได้คืนเกิน 3 เล่มหรือไม่
        if return_flag >= 3:
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถยืมหนังสือได้ เนื่องจากเกินจำนวนการยืมสูงสุด (3 เล่ม)")
            return

        # ตรวจสอบว่าผู้ใช้เคยยืมหนังสือ ISBN นี้ไปแล้วหรือไม่
        if check_borrow_duplicate(pid, book_isbn):
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถยืมหนังสือเล่มนี้ซ้ำได้ เนื่องจากคุณยังไม่ได้คืนหนังสือเล่มนี้")
            return
        
        # ตรวจสอบจำนวนหนังสือในสต็อก
        book_stock = check_book_stock(book_isbn)  # ฟังก์ชันนี้จะตรวจสอบจำนวนหนังสือที่มีอยู่ในสต็อก
        if book_stock == 0:
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถยืมหนังสือได้เนื่องจากไม่มีหนังสือในสต็อก")
            return
        
        # ถ้ามีหนังสือในสต็อก ยืมหนังสือจากฐานข้อมูล
        if borrow_book_from_db(pid, book_isbn):
            # อัปเดตสต็อกหลังจากยืมหนังสือ
            update_book_stock(book_isbn)
            messagebox.showinfo("สำเร็จ", "การยืมหนังสือสำเร็จ")
        else:
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถยืมหนังสือได้ กรุณาลองใหม่อีกครั้ง")


class Staff:
    def __init__(self, root, library_gui, book):
        self.root = root
        self.library_gui = library_gui
        self.book = book
        self.book_name_entry = None
        self.isbn_entry = None
        self.results_frame = None
        self.results_tree = None

    def staff_add_book(self):
        # ล้างหน้าต่างก่อนตั้งค่าฟอร์มใหม่
        self.library_gui.clear_window()

        # ตั้งค่าขนาดหน้าต่างเริ่มต้น
        self.root.geometry("550x800")
        self.root.resizable(True, True)
        ttk.Label(self.root, text="เพิ่มหนังสือ", font=("Arial", 16, "bold")).pack()

        # สร้างเฟรมสำหรับแถบนำทาง (Navbar)
        self.library_gui.show_navbar()

        # สร้างเฟรมฟอร์มสำหรับเพิ่มหนังสือ
        self.add_book_form_frame = ttk.Frame(self.root)
        self.add_book_form_frame.pack(pady=20)

        # รูปภาพหนังสือ
        ttk.Label(self.add_book_form_frame, text="รูปภาพหนังสือ:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.image_path = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.image_path, width=40).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self.add_book_form_frame, text="เรียกดู", command=self.browse_image).grid(row=0, column=2, padx=10, pady=5)

        # ปุ่มแสดงตัวอย่างรูปภาพ
        self.preview_button = ttk.Button(self.add_book_form_frame, text="ดูตัวอย่าง", command=self.preview_image, state=tk.DISABLED)
        self.preview_button.grid(row=0, column=3, padx=10, pady=5)

        # แสดงตัวอย่างรูปภาพ
        self.image_preview_label = ttk.Label(self.root)
        self.image_preview_label.pack(pady=10)

        # ชื่อหนังสือ
        ttk.Label(self.add_book_form_frame, text="ชื่อหนังสือ:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.title_var = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.title_var, width=40).grid(row=2, column=1, padx=10, pady=5)

        # ผู้แต่ง
        ttk.Label(self.add_book_form_frame, text="ผู้แต่ง:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.author_var = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.author_var, width=40).grid(row=3, column=1, padx=10, pady=5)

        # สำนักพิมพ์
        ttk.Label(self.add_book_form_frame, text="สำนักพิมพ์:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.publisher_var = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.publisher_var, width=40).grid(row=4, column=1, padx=10, pady=5)

        # ISBN
        ttk.Label(self.add_book_form_frame, text="ISBN:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        self.isbn_var = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.isbn_var, width=40).grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_form_frame, text="จำนวนหน้า:").grid(row=6, column=0, padx=10, pady=5, sticky='e')
        self.page_var = tk.IntVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.page_var, width=40).grid(row=6, column=1, padx=10, pady=5)

        # จำนวนสต็อก
        ttk.Label(self.add_book_form_frame, text="จำนวนสต็อก:").grid(row=7, column=0, padx=10, pady=5, sticky='e')
        self.stock_var = tk.IntVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.stock_var, width=40).grid(row=7, column=1, padx=10, pady=5)

        # สร้าง category_map เพื่อแปลงหมวดหมู่เป็นรหัสตัวเลข
        self.category_map = {
            'เบ็ตเตล็ดหรือความรู้ทั่วไป (Generalities)': '000',
            'ปรัชญา (Philosophy)': '100',
            'ศาสนา (Religion)': '200',
            'สังคมศาสตร์ (Social Sciences)': '300',
            'ภาษาศาสตร์ (Language)': '400',
            'วิทยาศาสตร์ (Science)': '500',
            'วิทยาศาสตร์ประยุกต์ หรือเทคโนโลยี (Technology)': '600',
            'ศิลปกรรมและการบันเทิง (Arts and recreation)': '700',
            'วรรณคดี (Literature)': '800',
            'ประวัติศาสตร์และภูมิศาสตร์ (History and geography)': '900'
        }

        # หมวดหมู่ (ComboBox)
        ttk.Label(self.add_book_form_frame, text="หมวดหมู่:").grid(row=8, column=0, padx=10, pady=5, sticky='e')
        self.catalog_var = tk.StringVar()
        catalog_combobox = ttk.Combobox(self.add_book_form_frame, textvariable=self.catalog_var, width=37)
        catalog_combobox['values'] = list(self.category_map.keys())  # ใช้ key จาก category_map
        catalog_combobox.grid(row=8, column=1, padx=10, pady=5)

        # เนื้อหา
        ttk.Label(self.add_book_form_frame, text="เนื้อหา:").grid(row=9, column=0, padx=10, pady=5, sticky='e')
        self.detail_text = tk.Text(self.add_book_form_frame, height=10, width=30, wrap=tk.WORD)
        self.detail_text.grid(row=9, column=1, padx=10, pady=5)

        # สร้างกรอบสำหรับปุ่ม
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=10, side=tk.BOTTOM, fill=tk.X)

        # ปุ่มส่งข้อมูลและปุ่มกลับไปหน้าแรก
        add_book_button = ttk.Button(buttons_frame, text="เพิ่มหนังสือ", command=self.add_book)
        add_book_button.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        back_button = ttk.Button(buttons_frame, text="กลับไปหน้าแรก", command=self.book.reset_to_main_menu)
        back_button.grid(row=0, column=0, padx=10, sticky='w')



    def search_books_edit_books(self):
        # ล้างหน้าจอและปรับขนาดหน้าต่าง
        self.library_gui.clear_window()
        self.root.geometry("490x720")  # ปรับขนาดหน้าต่าง

        ttk.Label(self.root, text="แก้ไขหนังสือ", font=("Arial", 16, "bold")).pack()
        self.library_gui.show_navbar()  # สร้างแถบเมนูนำทาง

        # สร้างฟิลด์อินพุต (Entry)
        tk.Label(self.root, text="ชื่อหนังสือ:").pack()
        self.book_name_entry = ttk.Entry(self.root)
        self.book_name_entry.pack()

        tk.Label(self.root, text="ISBN:").pack()
        self.isbn_entry = ttk.Entry(self.root)
        self.isbn_entry.pack()

        # เพิ่มปุ่มค้นหา
        search_button = ttk.Button(self.root, text="ค้นหา", command=self.perform_search)
        search_button.pack(pady=10)

        # สร้าง Treeview สำหรับผลการค้นหา
        if self.results_tree is None:
            self.show_results_edit_books()  # สร้าง results_tree หากยังไม่มี

        # สร้าง frame สำหรับปุ่มด้านล่าง
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=10, side=tk.BOTTOM, fill=tk.X)

        # สร้างปุ่มกลับไปหน้าแรก
        back_button = ttk.Button(buttons_frame, text="กลับไปหน้าแรก", command=self.book.reset_to_main_menu)
        back_button.grid(row=0, column=0, padx=10, sticky='w')

    def perform_search(self):
        # ดึงค่าจากฟิลด์อินพุต
        book_name = self.book_name_entry.get()  # อ้างอิงตัวแปรให้ถูกต้อง
        isbn = self.isbn_entry.get()  # อ้างอิงตัวแปรให้ถูกต้อง

        # ตรวจสอบว่ากรอกข้อมูลแค่ตัวเลือกเดียว
        search_criteria_count = sum([bool(book_name), bool(isbn)])
        
        if search_criteria_count > 1:
            messagebox.showwarning("คำเตือน", "กรุณากรอกข้อมูลเพียงตัวเลือกเดียวเท่านั้น")
            return

        # ล้างผลการค้นหาก่อนหน้า
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)

        # ค้นหาตามข้อมูลที่กรอกเข้ามา
        if book_name:
            result = search_edit_books_by_title(book_name)
        elif isbn:
            result = search_edit_books_by_isbn(isbn)

        # จัดการผลการค้นหา
        if isinstance(result, str) and "Error in connection" in result:
            messagebox.showerror("ข้อผิดพลาด", result)
        elif isinstance(result, str):
            messagebox.showinfo("ผลการค้นหา", result)
        else:
            # แสดงผลการค้นหาใน treeview
            for index, book in enumerate(result):
                self.results_tree.insert("", "end", values=(
                    book.get('book_title', 'N/A'),
                    book.get('book_isbn', 'N/A'),
                    book.get('book_publisher', 'N/A'),
                    book.get('catalog_name', 'N/A')
                ))

        # ซ่อน search_frame และแสดง results_frame
        self.results_frame.pack(fill="both", expand=True)


    def show_add_book_form(self):
        # แสดงฟอร์มเพิ่มหนังสือ (สลับการแสดงผลหรือสร้างฟอร์มใหม่)
        self.staff_add_book()


    def show_results_edit_books(self):
        if self.results_frame is None:
            self.results_frame = ttk.Frame(self.root, padding=10)

            # Clear any existing frames except the results_frame
            for widget in self.root.winfo_children():
                if isinstance(widget, ttk.Frame) and widget != self.results_frame:
                    widget.pack_forget()  # Hides other frames

            self.results_header = ttk.Label(self.results_frame, text="ผลลัพธ์การค้นหา", font=("Arial", 18))
            self.results_header.pack(pady=10)

            # Setup the Treeview
            self.results_tree = ttk.Treeview(self.results_frame, columns=("Title", "ISBN", "Publisher", "Category"), show='headings')

            # Set column headings
            self.results_tree.heading("Title", text="ชื่อหนังสือ")
            self.results_tree.heading("ISBN", text="เลข ISBN")
            self.results_tree.heading("Publisher", text="สำนักพิมพ์")
            self.results_tree.heading("Category", text="หมวดหมู่")

            # Set column widths
            self.results_tree.column("Title", width=200, anchor="w")
            self.results_tree.column("ISBN", width=120, anchor="w")
            self.results_tree.column("Publisher", width=150, anchor="w")
            self.results_tree.column("Category", width=120, anchor="w")

            self.results_tree.pack(padx=10, pady=10, fill="both", expand=True)

            # Bind double-click event
            self.results_tree.bind("<Double-1>", self.on_edit_book_select)

            # Show the results frame
            self.results_frame.pack(fill="both", expand=True)

            # Adjust window size to fit results
            self.results_frame.master.geometry("1200x600")



    def edit_book(self):
        # ตรวจสอบความถูกต้องของฟิลด์ในฟอร์ม
        book_title = self.title_var.get()
        book_author = self.author_var.get()
        book_publisher = self.publisher_var.get()
        book_isbn = self.isbn_var.get()
        book_stock = self.stock_var.get()
        book_detail = self.detail_text.get("1.0", "end-1c")
        selected_category = self.catalog_var.get()

        # แปลงหมวดหมู่ที่เลือกเป็นรหัสตัวเลข 3 หลัก
        catalog_num = self.category_map.get(selected_category, None)
        if catalog_num is None:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกหมวดหมู่ที่ถูกต้อง")
            return

        # แปลงรูปภาพเป็น base64 ถ้ามีการระบุเส้นทางของรูปภาพ
        book_cover_id = self.image_path.get()  # สมมติว่าเป็นเส้นทางหรือ ID สำหรับภาพปกหนังสือ
        encoded_image = None
        if book_cover_id:
            try:
                with open(book_cover_id, 'rb') as image_file:
                    image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode('utf-8')  # เข้ารหัส base64
            except FileNotFoundError:
                messagebox.showerror("ข้อผิดพลาด", "ไม่พบไฟล์รูปภาพที่ระบุ")
                return
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการแปลงรูปภาพ: {e}")
                return

        # เพิ่มหนังสือเข้าไปในฐานข้อมูล
        try:
            book_id = update_book(
                book_title,
                book_author,
                book_publisher,
                book_isbn,
                book_stock,
                catalog_num,  # ส่งรหัสหมวดหมู่ที่มี 3 หลัก
                book_detail,
                encoded_image  # ส่งข้อมูลรูปภาพที่เข้ารหัส
            )
            messagebox.showinfo("สำเร็จ", "ข้อมูลหนังสือถูกแก้ไขเรียบร้อยแล้ว")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการแก้ไขข้อมูลหนังสือ: {e}")


    def add_book(self):
        # ดึงค่าจากฟิลด์ในฟอร์ม
        book_title = self.title_var.get()
        book_author = self.author_var.get()
        book_publisher = self.publisher_var.get()
        book_isbn = self.isbn_var.get()
        book_page = self.page_var.get()
        book_stock = self.stock_var.get()
        book_detail = self.detail_text.get("1.0", "end-1c")
        selected_category = self.catalog_var.get()

        # ตรวจสอบฟิลด์ที่จำเป็น
        if not all([book_title, book_author, book_publisher, book_isbn,book_page, book_stock, selected_category]):
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกข้อมูลให้ครบถ้วน")
            return

        # # ตรวจสอบรูปแบบ ISBN (ตัวอย่างพื้นฐาน)
        # if len(book_isbn) != 13 or not book_isbn.isdigit():
        #     messagebox.showerror("ข้อผิดพลาด", "กรุณากรอก ISBN ให้ถูกต้อง (13 หลัก)")
        #     return

        # แปลงหมวดหมู่ที่เลือกเป็นรหัสตัวเลข
        catalog_num = self.category_map.get(selected_category, None)
        if catalog_num is None:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกหมวดหมู่ที่ถูกต้อง")
            return

        # จัดการภาพปกหนังสือ
        book_cover_id = self.image_path.get()  # สมมติว่านี่คือเส้นทางของภาพปกหนังสือ
        encoded_image = None
        if book_cover_id:
            try:
                with open(book_cover_id, 'rb') as image_file:
                    image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode('utf-8')  # เข้ารหัสเป็น Base64
            except FileNotFoundError:
                messagebox.showerror("ข้อผิดพลาด", "ไม่พบไฟล์รูปภาพที่ระบุ")
                return
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการแปลงรูปภาพ: {e}")
                return

        # เพิ่มหนังสือลงในฐานข้อมูล
        try:
            book_id = insert_book(
                book_title,
                book_author,
                book_publisher,
                book_isbn,
                book_page,
                book_stock,
                catalog_num,  # ส่งรหัสหมวดหมู่
                book_detail,
                encoded_image  # ส่งข้อมูลรูปภาพที่เข้ารหัส
            )
            messagebox.showinfo("สำเร็จ", "ข้อมูลหนังสือถูกเพิ่มเรียบร้อยแล้ว")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการเพิ่มข้อมูลหนังสือ: {e}")


    @staticmethod
    def encode_image(file_path):
        try:
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการเข้ารหัสรูปภาพ: {e}")
            return None


    def browse_image(self):
        # เปิดหน้าต่างให้เลือกไฟล์รูปภาพ
        file_path = filedialog.askopenfilename(
            title="เลือกรูปภาพ",
            filetypes=[("ไฟล์รูปภาพ", "*.jpg;*.jpeg;*.png;*.gif")]
        )
        if file_path:
            self.image_path.set(file_path)
            self.preview_button.config(state=tk.NORMAL)  # เปิดใช้งานปุ่มพรีวิวเมื่อเลือกไฟล์


    def preview_image(self):
        # แสดงพรีวิวรูปภาพ
        file_path = self.image_path.get()
        if file_path:
            self.show_image_preview(file_path)


    def show_image_preview(self, file_path):
        img = Image.open(file_path)
        img = img.resize((150, 200), Image.Resampling.LANCZOS)  # เปลี่ยนจาก Image.ANTIALIAS เป็น Image.Resampling.LANCZOS
        img_tk = ImageTk.PhotoImage(img)  # แปลงรูปภาพให้เป็นฟอร์แมตที่แสดงผลได้ใน Tkinter

        # อัปเดต label ให้แสดงพรีวิวรูปภาพ
        self.image_preview_label.config(image=img_tk)
        self.image_preview_label.image = img_tk  # เก็บ reference ของรูปภาพเพื่อป้องกันการถูกลบจากหน่วยความจำ


    def validate_fields(self):
        # ตรวจสอบว่ามีการกรอกข้อมูลครบทุกช่องหรือไม่
        if not self.image_path.get() or not self.title_var.get() or not self.author_var.get() or \
        not self.publisher_var.get() or not self.isbn_var.get() or self.stock_var.get() == 0 or \
        not self.catalog_var.get():
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
        else:
            self.add_book()


    def on_edit_book_select(self, event):
        # รับข้อมูลที่เลือกจาก Treeview
        selected_item = self.results_tree.focus()
        book_data = self.results_tree.item(selected_item)['values']

        # ตรวจสอบให้แน่ใจว่ามีข้อมูลเพียงพอ
        if len(book_data) < 3:  # ต้องมีอย่างน้อยชื่อหนังสือ, ISBN, สำนักพิมพ์
            messagebox.showerror("ข้อผิดพลาด", "ข้อมูลหนังสือไม่ครบถ้วน")
            return

        # ดึงข้อมูลจากฐานข้อมูลโดยใช้ ISBN
        isbn = book_data[1]  # สมมติว่า ISBN อยู่ในตำแหน่งที่ 1
        book_info = search_edit_books_by_isbn(isbn)

        if isinstance(book_info, str):  # ตรวจสอบว่ามีข้อผิดพลาด
            messagebox.showerror("ข้อผิดพลาด", book_info)
            return

        # ดึงข้อมูลจาก book_info
        if book_info:
            title = book_info[0]["book_title"]
            publisher = book_info[0]["book_publisher"]
            stock = book_info[0]["book_stock"]
            detail = book_info[0]["book_detail"]
            category = book_info[0]["catalog_name"]
            cover_id = book_info[0]["book_cover_id"]  # ดึง book_cover_id
            # ดึงรูปภาพจากฐานข้อมูล
            cover_image = get_cover_image(isbn, cover_id)  # ฟังก์ชันใหม่ที่จะสร้าง
        else:
            messagebox.showerror("ข้อผิดพลาด", "ไม่พบข้อมูลหนังสือในฐานข้อมูล")
            return

        # ล้างหน้าต่างเพื่อแสดงฟอร์มการแก้ไข
        self.library_gui.clear_window()

        # ตั้งค่าขนาดหน้าต่างเริ่มต้นสำหรับฟอร์มการแก้ไข
        self.root.geometry("550x1000")
        ttk.Label(self.root, text="แก้ไขหนังสือ", font=("Arial", 18)).pack()

        # เพิ่มแถบนำทาง (ถ้าจำเป็น)
        self.library_gui.show_navbar()

        # สร้างฟอร์มสำหรับแก้ไขข้อมูล
        self.add_book_form_frame = ttk.Frame(self.root)
        self.add_book_form_frame.pack(pady=20)

        # ช่องสำหรับรูปภาพหนังสือ
        ttk.Label(self.add_book_form_frame, text="รูปภาพหนังสือ:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.image_path = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.image_path, width=40).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self.add_book_form_frame, text="เรียกดู", command=self.browse_image).grid(row=0, column=2, padx=10, pady=5)

        # ปุ่มแสดงตัวอย่างรูปภาพ
        self.preview_button = ttk.Button(self.add_book_form_frame, text="ดูตัวอย่าง", command=self.preview_image, state=tk.DISABLED)
        self.preview_button.grid(row=0, column=3, padx=10, pady=5)

        # แสดงตัวอย่างรูปภาพ
        self.image_preview_label = ttk.Label(self.root)
        self.image_preview_label.pack(pady=10)

        # สร้างกรอบสำหรับแสดงรูปภาพ
        self.cover_frame = ttk.Frame(self.add_book_form_frame, width=150, height=200)
        self.cover_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        # แสดงรูปภาพปกหนังสือใหม่
        if cover_id:
            try:
                # ถอดรหัสรูปภาพจาก base64
                image_data = base64.b64decode(cover_id)
                cover_image = Image.open(io.BytesIO(image_data))

                # ปรับขนาดภาพให้เหมาะสมกับกรอบ (ทำการปรับขนาดก่อนสร้าง PhotoImage)
                cover_image = cover_image.resize((150, 200), Image.Resampling.LANCZOS)  # ปรับขนาดภาพให้พอดีกับกรอบ 150x200 พิกเซล
                cover_image_tk = ImageTk.PhotoImage(cover_image)

                # อัปเดตรูปภาพในกรอบ
                cover_label = ttk.Label(self.cover_frame, image=cover_image_tk)
                cover_label.image = cover_image_tk  # เก็บการอ้างอิงไม่ให้รูปหายไป
                cover_label.pack(expand=True, fill='both')

            except Exception as e:
                # แสดงข้อความในกรณีที่เกิดข้อผิดพลาดในการแสดงภาพ
                print(f"เกิดข้อผิดพลาดในการแสดงภาพ: {e}")
                error_label = ttk.Label(self.cover_frame, text="ไม่สามารถแสดงรูปภาพปกหนังสือ", font=("Arial", 12, "bold"))
                error_label.pack(expand=True, fill='both')
        else:
            # แสดงข้อความว่าไม่มีรูปภาพ
            no_image_label = ttk.Label(self.cover_frame, text="ไม่มีรูปภาพ", font=("Arial", 12))
            no_image_label.pack(expand=True, fill='both')

        # ชื่อหนังสือ
        ttk.Label(self.add_book_form_frame, text="ชื่อหนังสือ:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.title_var = tk.StringVar(value=title)
        ttk.Entry(self.add_book_form_frame, textvariable=self.title_var, width=40).grid(row=2, column=1, padx=10, pady=5)

        # สำนักพิมพ์
        ttk.Label(self.add_book_form_frame, text="สำนักพิมพ์:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.publisher_var = tk.StringVar(value=publisher)
        ttk.Entry(self.add_book_form_frame, textvariable=self.publisher_var, width=40).grid(row=3, column=1, padx=10, pady=5)

        # ISBN
        ttk.Label(self.add_book_form_frame, text="ISBN:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.isbn_var = tk.StringVar(value=isbn)
        ttk.Entry(self.add_book_form_frame, textvariable=self.isbn_var, width=40).grid(row=4, column=1, padx=10, pady=5)

        # จำนวนสต็อก
        ttk.Label(self.add_book_form_frame, text="จำนวนสต็อก:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        self.stock_var = tk.IntVar(value=stock)
        ttk.Entry(self.add_book_form_frame, textvariable=self.stock_var, width=40).grid(row=5, column=1, padx=10, pady=5)

        # สร้าง category_map เพื่อแปลงหมวดหมู่เป็นรหัสตัวเลข
        self.category_map = {
            'เบ็ตเตล็ดหรือความรู้ทั่วไป (Generalities)': '000',
            'ปรัชญา (Philosophy)': '100',
            'ศาสนา (Religion)': '200',
            'สังคมศาสตร์ (Social Sciences)': '300',
            'ภาษาศาสตร์ (Language)': '400',
            'วิทยาศาสตร์ (Science)': '500',
            'วิทยาศาสตร์ประยุกต์ หรือเทคโนโลยี (Technology)': '600',
            'ศิลปกรรมและการบันเทิง (Arts and recreation)': '700',
            'วรรณคดี (Literature)': '800',
            'ประวัติศาสตร์และภูมิศาสตร์ (History and geography)': '900'
        }

        # Combobox หมวดหมู่
        ttk.Label(self.add_book_form_frame, text="หมวดหมู่:").grid(row=6, column=0, padx=10, pady=5, sticky='e')
        self.catalog_var = tk.StringVar(value=category)
        catalog_combobox = ttk.Combobox(self.add_book_form_frame, textvariable=self.catalog_var, width=37)
        catalog_combobox['values'] = list(self.category_map.keys())
        catalog_combobox.grid(row=6, column=1, padx=10, pady=5)

        # เนื้อหา
        ttk.Label(self.add_book_form_frame, text="เนื้อหา:").grid(row=7, column=0, padx=10, pady=5, sticky='e')
        self.detail_text = tk.Text(self.add_book_form_frame, height=10, width=30, wrap=tk.WORD)
        self.detail_text.insert(tk.END, detail)
        self.detail_text.grid(row=8, column=1, padx=10, pady=5)

        # ปุ่มบันทึกและปุ่มกลับ
        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=10, side=tk.BOTTOM, fill=tk.X)
        add_book_button = ttk.Button(buttons_frame, text="บันทึกข้อมูล", command=self.edit_book)
        add_book_button.pack(side=tk.LEFT, padx=10, pady=5)
        back_button = ttk.Button(buttons_frame, text="กลับ", command=self.book.reset_to_main_menu)
        back_button.pack(side=tk.LEFT, padx=10, pady=5)
 

class Library:
    def __init__(self, root, book):
        self.root = root
        self.results_frame = None
        self.results_tree = None
        self.book = book

    def show_results(self):
        if self.results_frame is None:
            self.results_frame = ttk.Frame(self.root, relief="sunken", padding=(10, 10))  # Add padding

            self.results_header = ttk.Label(self.results_frame, text="ผลลัพธ์การค้นหา", font=("Arial", 18))
            self.results_header.pack(pady=10)

            self.results_tree = ttk.Treeview(self.results_frame, columns=("Number", "Book_on", "Title", "ISBN", "Publisher", "Category"), show='headings')

            # Set column headings
            self.results_tree.heading("Number", text="ลำดับ")
            self.results_tree.heading("Book_on", text="เลขหนังสือ")
            self.results_tree.heading("Title", text="ชื่อหนังสือ")
            self.results_tree.heading("ISBN", text="เลข ISBN")
            self.results_tree.heading("Publisher", text="สำนักพิมพ์")
            self.results_tree.heading("Category", text="หมวดหมู่")

            # Set column widths
            self.results_tree.column("Number", width=80, anchor="center")
            self.results_tree.column("Book_on", width=100, anchor="center")
            self.results_tree.column("Title", width=200, anchor="w")
            self.results_tree.column("ISBN", width=120, anchor="w")
            self.results_tree.column("Publisher", width=150, anchor="w")

            self.results_tree.pack(padx=10, pady=10, fill="both", expand=True)

            self.results_tree.bind("<Double-1>", self.book.on_book_select)

            self.results_back_button = ttk.Button(self.results_frame, text="กลับ", width=10, command=self.book.reset_to_main_menu)
            self.results_back_button.pack(side="left", padx=20, pady=10)

        # Adjust the size of the results window
        self.results_frame.pack(fill="both", expand=True)
        # Set the size of the window displaying the results
        self.results_frame.master.geometry("1200x600")


# Main program to run the GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryGUI(root)
    root.mainloop()