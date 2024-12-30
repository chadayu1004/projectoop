import pyodbc
import re
from PIL import Image, ImageTk
import io
import base64
from smartcard.System import readers
from smartcard.util import toHexString
from datetime import datetime, timedelta


def test_connection():
    try:
        with pyodbc.connect('DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=OOPLibrary;UID=sqlconnect;PWD=sq1connect0r', timeout=3) as connection:
            return "เชื่อมต่อกับฐานข้อมูลอยู่ในขณะนี้"
    except pyodbc.Error:
        return f"ไม่สามารถเชื่อมต่อกับฐานข้อมูลได้ กรุณาตรวจสอบว่าเรียกใช้ Web Socket อยู่"

def connect_db():
    try:
        return pyodbc.connect(
            'DRIVER={SQL Server};SERVER=127.0.0.1;DATABASE=OOPLibrary;UID=sqlconnect;PWD=sq1connect0r', timeout=3)
    except pyodbc.Error as e:
        raise Exception(f"ข้อผิดพลาดในการเชื่อมต่อ: {e}")

def execute_query(query, params=None):
    try:
        with connect_db() as connection:
            cursor = connection.cursor()
            cursor.execute(query, params or ())
            return cursor.fetchall()
    except pyodbc.Error as e:
        return f"ข้อผิดพลาดในการเชื่อมต่อ: {e}"

def is_base64(data):
    # ตรวจสอบว่าข้อมูลเป็น Base64 หรือไม่
    base64_pattern = re.compile('^[A-Za-z0-9+/=]+$')
    return bool(base64_pattern.match(data)) and len(data) % 4 == 0

def book_testim(book_id):
    query = """
            SELECT book_cover_id
            FROM table_book
            WHERE book_isbn = ?
            """
    # ดึงข้อมูลจากฐานข้อมูล
    rows = execute_query(query, (book_id,))
    
    if rows:
        book_cover_id = rows[0][0]
        
        # ตรวจสอบว่าข้อมูลเป็น Base64 หรือไม่
        if is_base64(book_cover_id):
            try:
                # ถอดรหัสข้อมูล Base64
                cover_data = base64.b64decode(book_cover_id)
                
                # แปลงข้อมูลเป็นภาพ
                image = Image.open(io.BytesIO(cover_data))
                return image  # ส่งคืนภาพเพื่อใช้งานต่อ
            except (base64.binascii.Error, IOError) as e:
                print(f"เกิดข้อผิดพลาดในการแปลงข้อมูลเป็นภาพ: {e}")
                return None
        else:
            print("ข้อมูลไม่ใช่ Base64 encoded.")
            return None
    else:
        print("ไม่พบข้อมูลสำหรับ book_id ที่กำหนด.")
        return None


def search_books_by_title(title):
    query = """
            SELECT book.book_on,
                   book.book_title,
                   book.book_isbn,
                   book.book_publisher,
                   book.book_detail,
                   catalogs.catalog_name
            FROM table_book AS book
            JOIN table_catalog AS catalogs
            ON book.catalog_num = catalogs.catalog_num
            WHERE book.book_title LIKE ?
            """
    rows = execute_query(query, f'%{title}%')
    
    if isinstance(rows, str):
        return rows
    
    return [{
        "book_on": row.book_on,
        "book_title": row.book_title,
        "book_isbn": row.book_isbn,
        "book_publisher": row.book_publisher,
        "book_detail": row.book_detail,
        "catalog_name": row.catalog_name
    } for row in rows] if rows else "ไม่พบผลลัพธ์"

def search_books_by_isbn(isbn):
    query = """
            SELECT book.book_on,
                   book.book_title,
                   book.book_isbn,
                   book.book_publisher,
                   book.book_detail,
                   catalogs.catalog_name
            FROM table_book AS book
            JOIN table_catalog AS catalogs
            ON book.catalog_num = catalogs.catalog_num
            WHERE book.book_isbn LIKE ?
            """
    rows = execute_query(query, f'%{isbn}%')
    
    if isinstance(rows, str):
        return rows
    
    return [{
        "book_on": row.book_on,
        "book_title": row.book_title,
        "book_isbn": row.book_isbn,
        "book_publisher": row.book_publisher,
        "book_detail": row.book_detail,
        "catalog_name": row.catalog_name
    } for row in rows] if rows else "ไม่พบผลลัพธ์"

