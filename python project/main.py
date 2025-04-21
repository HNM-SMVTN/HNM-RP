import psycopg2
from psycopg2 import sql


DB_NAME = "person_db"
DB_USER = "postgres"
DB_PASS = "hoonam1386"
DB_HOST = "localhost"
DB_PORT = "5432"

def connect_postgres():
    return psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )


def create_database():
    try:
        conn = connect_postgres()
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(DB_NAME)))
        print("✓ دیتابیس ساخته شد.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"(i) ساخت دیتابیس رد شد یا قبلاً ساخته شده. ({e})")


def connect():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        port=DB_PORT
    )


def create_table():
    try:
        conn = connect()
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS people (
                id SERIAL PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                birth_date DATE,
                gender TEXT,
                phone_number TEXT
            );
        """)
        conn.commit()
        print("✓ جدول ساخته شد.")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"× خطا در ساخت جدول: {e}")


def add_person():
    conn = connect()
    cur = conn.cursor()
    fname = input("نام: ")
    lname = input("نام خانوادگی: ")
    birth = input("تاریخ تولد (YYYY-MM-DD): ")
    gender = input("جنسیت (مرد/زن): ")
    phone = input("شماره موبایل: ")

    cur.execute("""
        INSERT INTO people (first_name, last_name, birth_date, gender, phone_number)
        VALUES (%s, %s, %s, %s, %s);
    """, (fname, lname, birth, gender, phone))

    conn.commit()
    print("✓ فرد با موفقیت اضافه شد.")
    cur.close()
    conn.close()
def show_all():
    conn = connect()
    cur = conn.cursor()
    cur.execute("SELECT * FROM people;")
    rows = cur.fetchall()
    print("\n--- لیست افراد ---")
    for row in rows:
        print(f"ID: {row[0]}, نام: {row[1]} {row[2]}, تولد: {row[3]}, جنسیت: {row[4]}, موبایل: {row[5]}")
    cur.close()
    conn.close()


def update_person():
    conn = connect()
    cur = conn.cursor()
    id = input("ID فرد برای بروزرسانی: ")
    fname = input("نام جدید: ")
    lname = input("نام خانوادگی جدید: ")
    birth = input("تاریخ تولد جدید: ")
    gender = input("جنسیت جدید: ")
    phone = input("شماره موبایل جدید: ")

    cur.execute("""
        UPDATE people
        SET first_name = %s,
            last_name = %s,
            birth_date = %s,
            gender = %s,
            phone_number = %s
        WHERE id = %s;
    """, (fname, lname, birth, gender, phone, id))

    conn.commit()
    print("✓ اطلاعات بروزرسانی شد.")
    cur.close()
    conn.close()


def delete_person():
    conn = connect()
    cur = conn.cursor()
    id = input("ID فرد برای حذف: ")
    cur.execute("DELETE FROM people WHERE id = %s;", (id,))
    conn.commit()
    print("✓ فرد حذف شد.")
    cur.close()
    conn.close()


def menu():
    while True:
        print("\n--- منو اصلی ---")
        print("1. افزودن فرد جدید")
        print("2. نمایش افراد")
        print("3. بروزرسانی اطلاعات")
        print("4. حذف فرد")
        print("5. خروج")

        choice = input("انتخاب شما: ")

        if choice == "1":
            add_person()
        elif choice == "2":
            show_all()
        elif choice == "3":
            update_person()
        elif choice == "4":
            delete_person()
        elif choice == "5":
            print("خروج از برنامه...")
            break
        else:
            print("گزینه نامعتبر.")
def main():
    create_database()
    create_table()
    menu()
if __name__=='__main__':
    main()