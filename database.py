import mysql.connector


def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="sivaleela",
            password="Sivaleela@19",
            database="cpms_db"
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