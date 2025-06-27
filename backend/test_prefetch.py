import os
from flask import Flask
from flask_mysqldb import MySQL
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('DB_PORT', 3306))
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')
ENCRYPT_KEY = os.getenv('MYSQL_ENCRYPT_KEY')

mysql = MySQL(app)

# Test parameters
test_company_id = 206
test_fields = ['overtime_pay', 'night_diff', 'basic_pay', 'sunday_holiday']
test_location_id = 126
test_period_from = '2025-03-03'
test_period_to = '2025-05-17'
aggregation_type = 'separate'

# Decrypted field SQL
field_sql = ', '.join([
    f"CAST(AES_DECRYPT({field}, '{ENCRYPT_KEY}') AS DECIMAL(10,2)) AS {field}" for field in test_fields
])

# Employee name fields (decrypted)
name_fields = [
    f"CAST(AES_DECRYPT(e.last_name, '{ENCRYPT_KEY}') AS CHAR(150) CHARACTER SET utf8) AS last_name",
    f"CAST(AES_DECRYPT(e.first_name, '{ENCRYPT_KEY}') AS CHAR(150) CHARACTER SET utf8) AS first_name"
]

# Build the query
query = f'''
    SELECT p.emp_id, {', '.join(name_fields)}, p.period_from, p.period_to, {field_sql}
    FROM payroll_payslip p
    JOIN employee e ON p.emp_id = e.emp_id
    WHERE p.company_id = %s
      AND p.period_from >= %s AND p.period_to <= %s
      AND p.emp_id IN (
        SELECT emp_id FROM employee_payroll_information epi
        WHERE epi.location_and_offices_id = %s
      )
    ORDER BY p.period_from, p.period_to, last_name, first_name
'''

params = (test_company_id, test_period_from, test_period_to, test_location_id)

def fetch_and_print():
    with app.app_context():
        cursor = mysql.connection.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        data = [dict(zip(colnames, row)) for row in rows]
        print(f"Fetched {len(data)} rows:")
        for row in data:
            print(row)
        cursor.close()

if __name__ == '__main__':
    fetch_and_print() 