def search_books_by_category(category_num):
    query = """
            SELECT book.book_on,
                   book.book_title,
                   book.book_isbn,
                   book.book_publisher,
                   book.book_detail,
                   catalogs.catalog_name
            FROM table_book AS book
            JOIN table_catalog AS catalogs
            ON book.catalog_num = catalogs.catalog_num
            WHERE book.catalog_num = ?
            """
    rows = execute_query(query, (category_num,))
    
    if isinstance(rows, str):
        return rows
    
    return [{
        "book_on": row.book_on,
        "book_title": row.book_title,
        "book_isbn": row.book_isbn,
        "book_publisher": row.book_publisher,
        "book_detail": row.book_detail,
        "catalog_name": row.catalog_name
    } for row in rows] if rows else "ไม่พบผลลัพธ์"


def search_edit_books_by_title(title):
    query = """
        SELECT 
            b.book_title, 
            b.book_isbn, 
            b.book_publisher,
            b.book_stock,
            b.book_detail,
            b.book_cover_id, 
            c.catalog_name
        FROM 
            table_book b
        INNER JOIN 
            table_catalog c ON b.catalog_num = c.catalog_num
        WHERE book_title LIKE ?
    """
    rows = execute_query(query, f'%{title}%')
    
    if isinstance(rows, str):
        return rows
    
    return [{
        "book_title": row.book_title,
        "book_isbn": row.book_isbn,
        "book_publisher": row.book_publisher,
        "book_stock": row.book_stock,
        "book_detail": row.book_detail,
        "catalog_name": row.catalog_name,
        "book_cover_id" : row.book_cover_id
    } for row in rows] if rows else "ไม่พบผลลัพธ์"


def search_edit_books_by_isbn(isbn):
    query = """
        SELECT 
            b.book_title, 
            b.book_isbn, 
            b.book_publisher,
            b.book_stock,
            b.book_detail,
            b.book_cover_id, 
            c.catalog_name
        FROM 
            table_book b
        INNER JOIN 
            table_catalog c ON b.catalog_num = c.catalog_num
        WHERE book_isbn LIKE ?
    """
    rows = execute_query(query, f'%{isbn}%')
    
    if isinstance(rows, str):
        return rows
    
    return [{
        "book_title": row.book_title,
        "book_isbn": row.book_isbn,
        "book_publisher": row.book_publisher,
        "book_stock": row.book_stock,
        "book_detail": row.book_detail,
        "book_cover_id" : row.book_cover_id,
        "catalog_name": row.catalog_name
    } for row in rows] if rows else "ไม่พบผลลัพธ์"

def get_cover_image(self, isbn):
    query = """
            SELECT book_cover_id
            FROM table_book
            WHERE book_isbn = ?
            """
    # Execute the query to fetch cover ID
    rows = execute_query(query, (isbn,))
    
    if rows:
        book_cover_id = rows[0][0]
        
        # Check if the data is Base64
        if is_base64(book_cover_id):
            try:
                # Decode the Base64 data
                cover_data = base64.b64decode(book_cover_id)
                
                # Convert the data to an image
                image = Image.open(io.BytesIO(cover_data))
                return image  # Return the image for further use
            except (base64.binascii.Error, IOError) as e:
                print(f"Error converting data to image: {e}")
                return None
        else:
            print("Data is not Base64 encoded.")
            return None
    else:
        print("No data found for the specified ISBN.")
        return None



