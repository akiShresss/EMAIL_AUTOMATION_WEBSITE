import sqlite3

conn = sqlite3.connect("clients.db")
cursor = conn.cursor()

# Create clients table
cursor.execute('''
CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE
)
''')

# Create templates table
cursor.execute('''
CREATE TABLE IF NOT EXISTS templates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    subject TEXT NOT NULL,
    body TEXT NOT NULL
)
''')

# Optional: Insert a sample client and template
cursor.execute("INSERT OR IGNORE INTO clients (name, email) VALUES (?, ?)", ("John Doe", "john@example.com"))
cursor.execute("INSERT OR IGNORE INTO templates (name, subject, body) VALUES (?, ?, ?)", (
    "Welcome Email", 
    "Welcome to our service, {name}!", 
    "Hi {name},\n\nWelcome aboard! Visit [our site]{https://example.com} to get started."
))

conn.commit()
conn.close()
print("Database initialized.")
