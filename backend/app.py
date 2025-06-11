from flask import Flask, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from datetime import datetime

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# MySQL configurations
app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('DB_PORT', 3306))
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')
ENCRYPT_KEY = os.getenv('MYSQL_ENCRYPT_KEY')

mysql = MySQL(app)

@app.route('/api/validate-company/<int:company_id>', methods=['GET'])
def validate_company(company_id):
    print(f"Validating company_id: {company_id}")  # Debug log
    cursor = mysql.connection.cursor()
    query = """
        SELECT DISTINCT company_id 
        FROM payroll_payslip 
        WHERE company_id = %s 
        LIMIT 1
    """
    print(f"Executing query: {query} with params: ({company_id},)")  # Debug log
    cursor.execute(query, (company_id,))
    result = cursor.fetchone()
    print(f"Query result: {result}")  # Debug log
    cursor.close()
    return jsonify({'valid': result is not None})

@app.route('/api/search-employees/<int:company_id>/<string:query>', methods=['GET'])
def search_employees(company_id, query):
    print(f"Searching employees for company_id: {company_id}, query: {query}")  # Debug log
    cursor = mysql.connection.cursor()
    
    # Search for first 5 matching employee IDs
    search_query = """
        SELECT DISTINCT emp_id 
        FROM payroll_payslip 
        WHERE company_id = %s 
        AND CAST(emp_id AS CHAR) LIKE %s
        ORDER BY emp_id 
        LIMIT 5
    """
    search_param = f"{query}%"
    print(f"Executing query: {search_query} with params: ({company_id}, {search_param})")  # Debug log
    
    cursor.execute(search_query, (company_id, search_param))
    employees = [str(row[0]) for row in cursor.fetchall()]  # Convert to string to ensure consistent type
    print(f"Found employees: {employees}")  # Debug log
    
    cursor.close()
    return jsonify({'employees': employees})

@app.route('/api/dates/<int:company_id>/<string:emp_id>', methods=['GET'])
def get_employee_dates(company_id, emp_id):
    print(f"Fetching dates for company_id: {company_id}, emp_id: {emp_id}")
    cursor = mysql.connection.cursor()
    
    # First get period_from dates
    period_from_query = """
        SELECT DISTINCT period_from
        FROM payroll_payslip
        WHERE company_id = %s 
        AND emp_id = %s
        AND period_from IS NOT NULL
        ORDER BY period_from DESC
    """
    print(f"Executing period_from query: {period_from_query}")
    cursor.execute(period_from_query, (company_id, emp_id))
    period_from_results = cursor.fetchall()
    print(f"Found {len(period_from_results)} period_from dates")
    
    # Then get period_to dates
    period_to_query = """
        SELECT DISTINCT period_to
        FROM payroll_payslip
        WHERE company_id = %s 
        AND emp_id = %s
        AND period_to IS NOT NULL
        ORDER BY period_to DESC
    """
    print(f"Executing period_to query: {period_to_query}")
    cursor.execute(period_to_query, (company_id, emp_id))
    period_to_results = cursor.fetchall()
    print(f"Found {len(period_to_results)} period_to dates")
    
    # Format dates
    period_from_dates = []
    period_to_dates = []
    
    for row in period_from_results:
        if row[0] is not None:
            try:
                period_from_dates.append(row[0].strftime('%Y-%m-%d'))
            except AttributeError as e:
                print(f"Error formatting period_from date {row[0]}: {e}")
                continue
    
    for row in period_to_results:
        if row[0] is not None:
            try:
                period_to_dates.append(row[0].strftime('%Y-%m-%d'))
            except AttributeError as e:
                print(f"Error formatting period_to date {row[0]}: {e}")
                continue
    
    print(f"Returning {len(period_from_dates)} period_from dates and {len(period_to_dates)} period_to dates")
    cursor.close()
    return jsonify({
        'period_from_dates': period_from_dates,
        'period_to_dates': period_to_dates
    })

