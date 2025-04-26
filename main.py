from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List


app = FastAPI(title="Person Management API")


class Person(BaseModel):
    first_name: str
    last_name: str
    birth_date: str
    gender: str
    phone_number: str


class PersonOut(Person):
    id: int


def get_conn(database="person_db"):
    return psycopg2.connect(
        dbname=database,
        user="postgres",
        password="hoonam1386",  
        host="localhost",
        port="5432"
    )

def create_database():
    try:
        conn = get_conn("postgres")
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_database WHERE datname = 'person_db'")
        exists = cur.fetchone()
        if not exists:
            cur.execute('CREATE DATABASE person_db')
            print("Database 'person_db' created.")
        else:
            print("Database already exists.")
        cur.close()
        conn.close()
    except Exception as e:
        print("Error creating database:", e)


def create_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
            id SERIAL PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            birth_date DATE NOT NULL,
            gender TEXT NOT NULL,
            phone_number TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


@app.on_event("startup")
def startup_event():
    create_database()
    create_table()


@app.post("/people", response_model=PersonOut)
def create_person(p: Person):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO people (first_name, last_name, birth_date, gender, phone_number)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """, (p.first_name, p.last_name, p.birth_date, p.gender, p.phone_number))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()
    return {**p.dict(), "id": new_id}


@app.get("/people", response_model=List[PersonOut])
def get_people():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM people;")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "birth_date": row[3],
            "gender": row[4],
            "phone_number": row[5]
        }
        for row in rows
    ]


@app.put("/people/{person_id}", response_model=PersonOut)
def update_person(person_id: int, p: Person):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE people
        SET first_name=%s, last_name=%s, birth_date=%s, gender=%s, phone_number=%s
        WHERE id=%s
        RETURNING id;
    """, (p.first_name, p.last_name, p.birth_date, p.gender, p.phone_number, person_id))
    updated = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if updated:
        return {**p.dict(), "id": person_id}
    else:
        raise HTTPException(status_code=404, detail="Person not found")


@app.delete("/people/{person_id}")
def delete_person(person_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM people WHERE id=%s RETURNING id;", (person_id,))
    deleted = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()
    if deleted:
        return {"message": f"Person with id {person_id} deleted successfully."}
    else:
        raise HTTPException(status_code=404, detail="Person not found")