# seed.py
import mysql.connector
import csv
import uuid


def connect_db():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="your_mysql_user",
            password="your_mysql_password"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def create_database(connection):
    cursor = connection.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS ALX_prodev")
    cursor.close()


def connect_to_prodev():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="your_mysql_user",
            password="your_mysql_password",
            database="ALX_prodev"
        )
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None


def create_table(connection):
    cursor = connection.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_data (
            user_id VARCHAR(36) PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            age DECIMAL NOT NULL,
            INDEX (user_id)
        )
    """)
    connection.commit()
    print("Table user_data created successfully")
    cursor.close()


def insert_data(connection, csv_file):
    cursor = connection.cursor()
    with open(csv_file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            user_id = str(uuid.uuid4())
            name = row['name']
            email = row['email']
            age = row['age']
            cursor.execute("""
                INSERT INTO user_data (user_id, name, email, age)
                SELECT * FROM (SELECT %s, %s, %s, %s) AS tmp
                WHERE NOT EXISTS (
                    SELECT 1 FROM user_data WHERE email = %s
                ) LIMIT 1;
            """, (user_id, name, email, age, email))
    connection.commit()
    cursor.close()
