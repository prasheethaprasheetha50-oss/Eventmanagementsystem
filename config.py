
import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="prashee@123",    
        database="eventdb"
    )
