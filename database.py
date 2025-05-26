import pymysql

def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="your_root",
        password="your_password",
        database="crime_records",
        cursorclass=pymysql.cursors.DictCursor
    )