def store_id_card_data(cid, member_gender, first_name, last_name):
    check_query = "SELECT COUNT(*) FROM table_member WHERE pid = ?"
    update_query = """
        UPDATE table_member
        SET member_gender = ?, first_name = ?, last_name = ?
        WHERE pid = ?
    """
    insert_query = """
        INSERT INTO table_member (pid, member_gender, first_name, last_name, book_borrow_max)
        VALUES (?, ?, ?, ?, ?)
    """
    
    try:
        with connect_db() as connection:
            cursor = connection.cursor()
            
            # ตรวจสอบว่ามีบันทึกอยู่หรือไม่
            cursor.execute(check_query, (cid,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                # อัปเดตบันทึกที่มีอยู่
                cursor.execute(update_query, (member_gender, first_name, last_name, cid))
            else:
                # แทรกบันทึกใหม่
                cursor.execute(insert_query, (cid, member_gender, first_name, last_name, "3"))
            
            connection.commit()
    except pyodbc.Error as e:
        return f"ข้อผิดพลาดในการจัดเก็บข้อมูลบัตรประชาชน: {e}"


def br_get_smartcard_data():
    def thai2unicode(data):
        if isinstance(data, list):
            return bytes(data).decode('tis-620').replace('#', ' ').strip()
        return data

    def split_thai_name(full_name):
        prefixes = ["นาย", "น.ส.", "นาง"]
        prefix = ""
        for p in prefixes:
            if full_name.startswith(p):
                prefix = p
                full_name = full_name[len(p):].strip()
                break

        name_parts = full_name.split()
        if len(name_parts) == 2:
            first_name, last_name = name_parts
        elif len(name_parts) > 2:
            first_name = " ".join(name_parts[:-1])
            last_name = name_parts[-1]
        else:
            first_name = full_name
            last_name = ""

        return prefix, first_name, last_name

    def get_data(cmd, req=[0x00, 0xc0, 0x00, 0x00]):
        data, sw1, sw2 = connection.transmit(cmd)
        data, sw1, sw2 = connection.transmit(req + [cmd[-1]])
        return [data, sw1, sw2]

    SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08]
    THAI_CARD = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]
    CMD_CID = [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d]
    CMD_THFULLNAME = [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64]

    readerList = readers()
    if not readerList:
        raise Exception("ไม่พบเครื่องอ่านบัตรสมาร์ทการ์ด")
    
    reader = readerList[0]
    connection = reader.createConnection()
    connection.connect()
    atr = connection.getATR()
    req = [0x00, 0xc0, 0x00, 0x01] if atr[0] == 0x3B and atr[1] == 0x67 else [0x00, 0xc0, 0x00, 0x00]

    # เลือกแอปพลิเคชัน
    data, sw1, sw2 = connection.transmit(SELECT + THAI_CARD)
    print(f"การเลือกแอปพลิเคชัน: {sw1:02X} {sw2:02X}")

    # รับ CID
    data = get_data(CMD_CID, req)
    cid = thai2unicode(data[0])

    # รับชื่อเต็ม
    data = get_data(CMD_THFULLNAME, req)
    full_name = thai2unicode(data[0])
    prefix, first_name, last_name = split_thai_name(full_name)

    # บันทึกข้อมูลลงฐานข้อมูล
    store_id_card_data(cid, prefix, first_name, last_name)
    
    # ปิดการเชื่อมต่อ
    try:
        if hasattr(connection, 'disconnect'):
            connection.disconnect()
        elif hasattr(connection, 'close'):
            connection.close()
        else:
            print("Connection object does not support a close method")
    except Exception as e:
        print(f"Error closing connection: {e}")

    return cid, prefix, first_name, last_name



def rt_get_smartcard_data():
    def thai2unicode(data):
        if isinstance(data, list):
            return bytes(data).decode('tis-620').replace('#', ' ').strip()
        return data

    def split_thai_name(full_name):
        prefixes = ["นาย", "น.ส.", "นาง"]
        prefix = ""
        for p in prefixes:
            if full_name.startswith(p):
                prefix = p
                full_name = full_name[len(p):].strip()
                break

        name_parts = full_name.split()
        if len(name_parts) == 2:
            first_name, last_name = name_parts
        elif len(name_parts) > 2:
            first_name = " ".join(name_parts[:-1])
            last_name = name_parts[-1]
        else:
            first_name = full_name
            last_name = ""

        return prefix, first_name, last_name

    def get_data(cmd, req=[0x00, 0xc0, 0x00, 0x00]):
        data, sw1, sw2 = connection.transmit(cmd)
        data, sw1, sw2 = connection.transmit(req + [cmd[-1]])
        return [data, sw1, sw2]

    SELECT = [0x00, 0xA4, 0x04, 0x00, 0x08]
    THAI_CARD = [0xA0, 0x00, 0x00, 0x00, 0x54, 0x48, 0x00, 0x01]
    CMD_CID = [0x80, 0xb0, 0x00, 0x04, 0x02, 0x00, 0x0d]
    CMD_THFULLNAME = [0x80, 0xb0, 0x00, 0x11, 0x02, 0x00, 0x64]

    readerList = readers()
    if not readerList:
        raise Exception("ไม่พบเครื่องอ่านบัตรสมาร์ทการ์ด")
    
    reader = readerList[0]
    connection = reader.createConnection()
    connection.connect()
    atr = connection.getATR()
    req = [0x00, 0xc0, 0x00, 0x01] if atr[0] == 0x3B and atr[1] == 0x67 else [0x00, 0xc0, 0x00, 0x00]

    # เลือกแอปพลิเคชัน
    data, sw1, sw2 = connection.transmit(SELECT + THAI_CARD)
    print(f"การเลือกแอปพลิเคชัน: {sw1:02X} {sw2:02X}")

    # รับ CID
    data = get_data(CMD_CID, req)
    cid = thai2unicode(data[0])

    # รับชื่อเต็ม
    data = get_data(CMD_THFULLNAME, req)
    full_name = thai2unicode(data[0])
    prefix, first_name, last_name = split_thai_name(full_name)



    # ปิดการเชื่อมต่อ
    try:
        if hasattr(connection, 'disconnect'):
            connection.disconnect()
        elif hasattr(connection, 'close'):
            connection.close()
        else:
            print("Connection object does not support a close method")
    except Exception as e:
        print(f"Error closing connection: {e}")

    return cid, prefix, first_name, last_name





