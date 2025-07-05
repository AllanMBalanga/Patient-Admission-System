import mysql.connector
from mysql.connector import Error
from mysql.connector.cursor import MySQLCursorDict      #returns dictionaries
from .config import settings

conn = mysql.connector.connect(
    host=settings.database_host,
    user=settings.database_user,
    password=settings.database_password
)

cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS admission")
print("Database successfully created")
conn.commit()

class Database:
    def __init__(self):
        try:
            self.conn = mysql.connector.connect(
                host=settings.database_host,
                user=settings.database_user,
                password=settings.database_password,
                database=settings.database_name,
                use_pure=True
            )

            self.cursor = self.conn.cursor(cursor_class=MySQLCursorDict, buffered=True)

        except Error as e:
            print(f"Database connection error: {e}")
            raise

    def create_tables(self):
        commands = (
            """
            CREATE TABLE IF NOT EXISTS provinces(
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(60) NOT NULL,
                city VARCHAR(60) NOT NULL,

                UNIQUE (name, city)
                );
            """,
            """
            CREATE TABLE IF NOT EXISTS patients(
                id INT AUTO_INCREMENT PRIMARY KEY,
                province_id INT NOT NULL,
                first_name VARCHAR(30) NOT NULL,
                last_name VARCHAR(30) NOT NULL,
                email VARCHAR(64) NOT NULL,
                password VARCHAR(120) NOT NULL,
                gender VARCHAR(16),
                birth_date DATE NOT NULL,
                allergies VARCHAR(80),
                height_cm FLOAT NOT NULL,
                weight_kg FLOAT NOT NULL,

                UNIQUE (email),
                FOREIGN KEY (province_id) REFERENCES provinces (id)
                ON UPDATE CASCADE ON DELETE CASCADE
                );
            """,
            """
            CREATE TABLE IF NOT EXISTS doctors (
                id INT AUTO_INCREMENT PRIMARY KEY,
                first_name VARCHAR(30) NOT NULL,
                last_name VARCHAR(30) NOT NULL,
                email VARCHAR(64) NOT NULL,
                password VARCHAR(120) NOT NULL,
                specialty VARCHAR(30) NOT NULL,

                UNIQUE (email)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS admissions (
                id INT AUTO_INCREMENT PRIMARY KEY,
                patient_id INT NOT NULL,
                doctor_id INT NOT NULL,
                diagnosis VARCHAR(80) NOT NULL,
                status VARCHAR(10) NOT NULL DEFAULT 'sick',
                admission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                discharge_date TIMESTAMP DEFAULT NULL,
                
                FOREIGN KEY (patient_id) REFERENCES patients (id)
                ON UPDATE CASCADE ON DELETE CASCADE,
                FOREIGN KEY (doctor_id) REFERENCES doctors (id)
                ON UPDATE CASCADE ON DELETE CASCADE
            );
            """
        )

        for command in commands:
            self.cursor.execute(command)

        print("Database connected successfully")
        self.conn.commit()
        self.conn.close()

db = Database()
db.create_tables()