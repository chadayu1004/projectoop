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
    def __init__(self, root, library):
        self.root = root
        self.library = library
        self.process = None
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.title("โปรแกรมจัดการห้องสมุด")
        self.root.geometry("450x600")
        self.initialize_main_menu()  
        self.results_frame = None 
        self.results_tree = None 

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.results_frame = None
        self.results_tree = None
        self.search_frame = None

    def initialize_main_menu(self):
        self.root.geometry("450x600")
        self.root.resizable(False, False)
        
        self.header = ttk.Label(self.root, text="โปรแกรมจัดการห้องสมุด", font=("Arial", 20))
        self.header.pack(pady=20)

        image = Image.open("main_menu.png")
        image = image.resize((200, 200), Image.Resampling.LANCZOS)
        self.image = ImageTk.PhotoImage(image)

        self.image_label = ttk.Label(self.root, image=self.image)
        self.image_label.pack(pady=5)

        self.subheader = ttk.Label(self.root, text="กรุณาเลือกเมนูที่ต้องการใช้งาน", font=("Arial", 14))
        self.subheader.pack(pady=5)

        self.button_frame = ttk.Frame(self.root)
        self.button_frame.pack(pady=20)

        self.search_button = ttk.Button(self.button_frame, text="ค้นหา/ยืม หนังสือ", width=25, command=self.show_search_form)
        self.search_button.grid(row=0, column=0, padx=10, pady=10)

        self.borrow_return_button = ttk.Button(self.button_frame, text="คืนหนังสือ", width=25, command=self.borrow_return_books)
        self.borrow_return_button.grid(row=1, column=0, padx=10, pady=10)

        self.staff_button = ttk.Button(self.button_frame, text="สำหรับเจ้าหน้าที่", width=25, command=self.staff)
        self.staff_button.grid(row=2, column=0, padx=10, pady=10)

        self.bottom_frame = ttk.Frame(self.root)
        self.bottom_frame.pack(side="bottom", fill="x", pady=10)

        self.easter_egg_button = ttk.Button(self.bottom_frame, text="สถานะการเชื่อมต่อ", width=15, command=self.test_db_connection)
        self.easter_egg_button.pack(side="left", padx=20)

        self.resource_button = ttk.Button(self.bottom_frame, text="SQL Web Socket", width=15, command=self.SQL_Web_Socket)
        self.resource_button.pack(side="left", padx=20, expand=True)

        self.about_button = ttk.Button(self.bottom_frame, text="เกี่ยวกับ", width=15, command=self.open_about)
        self.about_button.pack(side="right", padx=20)

    def SQL_Web_Socket(self):
        batch_file_path = r"library_oob.bat"  
        try:
            self.process = subprocess.Popen(
                ['cmd.exe', '/k', batch_file_path],
                creationflags=subprocess.CREATE_NEW_CONSOLE  
            )
        except Exception as e:
            messagebox.showerror("Error", f"ไม่สามารถรันไฟล์ Batch ได้: {str(e)}")

    def on_close(self):
        if messagebox.askokcancel("Quit", "คุณแน่ใจว่าต้องการปิดโปรแกรม?"):
            if self.process is not None:
                # ปิด subprocess
                self.process.terminate()
                self.process = None            
            self.root.destroy() 

    def open_about(self):
        about_window = Toplevel(self.root)
        about_window.title("เกี่ยวกับ")

        header_label = ttk.Label(about_window, text="เกี่ยวกับ", font=("Arial", 16, "bold"))
        header_label.pack(pady=10)

        frame = ttk.Frame(about_window)
        frame.pack(expand=True)

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

        about_label = ttk.Label(frame, text=about_text, justify="center", padding=(10, 10))
        about_label.pack()

        url = "https://shorturl.at/KHVqb"
        link_label = ttk.Label(frame, text=url, font=("Arial", 12, "underline"), foreground="blue", cursor="hand2")


        link_label.pack(pady=5)
        link_label.bind("<Button-1>", lambda e: webbrowser.open_new(url))

        try:
            original_image = Image.open("qr-manual.png")
            size = (100, 100)  
            resized_image = original_image.resize(size, Image.Resampling.LANCZOS)
            qr_image = ImageTk.PhotoImage(resized_image)

            qr_label = ttk.Label(frame, image=qr_image)
            qr_label.image = qr_image  
            qr_label.pack(pady=10)
        except Exception as e:
            error_label = ttk.Label(frame, text="ไม่สามารถโหลด QR Code ได้", foreground="red")
            error_label.pack(pady=10)

        close_button = ttk.Button(about_window, text="ปิด", command=about_window.destroy)
        close_button.pack(pady=10)  

    def initialize_search_frame(self):
        if not hasattr(self, 'search_frame') or self.search_frame is None:
            self.search_frame = ttk.Frame(self.root, padding="10")
            
            self.search_header = ttk.Label(self.search_frame, text="ค้นหาหนังสือ", font=("Arial", 18))
            self.search_header.pack(pady=10)

            image = Image.open("search_pic.png")
            image = image.resize((int(1.50 * 90), int(1.25 * 90)), Image.Resampling.LANCZOS) 
            image = ImageTk.PhotoImage(image)  
            
            image_label = ttk.Label(self.search_frame, image=image)
            image_label.image = image  
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

        self.header.pack_forget()
        self.subheader.pack_forget()
        self.button_frame.pack_forget()
        self.staff_button.pack_forget()
        self.easter_egg_button.pack_forget()
        self.resource_button.pack_forget()
        self.about_button.pack_forget()
        self.image_label.pack_forget()
        self.search_frame.pack(fill="both", expand=True)

    def reset_to_main_menu(self):
        self.clear_window()
        self.initialize_main_menu()

    def staff(self):
        self.clear_window()

        self.root.geometry("350x500")

        self.root.grid_rowconfigure(0, weight=1)  
        self.root.grid_rowconfigure(8, weight=1) 
        self.root.grid_columnconfigure(0, weight=1)  

        self.title_label = ttk.Label(self.root, text="เข้าสู่ระบบสำหรับเจ้าหน้าที่", font=("Arial", 14, "bold"))
        self.title_label.grid(row=0, column=0, pady=10, padx=40, sticky="n")

        image_path = "user_icon.png"  
        image = Image.open(image_path)
        image = image.resize((200, 150), Image.Resampling.LANCZOS) 
        self.image = ImageTk.PhotoImage(image)
        self.image_label = ttk.Label(self.root, image=self.image)
        self.image_label.grid(row=1, column=0, pady=5, padx=40, sticky="n")

        self.instruction_label = ttk.Label(self.root, text="กรุณากรอกชื่อผู้ใช้และรหัสผ่าน", font=("Arial", 12))
        self.instruction_label.grid(row=2, column=0, pady=5, padx=40, sticky="n")

        self.username_label = ttk.Label(self.root, text="ชื่อผู้ใช้", font=("Arial", 12))
        self.username_label.grid(row=3, column=0, pady=5, padx=40, sticky="nw")

        self.username_entry = ttk.Entry(self.root, font=("Arial", 12), width=30)
        self.username_entry.grid(row=4, column=0, pady=5, padx=40, sticky="ew") 

        self.password_label = ttk.Label(self.root, text="รหัสผ่าน", font=("Arial", 12))
        self.password_label.grid(row=5, column=0, pady=5, padx=40, sticky="nw")

        self.password_entry = ttk.Entry(self.root, show='*', font=("Arial", 12), width=30)
        self.password_entry.grid(row=6, column=0, pady=5, padx=40, sticky="ew")  

        self.login_button = ttk.Button(self.root, text="เข้าสู่ระบบ", command=self.login)
        self.login_button.grid(row=7, column=0, pady=(5, 5), padx=40, sticky="ew")  
        self.login_button.config(style='TButton')

        self.back_button = ttk.Button(self.root, text="กลับไปหน้าแรก", command=self.reset_to_main_menu)
        self.back_button.grid(row=8, column=0, pady=(5, 5), padx=40, sticky="ew")  
        self.back_button.config(style='TButton')

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if staff_admin(username, password):
            messagebox.showinfo("เข้าสู่ระบบ", "เข้าสู่ระบบสำเร็จ!")
            self.staff_add_book()
        else:
            messagebox.showerror("เข้าสู่ระบบ", "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้ง.")

    def show_navbar(self):
        navbar_frame = ttk.Frame(self.root, padding=5)
        navbar_frame.pack(fill=tk.X)

        add_book_button = ttk.Button(navbar_frame, text="เพิ่มหนังสือ", command=self.show_add_book_form)
        add_book_button.pack(side=tk.LEFT, padx=10, pady=10)

        edit_book_button = ttk.Button(navbar_frame, text="แก้ไขหนังสือ", command=self.search_books_edit_books)
        edit_book_button.pack(side=tk.LEFT, padx=10, pady=10)

    def staff_add_book(self):
        self.clear_window()

        self.root.geometry("550x880")
        self.root.resizable(False, False)
        ttk.Label(self.root, text="เพิ่มหนังสือ", font=("Arial", 16, "bold")).pack()

        self.show_navbar()

        self.add_book_form_frame = ttk.Frame(self.root)
        self.add_book_form_frame.pack(pady=20)

        ttk.Label(self.add_book_form_frame, text="รูปภาพหนังสือ:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.image_path = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.image_path, width=40).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self.add_book_form_frame, text="เรียกดู", command=self.browse_image).grid(row=0, column=2, padx=10, pady=5)

        self.preview_button = ttk.Button(self.add_book_form_frame, text="ดูตัวอย่าง", command=self.preview_image_add, state=tk.DISABLED)
        self.preview_button.grid(row=0, column=3, padx=10, pady=5)

        self.image_preview_label = ttk.Label(self.root)
        self.image_preview_label.pack(pady=10)
        
        self.cover_frame = ttk.Frame(self.add_book_form_frame, width=150, height=200, relief="groove", borderwidth=2)
        self.cover_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        self.image_placeholder_label = ttk.Label(self.cover_frame, text="รูปแสดงตัวอย่างจะปรากฏที่นี่", anchor="center")
        self.image_placeholder_label.place(relx=0.5, rely=0.5, anchor="center")

        ttk.Label(self.add_book_form_frame, text="ชื่อหนังสือ:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.title_var = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.title_var, width=40).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_form_frame, text="ผู้แต่ง:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.author_var = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.author_var, width=40).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_form_frame, text="สำนักพิมพ์:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.publisher_var = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.publisher_var, width=40).grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_form_frame, text="ISBN:").grid(row=6, column=0, padx=10, pady=5, sticky='e')
        self.isbn_var = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.isbn_var, width=40).grid(row=5, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_form_frame, text="จำนวนหน้า:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        self.page_var = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.page_var, width=40).grid(row=6, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_form_frame, text="จำนวนสต็อก:").grid(row=7, column=0, padx=10, pady=5, sticky='e')
        self.stock_var = tk.IntVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.stock_var, width=40).grid(row=7, column=1, padx=10, pady=5)

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

        ttk.Label(self.add_book_form_frame, text="หมวดหมู่:").grid(row=8, column=0, padx=10, pady=5, sticky='e')
        self.catalog_var = tk.StringVar()
        catalog_combobox = ttk.Combobox(self.add_book_form_frame, textvariable=self.catalog_var, width=37)
        catalog_combobox['values'] = list(self.category_map.keys())  # ใช้ key จาก category_map
        catalog_combobox.grid(row=8, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_form_frame, text="เนื้อหา:").grid(row=9, column=0, padx=10, pady=5, sticky='e')
        self.detail_text = tk.Text(self.add_book_form_frame, height=10, width=30, wrap=tk.WORD)
        self.detail_text.grid(row=9, column=1, padx=10, pady=5)

        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=10, side=tk.BOTTOM, fill=tk.X)

        add_book_button = ttk.Button(buttons_frame, text="เพิ่มหนังสือ", command=self.add_book)
        add_book_button.grid(row=0, column=1, padx=10, pady=10, sticky='w')

        back_button = ttk.Button(buttons_frame, text="กลับไปหน้าแรก", command=self.reset_to_main_menu)
        back_button.grid(row=0, column=0, padx=10, sticky='w')

    def show_add_book_form(self):
        self.staff_add_book()

    def search_books_edit_books(self):
        self.clear_window()
        
        self.root.geometry("490x720")  
        ttk.Label(self.root, text="แก้ไขหนังสือ", font=("Arial", 16, "bold")).pack()
        self.show_navbar()  

        tk.Label(self.root, text="ชื่อหนังสือ:").pack()
        self.book_name_entry = ttk.Entry(self.root)
        self.book_name_entry.pack()

        tk.Label(self.root, text="ISBN:").pack()
        self.isbn_entry = ttk.Entry(self.root)
        self.isbn_entry.pack()

        search_button = ttk.Button(self.root, text="ค้นหา", command=self.perform_search)
        search_button.pack(pady=10)

        if self.results_tree is None:
            self.show_results_edit_books()  

        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=10, side=tk.BOTTOM, fill=tk.X)

        back_button = ttk.Button(buttons_frame, text="กลับไปหน้าแรก", command=self.reset_to_main_menu)
        back_button.grid(row=0, column=0, padx=10, sticky='w')

    def perform_search(self):
            book_name = self.book_name_entry.get()
            isbn = self.isbn_entry.get()

            search_criteria_count = sum([bool(book_name), bool(isbn)])
            
            if search_criteria_count > 1:
                messagebox.showwarning("คำเตือน", "กรุณากรอกข้อมูลเพียงตัวเลือกเดียวเท่านั้น")
                return

            for row in self.results_tree.get_children():
                self.results_tree.delete(row)

            if book_name:
                result = search_edit_books_by_title(book_name)
            elif isbn:
                result = search_edit_books_by_isbn(isbn)

            if isinstance(result, str) and "Error in connection" in result:
                messagebox.showerror("ข้อผิดพลาด", result)
            elif isinstance(result, str):
                messagebox.showinfo("ผลการค้นหา", result)
            else:
                for index, book in enumerate(result):
                    self.results_tree.insert("", "end", values=(
                        book.get('book_title', 'N/A'),
                        book.get('book_isbn', 'N/A'),
                        book.get('book_publisher', 'N/A'),
                        book.get('catalog_name', 'N/A')
                    ))

            if self.search_frame is not None:
                     self.search_frame.pack_forget()
                     self.results_frame.pack(fill="both", expand=True)

    def show_results_edit_books(self):
        if self.results_frame is None:
            self.results_frame = ttk.Frame(self.root, padding=10)

            self.results_header = ttk.Label(self.results_frame, text="ผลลัพธ์การค้นหา", font=("Arial", 18))
            self.results_header.pack(pady=10)

            self.results_tree = ttk.Treeview(self.results_frame, columns=("Title", "ISBN", "Publisher", "Category"), show='headings')

            self.results_tree.heading("Title", text="ชื่อหนังสือ")
            self.results_tree.heading("ISBN", text="เลข ISBN")
            self.results_tree.heading("Publisher", text="สำนักพิมพ์")
            self.results_tree.heading("Category", text="หมวดหมู่")

            self.results_tree.column("Title", width=200, anchor="w")
            self.results_tree.column("ISBN", width=120, anchor="w")
            self.results_tree.column("Publisher", width=150, anchor="w")
            self.results_tree.column("Category", width=120, anchor="w")

            self.results_tree.pack(padx=10, pady=10, fill="both", expand=True)

            self.results_tree.bind("<Double-1>", self.on_edit_book_select)

            self.results_frame.pack(fill="both", expand=True)
            self.results_frame.master.geometry("1200x600")

    def on_edit_book_select(self, event):
        selected_item = self.results_tree.focus()
        book_data = self.results_tree.item(selected_item)['values']

        if len(book_data) < 3: 
            messagebox.showerror("ข้อผิดพลาด", "ข้อมูลหนังสือไม่ครบถ้วน")
            return

        isbn = book_data[1]  
        book_info = search_edit_books_by_isbn(isbn)

        if isinstance(book_info, str):  
            messagebox.showerror("ข้อผิดพลาด", book_info)
            return

        if book_info:
            title = book_info[0]["book_title"]
            publisher = book_info[0]["book_publisher"]
            stock = book_info[0]["book_stock"]
            detail = book_info[0]["book_detail"]
            category = book_info[0]["catalog_name"]
            cover_id = book_info[0]["book_cover_id"]  
            cover_image = get_cover_image(isbn, cover_id)  
        else:
            messagebox.showerror("ข้อผิดพลาด", "ไม่พบข้อมูลหนังสือในฐานข้อมูล")
            return

        self.clear_window()
        self.root.geometry("550x880")
        ttk.Label(self.root, text="แก้ไขหนังสือ", font=("Arial", 18)).pack()

        self.show_navbar()
        self.add_book_form_frame = ttk.Frame(self.root)
        self.add_book_form_frame.pack(pady=20)

        ttk.Label(self.add_book_form_frame, text="รูปภาพหนังสือ:").grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.image_path = tk.StringVar()
        ttk.Entry(self.add_book_form_frame, textvariable=self.image_path, width=40).grid(row=0, column=1, padx=10, pady=5)
        ttk.Button(self.add_book_form_frame, text="เรียกดู", command=self.browse_image).grid(row=0, column=2, padx=10, pady=5)

        self.preview_button = ttk.Button(self.add_book_form_frame, text="ดูตัวอย่าง", command=self.preview_image_edit,state=tk.DISABLED)
        self.preview_button.grid(row=0, column=3, padx=10, pady=5)

        self.image_preview_label = ttk.Label(self.root)
        self.image_preview_label.pack(pady=10)

        self.cover_frame = ttk.Frame(self.add_book_form_frame, width=150, height=200)
        self.cover_frame.grid(row=1, column=0, columnspan=3, padx=10, pady=5)

        if cover_id:
            try:
                image_data = base64.b64decode(cover_id)
                cover_image = Image.open(io.BytesIO(image_data))

                cover_image = cover_image.resize((150, 200), Image.Resampling.LANCZOS) 
                cover_image_tk = ImageTk.PhotoImage(cover_image)

                cover_label = ttk.Label(self.cover_frame, image=cover_image_tk)
                cover_label.image = cover_image_tk  
                cover_label.pack(expand=True, fill='both')

            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการแสดงภาพ: {e}")
                error_label = ttk.Label(self.cover_frame, text="ไม่สามารถแสดงรูปภาพปกหนังสือ", font=("Arial", 12, "bold"))
                error_label.pack(expand=True, fill='both')
        else:
            no_image_label = ttk.Label(self.cover_frame, text="ไม่มีรูปภาพ", font=("Arial", 12))
            no_image_label.pack(expand=True, fill='both')

        ttk.Label(self.add_book_form_frame, text="ชื่อหนังสือ:").grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.title_var = tk.StringVar(value=title)
        ttk.Entry(self.add_book_form_frame, textvariable=self.title_var, width=40).grid(row=2, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_form_frame, text="สำนักพิมพ์:").grid(row=3, column=0, padx=10, pady=5, sticky='e')
        self.publisher_var = tk.StringVar(value=publisher)
        ttk.Entry(self.add_book_form_frame, textvariable=self.publisher_var, width=40).grid(row=3, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_form_frame, text="ISBN:").grid(row=4, column=0, padx=10, pady=5, sticky='e')
        self.isbn_var = tk.StringVar(value=isbn)
        ttk.Entry(self.add_book_form_frame, textvariable=self.isbn_var, width=40).grid(row=4, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_form_frame, text="จำนวนสต็อก:").grid(row=5, column=0, padx=10, pady=5, sticky='e')
        self.stock_var = tk.IntVar(value=stock)
        ttk.Entry(self.add_book_form_frame, textvariable=self.stock_var, width=40).grid(row=5, column=1, padx=10, pady=5)

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

        ttk.Label(self.add_book_form_frame, text="หมวดหมู่:").grid(row=6, column=0, padx=10, pady=5, sticky='e')
        self.catalog_var = tk.StringVar(value=category)
        catalog_combobox = ttk.Combobox(self.add_book_form_frame, textvariable=self.catalog_var, width=37)
        catalog_combobox['values'] = list(self.category_map.keys())
        catalog_combobox.grid(row=6, column=1, padx=10, pady=5)

        ttk.Label(self.add_book_form_frame, text="เนื้อหา:").grid(row=7, column=0, padx=10, pady=5, sticky='e')
        self.detail_text = tk.Text(self.add_book_form_frame, height=10, width=30, wrap=tk.WORD)
        self.detail_text.insert(tk.END, detail)
        self.detail_text.grid(row=8, column=1, padx=10, pady=5)

        buttons_frame = ttk.Frame(self.root)
        buttons_frame.pack(pady=10, side=tk.BOTTOM, fill=tk.X)
        add_book_button = ttk.Button(buttons_frame, text="บันทึกข้อมูล", command=self.edit_book)
        add_book_button.pack(side=tk.LEFT, padx=10, pady=5)
        back_button = ttk.Button(buttons_frame, text="กลับ", command=self.reset_to_main_menu)
        back_button.pack(side=tk.LEFT, padx=10, pady=5)
           
    def edit_book(self):
        book_title = self.title_var.get()
        book_author = self.author_var.get()
        book_publisher = self.publisher_var.get()
        book_isbn = self.isbn_var.get()
        book_stock = self.stock_var.get()
        book_detail = self.detail_text.get("1.0", "end-1c")
        selected_category = self.catalog_var.get()

        catalog_num = self.category_map.get(selected_category, None)
        if catalog_num is None:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกหมวดหมู่ที่ถูกต้อง")
            return


        book_cover_id = self.image_path.get() 
        encoded_image = None
        if book_cover_id:
            try:
                with open(book_cover_id, 'rb') as image_file:
                    image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode('utf-8')  
            except FileNotFoundError:
                messagebox.showerror("ข้อผิดพลาด", "ไม่พบไฟล์รูปภาพที่ระบุ")
                return
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการแปลงรูปภาพ: {e}")
                return

        try:
            book_id = update_book(
                book_title,
                book_author,
                book_publisher,
                book_isbn,
                book_stock,
                catalog_num, 
                book_detail,
                encoded_image 
            )
            messagebox.showinfo("สำเร็จ", "ข้อมูลหนังสือถูกแก้ไขเรียบร้อยแล้ว")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการแก้ไขข้อมูลหนังสือ: {e}")

    def encode_image(file_path):
        try:
            with open(file_path, "rb") as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
            return encoded_string
        except Exception as e:
            print(f"เกิดข้อผิดพลาดในการเข้ารหัสรูปภาพ: {e}")
            return None

    def browse_image(self):
        file_path = filedialog.askopenfilename(
            title="เลือกรูปภาพ",
            filetypes=[("ไฟล์รูปภาพ", "*.jpg;*.jpeg;*.png;*.gif")]
        )
        if file_path:
            self.image_path.set(file_path)
            self.preview_button.config(state=tk.NORMAL)  

    def preview_image_add(self):
        file_path = self.image_path.get()
        if file_path:
            self.show_image_preview(file_path)

    def preview_image_edit(self):
        image_path = self.image_path.get()
        if not image_path:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกไฟล์รูปภาพก่อนดูตัวอย่าง")
            return

        try:
            cover_image = Image.open(image_path)
            cover_image = cover_image.resize((150, 200), Image.Resampling.LANCZOS)
            cover_image_tk = ImageTk.PhotoImage(cover_image)

            for widget in self.cover_frame.winfo_children():
                widget.destroy()  
            cover_label = ttk.Label(self.cover_frame, image=cover_image_tk)
            cover_label.image = cover_image_tk  
            cover_label.pack(expand=True, fill='both')

        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถแสดงรูปภาพได้: {e}")
    def show_image_preview(self, file_path):
        img = Image.open(file_path)
        if not img:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกไฟล์รูปภาพก่อนดูตัวอย่าง")
            return

        try:
            img = Image.open(file_path)
            img = img.resize((150, 200), Image.Resampling.LANCZOS)
            img_tk = ImageTk.PhotoImage(img)

            for widget in self.cover_frame.winfo_children():
                widget.destroy()  
            img_label = ttk.Label(self.cover_frame, image=img_tk)
            img_label.image = img_tk  
            img_label.pack(expand=True, fill='both')

        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถแสดงรูปภาพได้: {e}")

    def validate_fields(self):
        if not self.image_path.get() or not self.title_var.get() or not self.author_var.get() or \
        not self.publisher_var.get() or not self.isbn_var.get() or self.stock_var.get() == 0 or \
        not self.catalog_var.get():
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลให้ครบทุกช่อง")
        else:
            self.add_book()

    def add_book(self):
        book_title = self.title_var.get()
        book_author = self.author_var.get()
        book_publisher = self.publisher_var.get()
        book_isbn = self.isbn_var.get()
        book_page = self.page_var.get()
        book_stock = self.stock_var.get()
        book_detail = self.detail_text.get("1.0", "end-1c")
        selected_category = self.catalog_var.get()

        if not all([book_title, book_author, book_publisher, book_isbn,book_page, book_stock, selected_category]):
            messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกข้อมูลให้ครบถ้วน")
            return

        catalog_num = self.category_map.get(selected_category, None)
        if catalog_num is None:
            messagebox.showerror("ข้อผิดพลาด", "กรุณาเลือกหมวดหมู่ที่ถูกต้อง")
            return

        book_cover_id = self.image_path.get()  
        encoded_image = None
        if book_cover_id:
            try:
                with open(book_cover_id, 'rb') as image_file:
                    image_data = image_file.read()
                    encoded_image = base64.b64encode(image_data).decode('utf-8')  
            except FileNotFoundError:
                messagebox.showerror("ข้อผิดพลาด", "ไม่พบไฟล์รูปภาพที่ระบุ")
                return
            except Exception as e:
                messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการแปลงรูปภาพ: {e}")
                return

        try:
            book_id = insert_book(
                book_title,
                book_author,
                book_publisher,
                book_isbn,
                book_page,
                book_stock,
                catalog_num,  
                book_detail,
                encoded_image  
            )
            messagebox.showinfo("สำเร็จ", "ข้อมูลหนังสือถูกเพิ่มเรียบร้อยแล้ว")
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาดในการเพิ่มข้อมูลหนังสือ: {e}")

    def borrow_return_books(self):

        self.clear_window()
        self.root.geometry("1200x700")

        main_frame = ttk.Frame(self.root, padding=20)
        main_frame.pack(expand=True, fill='both')

        info_frame = ttk.Frame(main_frame, padding=20)
        info_frame.grid(row=0, column=1, sticky="nsew")

        image_frame = ttk.Frame(main_frame, padding=20)
        image_frame.grid(row=0, column=0, sticky="nsew")

        title_label = ttk.Label(info_frame, text="คืนหนังสือ", font=("Arial", 18, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=15)

        labels = ["เลขบัตรประชาชน:", "คำนำหน้า:", "ชื่อ:", "นามสกุล:", "ยืมได้สูงสุด:", "ยืมได้อีก:"]
        self.entries = {}  

        for i, text in enumerate(labels):
            label = ttk.Label(info_frame, text=text, font=("Arial", 12))
            label.grid(row=i+1, column=0, sticky="e", padx=(0, 10), pady=5)
            entry = ttk.Entry(info_frame, font=("Arial", 12), state='readonly')
            entry.grid(row=i+1, column=1, padx=(10, 0), pady=5, sticky="w")
            self.entries[text] = entry

        instructions_label = ttk.Label(info_frame, text="หนังสือที่ท่านยืม", font=("Arial", 12, "bold"))
        instructions_label.grid(row=11, column=0, columnspan=2, pady=10, sticky="w")

        img = Image.open("insert_card.png")
        img = img.resize((400, 400))  
        img = ImageTk.PhotoImage(img)
        image_label = ttk.Label(image_frame, image=img)
        image_label.image = img
        image_label.pack(pady=5)

        instructions_label = ttk.Label(
            image_frame, 
            text="โปรดเสียบบัตรประชาชนเพื่ออ่านข้อมูลจากบัตร", 
            font=("Arial", 10, "bold")
        )
        instructions_label.pack(side="top", pady=(0, 5))  
        read_card_button = ttk.Button(
            image_frame, 
            text="อ่านบัตร",
            command=self.read_card
        )
        read_card_button.pack(side="top", pady=5)

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

        button_frame = ttk.Frame(info_frame, padding=10)
        button_frame.grid(row=13, column=0, columnspan=2, sticky="e")

        close_button = ttk.Button(button_frame, text="กลับไปหน้าแรก", command=self.reset_to_main_menu)
        close_button.pack(side="left", padx=10)

        return_button = ttk.Button(button_frame, text="คืนเล่มนี้", command=self.return_book)
        return_button.pack(side="left", padx=10)

        regulations_button = ttk.Button(button_frame, text="กฎระเบียบในการยืม", command=self.show_regulations)
        regulations_button.pack(side="left", padx=10)

        info_frame.grid_rowconfigure(12, weight=1)
        info_frame.grid_columnconfigure(1, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_columnconfigure(1, weight=3)  

    def read_card(self):
        try:           
            for _ in range(3):  
                card_data = rt_get_smartcard_data()
                if card_data:
                    break
                time.sleep(1)  

            if not card_data:
                messagebox.showerror("Error", "ไม่พบเครื่องอ่านบัตร กรุณาลองใหม่อีกครั้ง")
                return

            if isinstance(card_data, tuple) and len(card_data) >= 4:
                pid = card_data[0]  # ดึงเลขบัตรประชาชน
                prefix = card_data[1]  # ดึงคำนำหน้า
                first_name = card_data[2]  # ดึงชื่อ
                last_name = card_data[3]  # ดึงนามสกุล

                is_member = check_member_status(pid)

                if not is_member:
                    messagebox.showerror("Error", "ไม่พบข้อมูลสมาชิก กรุณาติดต่อเจ้าหน้าที่")
                    return

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
                    entry = self.entries.get(field)
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

                borrowed_books = fetch_borrowed_books(pid)

                for item in self.data_tree.get_children():
                    self.data_tree.delete(item)
                for book in borrowed_books:
                    self.data_tree.insert("", "end", values=(
                        book[0],  # ISBN ของหนังสือ
                        book[1],  # ชื่อหนังสือ
                        book[2],  # รายละเอียดหรือหมวดหมู่หนังสือ
                        book[3],  # วันที่ยืม
                        book[4]   # วันที่ต้องคืน
                    ))

            else:
                messagebox.showerror("Error", "ไม่พบข้อมูล กรุณาเสียบบัตร")

        except Exception as e:
            error_msg = "ไม่พบเครื่องอ่านบัตร" if "No readers" in str(e) else f"ไม่พบข้อมูลสมาชิก กรุณาติดต่อเจ้าหน้าที่\n{str(e)}"
            messagebox.showerror("Error", error_msg)

    def return_book(self):
        selected_item = self.data_tree.selection()
        if selected_item:
            book_data = self.data_tree.item(selected_item, "values")
            isbn = book_data[0]

            update_book_status(isbn)
            update_book_stock(isbn, increment=True)

            self.data_tree.delete(selected_item)

            messagebox.showinfo("Success", "หนังสือถูกคืนสำเร็จ")
        else:
            messagebox.showwarning("Warning", "กรุณาเลือกหนังสือที่จะคืน")

    def close_window(self):
        self.root.destroy()

    def show_regulations(self):
        regulations_window = tk.Toplevel(self.root)  
        regulations_window.title("กฎระเบียบการยืม")
        regulations_window.geometry("600x600")  

        regulations_font = font.Font(size=12)
        header_font = font.Font(size=16, weight="bold")

        header_label = ttk.Label(regulations_window, text="กฎระเบียบการยืม", font=header_font)
        header_label.pack(pady=10)  
        image = PhotoImage(file="role_library.png")

        image_label = ttk.Label(regulations_window, image=image)
        image_label.image = image  
        image_label.pack(pady=10)

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
    
    def show_results(self):
        if self.results_frame is None:
            self.results_frame = ttk.Frame(self.root, relief="sunken", padding=(10, 10))  

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

            self.results_tree.bind("<Double-1>", self.on_book_select)

            self.results_back_button = ttk.Button(self.results_frame, text="กลับ", command=self.reset_to_main_menu, width=10)
            self.results_back_button.pack(side="left", padx=20, pady=10)

        self.results_frame.pack(fill="both", expand=True)
        self.results_frame.master.geometry("1200x600")

    def test_db_connection(self):
        try:
            result = test_connection()
            messagebox.showinfo("สถานะเซิร์ฟเวอร์", result)
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"เกิดข้อผิดพลาด: {str(e)}")

    def on_book_select(self, event):
        selected_item = self.results_tree.selection()[0]
        book_details = self.results_tree.item(selected_item, "values")
        self.show_book_details(book_details)

    def search_books(self):
        book_name = self.book_name_entry.get()
        isbn = self.isbn_entry.get()
        category = self.category.get()

        search_criteria_count = sum([bool(book_name), bool(isbn), bool(category)])

        if search_criteria_count > 1:
            messagebox.showwarning("คำเตือน", "กรุณากรอกข้อมูลเพียงตัวเลือกเดียวเท่านั้น")
            return

        if self.results_tree is None:
            self.show_results()  

        for row in self.results_tree.get_children():
            self.results_tree.delete(row)

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
            result = "กรุณากรอกข้อมูลอย่างน้อย 1 เงื่อนไขเพื่อค้นหา"

        if isinstance(result, str) and "Error in connection" in result:
            messagebox.showerror("ข้อผิดพลาด", result)
        elif isinstance(result, str):
            messagebox.showinfo("ผลการค้นหา", result)
        else:
            for index, book in enumerate(result):
                self.results_tree.insert("", "end", values=(
                    index + 1,
                    book.get('book_on', 'N/A'),
                    book.get('book_title', 'N/A'),
                    book.get('book_isbn', 'N/A'),
                    book.get('book_publisher', 'N/A'),
                    book.get('catalog_name', 'N/A'),
                    book.get('book_detail', 'N/A')
                ))

        self.search_frame.pack_forget()
        self.results_frame.pack(fill="both", expand=True)        

    def show_book_details(self, book_details):
        details_window = tk.Toplevel(self.root)
        details_window.title("รายละเอียดหนังสือ")
        details_window.geometry("900x600")
        details_window.resizable(True, True)

        details_frame = ttk.Frame(details_window, padding="20")
        details_frame.pack(fill="both", expand=True)

        image = book_testim(book_details[3])

        content_frame = ttk.Frame(details_frame)
        content_frame.grid(row=0, column=0, sticky="nsew")

        if image:
            try:
                size = (int(2 * 96), int(2 * 96))
                image = image.resize(size, Image.Resampling.LANCZOS)
                img = ImageTk.PhotoImage(image)

                panel = ttk.Label(content_frame, image=img)
                panel.image = img  
                panel.grid(row=0, column=0, rowspan=6, padx=(0, 20), pady=10, sticky="nw")
            except Exception as e:
                print(f"เกิดข้อผิดพลาดในการแสดงภาพ: {e}")
                ttk.Label(content_frame, text="ไม่สามารถแสดงรูปภาพปกหนังสือ", font=("Arial", 12, "bold"), foreground="red").grid(row=0, column=0, rowspan=6, padx=(0, 20), pady=10, sticky="nw")
        else:
            ttk.Label(content_frame, text="ไม่พบรูปภาพปกหนังสือ", font=("Arial", 12, "bold"), foreground="red").grid(row=0, column=0, rowspan=6, padx=(0, 20), pady=10, sticky="nw")

        details = [
            ("ชื่อหนังสือ", book_details[2]),
            ("ISBN", book_details[3]),
            ("สำนักพิมพ์", book_details[4]),
            ("หมวดหมู่", book_details[5])
        ]
        for idx, (label, value) in enumerate(details):
            ttk.Label(content_frame, text=f"{label}: {value}", font=("Arial", 12, "bold")).grid(row=idx, column=1, sticky="w", pady=(0, 5))

        summary_text = book_details[6] if len(book_details) > 6 else "ไม่มีข้อมูลเรื่องย่อ"
        summary_text = "\n\n".join(["    " + para for para in summary_text.split("\n")])

        ttk.Label(content_frame, text="เนื้อหาภายใน:", font=("Arial", 12, "bold")).grid(row=len(details), column=1, sticky="nw", pady=(10, 0))

        summary_textbox = tk.Text(content_frame, wrap="word", font=("Arial", 12), height=10, width=60, bd=0)
        summary_textbox.insert("1.0", summary_text)
        summary_textbox.config(state="disabled")  
        summary_textbox.grid(row=len(details)+1, column=1, pady=10, sticky="w")

        button_frame = ttk.Frame(details_window)
        button_frame.pack(side="bottom", padx=20, pady=10, fill="x")

        borrow_button = ttk.Button(
            button_frame,
            text="ยืมหนังสือเล่มนี้",
            command=lambda: self.borrow_book(book_details[2], book_details[3])
        )
        borrow_button.pack(side="left", padx=4, pady=10)
        back_button = ttk.Button(
            button_frame,
            text="กลับไปหน้าแรก",
            command=details_window.destroy  
        )
        back_button.pack(side="left", padx=4, pady=10)

    def borrow_book(self, book_title, book_isbn):
        self.clear_window()
        self.root.geometry('600x550')
        
        borrow_frame = ttk.Frame(self.root, padding="20")
        borrow_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(borrow_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        image = Image.open("insert_card.png")
        inches = 3
        dpi = 96
        size = (int(inches * dpi), int(inches * dpi))
        image = image.resize(size, Image.Resampling.LANCZOS)
        photo = ImageTk.PhotoImage(image)
        image_label = ttk.Label(left_frame, image=photo)
        image_label.photo = photo
        image_label.pack(pady=10)

        right_frame = ttk.Frame(borrow_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)
        card_instructions_label = ttk.Label(right_frame, text="กรุณาเสียบบัตรประชาชน", font=("Arial", 14))
        card_instructions_label.pack(pady=10)
        press_button_label = ttk.Label(right_frame, text="จากนั้นกดปุ่ม อ่านข้อมูล")
        press_button_label.pack(pady=10)

        read_card_button = ttk.Button(right_frame, text="อ่านข้อมูล", command=self.process_card_data)
        read_card_button.pack(pady=10)

        self.root.update_idletasks()
        self.root.geometry(f"{self.root.winfo_width()}x{self.root.winfo_height()}")

        self.card_id_var = tk.StringVar()
        self.first_name_var = tk.StringVar()
        self.last_name_var = tk.StringVar()

        self.isbn_var = tk.StringVar()
        self.isbn_var.set(book_isbn)

        self.title_var = tk.StringVar()
        self.title_var.set(book_title)

        isbn_label = ttk.Label(right_frame, text="หมายเลข ISBN:")
        isbn_label.pack(pady=5)

        self.isbn_entry = ttk.Entry(right_frame, textvariable=self.isbn_var, state='readonly')
        self.isbn_entry.pack(pady=5)

        title_label = ttk.Label(right_frame, text="ชื่อหนังสือ:")
        title_label.pack(pady=5)

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

        buttons_frame = ttk.Frame(right_frame)
        buttons_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)

        confirm_button = ttk.Button(
            buttons_frame, text="ยืนยันการยืม",
            command=self.confirm_borrowing)
        confirm_button.pack(side=tk.LEFT, padx=5)

        back_button = ttk.Button(
            buttons_frame, text="กลับไปหน้าแรก",
            command=self.reset_to_main_menu)  
        back_button.pack(side=tk.LEFT, padx=5)

    def process_card_data(self):
        try:
            cid, prefix, first_name, last_name = br_get_smartcard_data()

            if not (cid and prefix and first_name and last_name):
                raise ValueError("ข้อมูลไม่ครบถ้วน")

            self.card_id_var.set(cid)
            self.first_name_var.set(first_name)
            self.last_name_var.set(last_name)

        except ValueError as ve:
            messagebox.showerror("ข้อผิดพลาด", str(ve))
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", "ไม่พบข้อมูล กรุณาเสียบบัตร")

    def confirm_borrowing(self):
        pid = self.card_id_var.get()
        book_isbn = self.isbn_var.get()

        if not pid:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลเลขบัตรประชาชน")
            return

        if not book_isbn:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกข้อมูล ISBN หนังสือ")
            return

        return_flag = check_return_flag(pid)  
        if return_flag == -1:
            messagebox.showerror("ข้อผิดพลาดฐานข้อมูล", "ไม่สามารถตรวจสอบข้อมูลการยืมได้ กรุณาลองใหม่")
            return
        
        if return_flag >= 3:
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถยืมหนังสือได้ เนื่องจากเกินจำนวนการยืมสูงสุด (3 เล่ม)")
            return

        if check_borrow_duplicate(pid, book_isbn):
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถยืมหนังสือเล่มนี้ซ้ำได้ เนื่องจากคุณยังไม่ได้คืนหนังสือเล่มนี้")
            return
        
        book_stock = check_book_stock(book_isbn)  
        if book_stock == 0:
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถยืมหนังสือได้เนื่องจากไม่มีหนังสือในสต็อก")
            return
        
        if borrow_book_from_db(pid, book_isbn):
            update_book_stock(book_isbn)
            messagebox.showinfo("สำเร็จ", "การยืมหนังสือสำเร็จ")
        else:
            messagebox.showerror("ข้อผิดพลาด", "ไม่สามารถยืมหนังสือได้ กรุณาลองใหม่อีกครั้ง")

class Library:
    def __init__(self):
        self.books = []
        self.members = []

if __name__ == "__main__":
    root = tk.Tk()
    library = Library()
    app = LibraryGUI(root, library)
    root.mainloop()