from flask import Flask
from flask_bcrypt import Bcrypt
from database import get_db_connection

app = Flask(__name__)
bcrypt = Bcrypt(app)

# Function to create necessary tables and trigger
def create_tables():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            # Create users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) NOT NULL UNIQUE,
                    email VARCHAR(100) NOT NULL UNIQUE,
                    phone VARCHAR(15) NOT NULL,
                    country_code VARCHAR(5) NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    role ENUM('police', 'public') NOT NULL,
                    dob DATE DEFAULT NULL,
                    access ENUM('accepted', 'denied') DEFAULT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create Police Users Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS police_users (
                    id INT PRIMARY KEY,
                    police_id VARCHAR(20) UNIQUE NOT NULL,
                    station_name VARCHAR(100) NOT NULL,
                    police_position ENUM('inspector', 'sub-inspector', 'constable') NOT NULL,
                    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')

            # Create Public Users Table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS public_users (
                    id INT PRIMARY KEY,
                    aadhaar VARCHAR(12) UNIQUE NOT NULL,
                    current_status ENUM('studying', 'working') NOT NULL,
                    organization VARCHAR(100) DEFAULT NULL,
                    FOREIGN KEY (id) REFERENCES users(id) ON DELETE CASCADE
                )
            ''')

            # Create admins table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL
                )
            ''')

            # Create cases table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS cases (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    district VARCHAR(255) NOT NULL,
                    station VARCHAR(255) NOT NULL,
                    fir_number VARCHAR(50) NOT NULL,
                    incharge_case VARCHAR(255) NOT NULL,
                    overview TEXT NOT NULL,
                    judgement TEXT DEFAULT NULL,
                    status ENUM('Pending', 'Closed') NOT NULL,
                    fir_file VARCHAR(255),
                    case_date DATE,
                    case_type VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    created_by INT,
                    updated_by INT,
                    FOREIGN KEY (created_by) REFERENCES admins(id) ON DELETE CASCADE,
                    FOREIGN KEY (updated_by) REFERENCES admins(id) ON DELETE CASCADE
                )
            ''')

            # Create case_logs table for trigger logging
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS case_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    case_id INT NOT NULL,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    action VARCHAR(50),
                    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
                )
            ''')

            # Drop and recreate trigger
            cursor.execute('DROP TRIGGER IF EXISTS trg_case_update')
            cursor.execute('''
                CREATE TRIGGER trg_case_update
                AFTER UPDATE ON cases
                FOR EACH ROW
                BEGIN
                    INSERT INTO case_logs (case_id, action)
                    VALUES (NEW.id, 'Updated');
                END
            ''')

            # Victims table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS victims (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    case_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    address TEXT NOT NULL,
                    phone VARCHAR(15) NOT NULL,
                    age INT,
                    aadhaar VARCHAR(12),
                    photo VARCHAR(255),
                    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
                )
            ''')

            # Suspects table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS suspects (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    case_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    address TEXT NOT NULL,
                    phone VARCHAR(15) NOT NULL,
                    age INT,
                    aadhaar VARCHAR(12),
                    photo VARCHAR(255),
                    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
                )
            ''')

            # Criminals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS criminals (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    case_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    address TEXT NOT NULL,
                    phone VARCHAR(15) NOT NULL,
                    age INT,
                    aadhaar VARCHAR(12),
                    photo VARCHAR(255),
                    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
                )
            ''')

        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"❌ Error occurred: {e}")
    finally:
        connection.close()

# Default admin user creation
def create_admin():
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            hashed_password = bcrypt.generate_password_hash("admin123").decode('utf-8')
            cursor.execute('''
                INSERT INTO admins (username, password_hash) 
                VALUES (%s, %s) 
                ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash)
            ''', ('admin', hashed_password))
        connection.commit()
    except Exception as e:
        connection.rollback()
        print(f"❌ Error occurred: {e}")
    finally:
        connection.close()

if __name__ == "__main__":
    create_tables()
    create_admin()