@app.route('/api/dates/<int:company_id>', methods=['GET'])
def get_company_dates(company_id):
    print(f"Fetching dates for company_id: {company_id}")
    cursor = mysql.connection.cursor()
    
    # First get period_from dates
    period_from_query = """
        SELECT DISTINCT period_from
        FROM payroll_payslip
        WHERE company_id = %s
        AND period_from IS NOT NULL
        ORDER BY period_from DESC
    """
    print(f"Executing period_from query: {period_from_query}")
    cursor.execute(period_from_query, (company_id,))
    period_from_results = cursor.fetchall()
    print(f"Found {len(period_from_results)} period_from dates")
    
    # Then get period_to dates
    period_to_query = """
        SELECT DISTINCT period_to
        FROM payroll_payslip
        WHERE company_id = %s
        AND period_to IS NOT NULL
        ORDER BY period_to DESC
    """
    print(f"Executing period_to query: {period_to_query}")
    cursor.execute(period_to_query, (company_id,))
    period_to_results = cursor.fetchall()
    print(f"Found {len(period_to_results)} period_to dates")
    
    # Format dates
    period_from_dates = []
    period_to_dates = []
    
    for row in period_from_results:
        if row[0] is not None:
            try:
                period_from_dates.append(row[0].strftime('%Y-%m-%d'))
            except AttributeError as e:
                print(f"Error formatting period_from date {row[0]}: {e}")
                continue
    
    for row in period_to_results:
        if row[0] is not None:
            try:
                period_to_dates.append(row[0].strftime('%Y-%m-%d'))
            except AttributeError as e:
                print(f"Error formatting period_to date {row[0]}: {e}")
                continue
    
    print(f"Returning {len(period_from_dates)} period_from dates and {len(period_to_dates)} period_to dates")
    cursor.close()
    return jsonify({
        'period_from_dates': period_from_dates,
        'period_to_dates': period_to_dates
    })

@app.route('/api/analytics/<int:company_id>/<emp_id>/<string:period_from>/<string:period_to>', methods=['GET'])
def get_analytics(company_id, emp_id, period_from, period_to):
    print(f"Fetching analytics for company_id: {company_id}, emp_id: {emp_id}, period: {period_from} to {period_to}")
    try:
        cursor = mysql.connection.cursor()
        
        # Query to get the encrypted data
        query = """
            SELECT regular_pay, night_diff, overtime_pay, sunday_holiday, 
                   adjustment_1, adjustment_2, gross_pay
            FROM payroll_payslip 
            WHERE company_id = %s
            AND period_from >= %s
            AND period_to <= %s
        """
        
        if emp_id != 'all':
            query += " AND emp_id = %s"
            params = (company_id, period_from, period_to, emp_id)
        else:
            params = (company_id, period_from, period_to)
            
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if not rows:
            return jsonify({'error': 'No data found for the specified period'}), 404
            
        # Initialize sums
        sums = {
            'regular_pay': 0.0,
            'night_diff': 0.0,
            'overtime_pay': 0.0,
            'sunday_holiday': 0.0,
            'adjustment_1': 0.0,
            'adjustment_2': 0.0,
            'gross_pay': 0.0
        }
        
        # Process each row
        for row in rows:
            # Process each field
            for i, field in enumerate(['regular_pay', 'night_diff', 'overtime_pay', 'sunday_holiday', 'adjustment_1', 'adjustment_2', 'gross_pay']):
                if row[i]:  # If the field is not None
                    # Decrypt the value
                    decrypt_query = "SELECT CAST(AES_DECRYPT(%s, %s) AS DECIMAL(10,2)) as value"
                    cursor.execute(decrypt_query, (row[i], ENCRYPT_KEY))
                    result = cursor.fetchone()
                    if result and result[0] is not None:
                        sums[field] += float(result[0])
        
        # Format the response to match frontend expectations
        analytics = {
            'basic': round(sums['regular_pay'], 2),
            'nsd': round(sums['night_diff'], 2),
            'ot': round(sums['overtime_pay'], 2),
            'holiday': round(sums['sunday_holiday'], 2),
            'retro': round(sums['adjustment_1'], 2),
            'adj': round(sums['adjustment_2'], 2),
            'total_salary': round(sums['gross_pay'], 2)
        }
        
        return jsonify(analytics)
        
    except Exception as e:
        print(f"Error in get_analytics: {str(e)}")
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(debug=True, port=5002) 