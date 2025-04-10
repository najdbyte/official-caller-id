import mysql.connector

# Connect to your MySQL database
conn = mysql.connector.connect(
    host="localhost",
    user="root",  # Change this if your MySQL username is different
    password="6250",  # Replace with your MySQL password
    database="official_caller_id"
)

cursor = conn.cursor()

# Query the table
cursor.execute("SELECT * FROM registered_numbers")
results = cursor.fetchall()

# Print the results
print("📞 Registered Official Numbers:")
print("--------------------------------")
for row in results:
    print(f"ID: {row[0]} | Number: {row[1]} | Organization: {row[2]}")

conn.close()
