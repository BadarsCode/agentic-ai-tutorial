import sqlite3

# Connect to database (creates it if not exists)
connection = sqlite3.connect("student.db")

cursor = connection.cursor()

# Create table (fixes syntax and data types)
tableinfo = """
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT(30),
    email TEXT,
    phone TEXT,
    address TEXT,
    class TEXT
);
"""

cursor.execute(tableinfo)

# ✅ Insert records (fixes: phone numbers, data types, commas, and field order)
cursor.execute("""INSERT INTO students (name, email, phone, address, class)
                  VALUES ('Aslam', 'aslam@gmail.com', '03081467623', 'Pakistan', '10th');""")
cursor.execute("""INSERT INTO students (name, email, phone, address, class)
                  VALUES ('Qamar', 'qamar@gmail.com', '0305020345', 'Pakistan', '9th');""")
cursor.execute("""INSERT INTO students (name, email, phone, address, class)
                  VALUES ('Molvi', 'molvi@gmail.com', '03023434545', 'usa', '10th');""")
cursor.execute("""INSERT INTO students (name, email, phone, address, class)
                  VALUES ('Subhan', 'subhan@gmail.com', '03083423543', 'india', '10th');""")

connection.commit()

print("The inserted records are:")
data = cursor.execute("SELECT * FROM students;")
for row in data:
    print(row)

connection.close()
