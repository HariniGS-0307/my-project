import psycopg2

try:
    # Connect to your database
    conn = psycopg2.connect(
        host="localhost",
        database="mydb",
        user="postgres",
        password="yourpassword"  # replace with your PostgreSQL password
    )
    
    # Create a cursor object
    cur = conn.cursor()
    
    print("Connection successful!")

except Exception as e:
    print("Error connecting to database:", e)