def check_member_status(pid):
    try:
        # เชื่อมต่อกับฐานข้อมูล
        conn = connect_db()
        cursor = conn.cursor()

        # สร้างคำสั่ง SQL เพื่อตรวจสอบสถานะสมาชิก
        query = """
                SELECT COUNT(*)
                FROM table_member
                WHERE pid = ?
                """
        # รันคำสั่ง SQL
        cursor.execute(query, (pid,))
        result = cursor.fetchone()

        # ตรวจสอบผลลัพธ์
        if result and result[0] > 0:
            return True  # พบสมาชิก
        else:
            return False  # ไม่พบสมาชิก
    except pyodbc.Error as e:
        print(f"Error: {e}")
        return False  # ถือว่าไม่พบสมาชิกในกรณีเกิดข้อผิดพลาด
    finally:
        # ปิดการเชื่อมต่อฐานข้อมูล
        cursor.close()
        conn.close()


def check_return_flag(pid):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # คำสั่ง SQL สำหรับนับจำนวนหนังสือที่ยังไม่ได้คืนของผู้ใช้
        query = """
        SELECT COUNT(*)
        FROM table_borrow
        WHERE pid = ? AND return_flag = 'N'
        """
        cursor.execute(query, (pid,))
        จำนวนหนังสือที่ยังไม่ได้คืน = cursor.fetchone()[0]

        cursor.close()

        # ส่งคืนจำนวนหนังสือที่ยังไม่ได้คืน (ต้องน้อยกว่า 3)
        return จำนวนหนังสือที่ยังไม่ได้คืน
    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการตรวจสอบ return flag: {e}")
        return -1  # ส่งคืน -1 หรือค่าความผิดพลาดเพื่อบอกว่าการเรียกข้อมูลล้มเหลว
    
def check_book_stock(book_isbn):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        query = "SELECT book_available FROM table_book WHERE book_isbn = ?"
        cursor.execute(query, (book_isbn,))
        stock = cursor.fetchone()

        if stock:
            return stock[0]  # คืนค่าจำนวนหนังสือในสต็อก
        else:
            return 0  # ถ้าไม่มีหนังสือในฐานข้อมูล ให้คืนค่า 0

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการตรวจสอบสต็อกหนังสือ: {e}")
        return 0  # คืนค่า 0 หากเกิดข้อผิดพลาด
    
    finally:
        cursor.close()
        conn.close()

def update_book_stock(book_isbn, increment=False):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        
        if increment:
            # เพิ่มจำนวนหนังสือที่สามารถยืมได้
            query = """
                UPDATE table_book 
                SET book_available = book_available + 1 
                WHERE book_isbn = ?
            """
        else:
            # ลดจำนวนหนังสือที่สามารถยืมได้
            query = """
                UPDATE table_book 
                SET book_available = book_available - 1 
                WHERE book_isbn = ? AND book_available > 0
            """
        
        cursor.execute(query, (book_isbn,))
        conn.commit()
        
        if cursor.rowcount == 0:
            print("ไม่สามารถอัปเดตสต็อกได้ หนังสือหมด หรือหมายเลข ISBN ไม่ถูกต้อง")
        else:
            print("อัปเดตสต็อกสำเร็จ")

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการอัปเดตสต็อกหนังสือ: {e}")

    finally:
        cursor.close()
        conn.close()

