import sqlite3

# Connect to the database (or create it)
conn = sqlite3.connect('slay.db')
cursor = conn.cursor()

# Enable foreign key constraint support in SQLite
cursor.execute("PRAGMA foreign_keys = ON")

# Create Users DB table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            image TEXT,
            skin_tone TEXT
        )
''')

# Create Image DB table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Images (
        item_id TEXT PRIMARY KEY,
        item_name TEXT,
        item_desc TEXT,
        category TEXT,
        item_image BLOB,
        color TEXT,
        FOREIGN KEY(item_id) REFERENCES Vector(item_id)
    )
''')

# Create User Cart table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS UserCart (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        UUID TEXT,
        item_id TEXT,
        purchased INTEGER,  -- 0 for not purchased, 1 for purchased
        date_of_purchase TEXT,
        FOREIGN KEY(UUID) REFERENCES Users(UUID),
        FOREIGN KEY(item_id) REFERENCES Vector(item_id)
    )
''')

# Create Preference DB table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Preference (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        UUID TEXT,
        item_id TEXT,
        preference_vector TEXT,
        non_preference_vector TEXT,
        added_to_cart INTEGER,  -- 0 for not added, 1 for added
        timestamp TEXT,
        FOREIGN KEY(UUID) REFERENCES Users(UUID),
        FOREIGN KEY(item_id) REFERENCES Vector(item_id)
    )
''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully!")
