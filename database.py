import sqlite3

DATABASE_NAME = "database.db"

def get_db_connection():
    """Connects to the SQLite database with dictionary-style column access."""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initializes tables for User Profile, Trusted Contacts, and Alert Logs."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # 1. User Profile & Settings Table (with POPIA consent tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            phone_number TEXT UNIQUE NOT NULL,
            popia_consent INTEGER DEFAULT 1,
            floating_button_enabled INTEGER DEFAULT 1,
            max_accounts INTEGER DEFAULT 2
        )
    ''')

    # 2. Trusted Emergency Contacts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trusted_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_phone TEXT NOT NULL,
            contact_name TEXT NOT NULL,
            contact_phone TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            FOREIGN KEY (user_phone) REFERENCES user_profile (phone_number) ON DELETE CASCADE
        )
    ''')

    # 3. Emergency Alert Logs Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone_number TEXT,
            latitude REAL,
            longitude REAL,
            status TEXT DEFAULT 'DISPATCHED',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("[DATABASE] SQLite tables initialized successfully.")


# --- CRUD & POPIA DATA FUNCTIONS ---

def save_user_profile(username, phone_number, popia_consent=1):
    """Saves or updates user registration and POPIA consent state."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO user_profile (username, phone_number, popia_consent)
            VALUES (?, ?, ?)
            ON CONFLICT(phone_number) DO UPDATE SET username=excluded.username
        ''', (username, phone_number, popia_consent))
        conn.commit()
        return True
    except sqlite3.Error as e:
        print(f"[DATABASE ERROR] {e}")
        return False
    finally:
        conn.close()

def log_alert(phone_number, latitude, longitude):
    """Records an active GPS emergency dispatch event."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO alert_logs (phone_number, latitude, longitude)
        VALUES (?, ?, ?)
    ''', (phone_number, latitude, longitude))
    conn.commit()
    conn.close()

def purge_all_user_data(phone_number):
    """POPIA Section 24 compliance: Wipes all user records permanently."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM user_profile WHERE phone_number = ?', (phone_number,))
    cursor.execute('DELETE FROM trusted_contacts WHERE user_phone = ?', (phone_number,))
    cursor.execute('DELETE FROM alert_logs WHERE phone_number = ?', (phone_number,))
    conn.commit()
    conn.close()
    print(f"[DATABASE] Purged all records for {phone_number}")

if __name__ == '__main__':
    init_db()
    