import psycopg2
conn = psycopg2.connect(host="34.72.164.60", dbname="FIS", user="postgres",
                                password="plazma12388", port=5432)
        
cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS Faculty_Account (
    faculty_Account_id INT PRIMARY KEY,
    name VARCHAR(255),
    age INT,
    email VARCHAR(255),
    password VARCHAR(255),
    gender VARCHAR(255)
);
            """)

conn.commit()
cur.close()
conn.close()  
