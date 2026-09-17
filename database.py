import os
import mysql.connector


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("MYSQLHOST", "localhost"),
            port=int(os.getenv("MYSQLPORT", 3306)),
            user=os.getenv("MYSQLUSER"),
            password=os.getenv("MYSQLPASSWORD"),
            database=os.getenv("MYSQLDATABASE")
        )

        print("✅ MySQL connected successfully!")
        return connection

    except mysql.connector.Error as e:
        print("❌ MySQL connection error:", e)
        return None


if __name__ == "__main__":
    conn = get_db_connection()
    if conn:
        conn.close()