def update_book_status(isbn):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # อัปเดตสถานะการคืนใน table_borrow โดยใช้ isbn
        update_query = """
        UPDATE table_borrow
        SET return_flag = 'Y', return_date = GETDATE()
        WHERE book_isbn = ? AND return_flag = 'N'
        """
        
        cursor.execute(update_query, (isbn,))

        # บันทึกการเปลี่ยนแปลง
        conn.commit()

        print(f"อัปเดตสถานะการคืนของหนังสือ ISBN: {isbn} สำเร็จ")

    except pyodbc.Error as e:
        print(f"เกิดข้อผิดพลาด: {e}")

    finally:
        cursor.close()
        conn.close()




def check_borrow_duplicate(pid, book_isbn):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        # ตรวจสอบว่ามีการยืมหนังสือเล่มนี้ที่ยังไม่ได้คืนหรือไม่
        query = """
        SELECT COUNT(*)
        FROM table_borrow
        WHERE pid = ? AND book_isbn = ? AND return_flag = 'N'
        """
        cursor.execute(query, (pid, book_isbn))
        borrow_count = cursor.fetchone()[0]

        cursor.close()

        # ถ้ามีการยืมหนังสือเล่มนี้อยู่และยังไม่ได้คืน จะคืนค่า True
        return borrow_count > 0

    except Exception as e:
        print(f"เกิดข้อผิดพลาดในการตรวจสอบการยืมหนังสือซ้ำ: {e}")
        return False

def borrow_book_from_db(pid, book_isbn):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        borrow_date = datetime.now().strftime('%Y-%m-%d')
        return_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        return_flag = 'N'

        query = """
                INSERT INTO table_borrow (pid, book_isbn, borrow_date, return_date, return_flag)
                VALUES (?, ?, ?, ?, ?)
            """
        cursor.execute(query, (pid, book_isbn, borrow_date, return_date, return_flag))
        conn.commit()
        return True

    except Exception as e:
        print("เกิดข้อผิดพลาด:", e)
        conn.rollback()
        return False

    finally:
        cursor.close()
        conn.close()

def fetch_borrowed_books(pid):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
                SELECT
                    b.book_isbn,
                    b.book_title,
                    c.catalog_name,
                    br.borrow_date,
                    br.return_date
                FROM
                    table_book b
                INNER JOIN table_catalog c ON b.catalog_num = c.catalog_num
                INNER JOIN table_borrow br ON b.book_isbn = br.book_isbn
                INNER JOIN table_member m ON br.pid = m.pid
                WHERE
                    br.return_flag = 'N'
                    AND m.pid = ?
                """
        cursor.execute(query, (pid,))
        rows = cursor.fetchall()
        return rows

    except Exception as e:
        print("เกิดข้อผิดพลาด:", e)
        return []

    finally:
        cursor.close()
        conn.close()

def get_borrow_max_data(pid):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
                SELECT book_borrow_max 
                FROM table_member
                WHERE pid = ?
                """
        cursor.execute(query, (pid,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print("เกิดข้อผิดพลาด:", e)
        return []
    finally:
        cursor.close()
        conn.close()



def get_remain_borrow(pid):
    try:
        conn = connect_db()
        cursor = conn.cursor()

        query = """
                SELECT
                3 - COUNT(*) AS books_remain
                FROM
                table_borrow
                WHERE
                pid = ? AND
                return_flag = 'N'
                """
        cursor.execute(query, (pid,))
        rows = cursor.fetchall()
        return rows
    except Exception as e:
        print("เกิดข้อผิดพลาด:", e)
        return []
    finally:
        cursor.close()
        conn.close()




def staff_admin(username, password):
    conn = connect_db()  
    cursor = conn.cursor()

    # คำสั่ง SQL เพื่อตรวจสอบว่ามี username และ password ตรงกับข้อมูลในฐานข้อมูลหรือไม่
    query = """
            SELECT CASE WHEN password = HASHBYTES('SHA1', ?) THEN '1' ELSE '' END AS result
            FROM table_admin
            WHERE username = ?

            """
    cursor.execute(query, (username, password))

    result = cursor.fetchone()  # ดึงข้อมูลแถวแรกที่ตรงกับเงื่อนไข
    conn.close()  # ปิดการเชื่อมต่อฐานข้อมูล

    if result:
        return True  # เข้าสู่ระบบสำเร็จ
    else:
        return False  # เข้าสู่ระบบไม่สำเร็จ


def insert_book(
    book_title,
    book_author,
    book_publisher,
    book_page,
    book_isbn,
    book_stock,
    catalog_num,  # รหัสหมวดหมู่ที่เป็นสตริง 3 หลัก
    book_detail,
    book_cover_id  # ข้อมูลรูปภาพที่เข้ารหัส base64
):
    try:
        conn = connect_db()  # เชื่อมต่อฐานข้อมูล
        cursor = conn.cursor()

        # เพิ่มข้อมูลหนังสือในตาราง พร้อมกับการตั้งค่า book_available เท่ากับ book_stock
        query = '''
        INSERT INTO table_book (
            book_title, 
            book_author, 
            book_publisher,  
            book_page,
            book_isbn, 
            book_detail, 
            book_stock, 
            book_available,  -- เพิ่มฟิลด์ book_available
            catalog_num,
            book_cover_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''

        params = (
            book_title, 
            book_author, 
            book_publisher,
            book_page, 
            book_isbn, 
            book_detail, 
            book_stock, 
            book_stock,  # ตั้งค่า book_available เท่ากับ book_stock
            catalog_num,  # ส่งรหัสหมวดหมู่ 3 หลัก
            book_cover_id  # ส่งข้อมูลรูปภาพที่เข้ารหัส base64
        )
        
        cursor.execute(query, params)  # รันคำสั่งเพิ่มข้อมูล
        conn.commit()  # ยืนยันการบันทึกข้อมูล

        print("ข้อมูลหนังสือถูกเพิ่มเรียบร้อยแล้ว")
        return  # Return book_id if needed
    
    except pyodbc.Error as e:
        print("เกิดข้อผิดพลาดในการเพิ่มข้อมูลหนังสือ:", e)
    
    finally:
        # ปิดการเชื่อมต่อฐานข้อมูลเสมอ
        if conn:
            conn.close()



def update_book(
    book_title,
    book_author,
    book_publisher,
    book_isbn,
    book_stock,
    catalog_num,  # รหัสหมวดหมู่ที่เป็นสตริง 3 หลัก
    book_detail,
    book_cover_id  # ข้อมูลรูปภาพที่เข้ารหัส base64
    ):
    try:
        conn = connect_db()  # เชื่อมต่อฐานข้อมูล
        cursor = conn.cursor()

        # คำสั่ง SQL สำหรับการอัปเดตข้อมูลหนังสือ
        query = '''
        UPDATE table_book
        SET 
            book_title = ?, 
            book_author = ?, 
            book_publisher = ?,  
            book_detail = ?, 
            book_stock = ?, 
            catalog_num = ?, 
            book_cover_id = ?
        WHERE book_isbn = ?
        '''

        # กำหนดพารามิเตอร์สำหรับคำสั่ง SQL
        params = (
            book_title, 
            book_author, 
            book_publisher, 
            book_detail, 
            book_stock, 
            catalog_num,  # ส่งรหัสหมวดหมู่ 3 หลัก
            book_cover_id,  # ส่งข้อมูลรูปภาพที่เข้ารหัส base64
            book_isbn  # ส่ง book_isbn สำหรับเงื่อนไข WHERE
        )
        
        cursor.execute(query, params)  # รันคำสั่งอัปเดตข้อมูล
        conn.commit()  # ยืนยันการบันทึกข้อมูล

        print("ข้อมูลหนังสือถูกแก้ไขเรียบร้อยแล้ว")
        return  # Return book_id if needed
    
    except pyodbc.Error as e:
        print("เกิดข้อผิดพลาดในการแก้ไขข้อมูลหนังสือ:", e)
    
    finally:
        # ปิดการเชื่อมต่อฐานข้อมูลเสมอ
        if conn:
            conn.close()











    
    


