from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from datetime import datetime
import logging
import sys

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Reduce Flask logging output
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
app.logger.setLevel(logging.ERROR)

# Disable Flask development server banner
cli = sys.modules['flask.cli']
cli.show_server_banner = lambda *x: None

# MySQL configurations
app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('DB_PORT', 3306))
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')
ENCRYPT_KEY = os.getenv('MYSQL_ENCRYPT_KEY')

mysql = MySQL(app)

@app.route('/api/analytics/<int:company_id>/<emp_id>/<string:period_from>/<string:period_to>/<string:aggregation_type>', methods=['GET'])
def get_analytics(company_id, emp_id, period_from, period_to, aggregation_type='single'):
    try:
        # Validate parameters
        if not all([company_id, emp_id, period_from, period_to]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Validate dates
        try:
            datetime.strptime(period_from, '%Y-%m-%d')
            datetime.strptime(period_to, '%Y-%m-%d')
        except ValueError as e:
            return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
            
        cursor = mysql.connection.cursor()
        
        # For separate view, first get all distinct periods in the range
        if aggregation_type == 'separate':
            # Initialize result structure for separate view
            result = {'periods': []}

            periods_query = """
                SELECT DISTINCT period_from, period_to
                FROM payroll_payslip
                WHERE company_id = %s
                AND period_from >= %s AND period_to <= %s
            """
            
            if emp_id != 'all':
                periods_query += " AND emp_id = %s"
                cursor.execute(periods_query, (company_id, period_from, period_to, emp_id))
            else:
                cursor.execute(periods_query, (company_id, period_from, period_to))
                
            periods = cursor.fetchall()
            if not periods:
                return jsonify({'error': 'No periods found'}), 404
                
            # Convert periods to list and sort by start date
            periods = list(periods)
            periods.sort(key=lambda x: x[0])
            
            # Process each period
            for period_start, period_end in periods:
                # Base query to get the encrypted data for this period
                query = """
                    SELECT regular_pay, night_diff, overtime_pay, sunday_holiday, 
                           adjustment_1, adjustment_2, gross_pay, absences, tardiness_pay,
                           undertime_pay, paid_leave_amount, allowances, de_minimis,
                           bonuses, other_compensation, hazard_pay
                    FROM payroll_payslip 
                    WHERE company_id = %s
                    AND period_from = %s AND period_to = %s
                """
                
                params = [company_id, period_start, period_end]
                if emp_id != 'all':
                    query += " AND emp_id = %s"
                    params.append(emp_id)
                    
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                if not rows:
                    continue
                    
                # Initialize sums for this period
                period_sums = {
                    'regular_pay': 0.0,
                    'night_diff': 0.0,
                    'overtime_pay': 0.0,
                    'sunday_holiday': 0.0,
                    'adjustment_1': 0.0,
                    'adjustment_2': 0.0,
                    'gross_pay': 0.0,
                    'absences': 0.0,
                    'tardiness_pay': 0.0,
                    'undertime_pay': 0.0,
                    'paid_leave_amount': 0.0,
                    'allowances': 0.0,
                    'de_minimis': 0.0,
                    'bonuses': 0.0,
                    'other_compensation': 0.0,
                    'hazard_pay': 0.0
                }
                
                # Process each row for this period
                for row in rows:
                    field_names = list(period_sums.keys())
                    for i, field in enumerate(field_names):
                        if row[i] and row[i] != 'NO_AUTO_VALUE_ON_ZERO':
                            decrypt_query = "SELECT CAST(AES_DECRYPT(%s, %s) AS DECIMAL(10,2)) as value"
                            cursor.execute(decrypt_query, (row[i], ENCRYPT_KEY))
                            decrypted_result = cursor.fetchone()
                            if decrypted_result and decrypted_result[0] is not None:
                                period_sums[field] += float(decrypted_result[0])
                
                # Calculate basic pay for this period
                basic_pay = period_sums['regular_pay'] - period_sums['absences'] - period_sums['tardiness_pay'] - period_sums['undertime_pay']
                
                # Add period data to result
                result['periods'].append({
                    'period': {
                        'from': period_start.strftime('%Y-%m-%d'),
                        'to': period_end.strftime('%Y-%m-%d')
                    },
                    'analytics': {
                        'basic': round(basic_pay, 2),
                        'nsd': round(period_sums['night_diff'], 2),
                        'ot': round(period_sums['overtime_pay'], 2),
                        'holiday': round(period_sums['sunday_holiday'], 2),
                        'paid_leave': round(period_sums['paid_leave_amount'], 2),
                        'allowances': round(period_sums['allowances'], 2),
                        'deminimis': round(period_sums['de_minimis'], 2),
                        'bonuses': round(period_sums['bonuses'], 2),
                        'other_comp': round(period_sums['other_compensation'], 2),
                        'hazard_pay': round(period_sums['hazard_pay'], 2),
                        'retro': round(period_sums['adjustment_1'], 2),
                        'adj': round(period_sums['adjustment_2'], 2),
                        'total_salary': round(period_sums['gross_pay'], 2)
                    }
                })
            
            cursor.close()
            return jsonify(result)
            
        # For single/aggregate view, use existing logic
        base_query = """
            SELECT regular_pay, night_diff, overtime_pay, sunday_holiday, 
                   adjustment_1, adjustment_2, gross_pay, absences, tardiness_pay,
                   undertime_pay, paid_leave_amount, allowances, de_minimis,
                   bonuses, other_compensation, hazard_pay,
                   period_from, period_to
            FROM payroll_payslip 
            WHERE company_id = %s
        """
        
        query = base_query
        
        # Handle date filtering based on aggregation type
        if aggregation_type == 'single':
            date_filter = " AND period_from = %s AND period_to = %s"
        else:  # 'aggregate'
            date_filter = " AND period_from >= %s AND period_to <= %s"
        query += date_filter
        
        # Add employee filter if not 'all'
        if emp_id != 'all':
            emp_filter = " AND emp_id = %s"
            query += emp_filter
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
            'gross_pay': 0.0,
            'absences': 0.0,
            'tardiness_pay': 0.0,
            'undertime_pay': 0.0,
            'paid_leave_amount': 0.0,
            'allowances': 0.0,
            'de_minimis': 0.0,
            'bonuses': 0.0,
            'other_compensation': 0.0,
            'hazard_pay': 0.0
        }
        
        # Process each row
        for row_idx, row in enumerate(rows):
            field_names = list(sums.keys())
            for i, field in enumerate(field_names):
                try:
                    if row[i] and row[i] != 'NO_AUTO_VALUE_ON_ZERO':
                        decrypt_query = "SELECT CAST(AES_DECRYPT(%s, %s) AS DECIMAL(10,2)) as value"
                        cursor.execute(decrypt_query, (row[i], ENCRYPT_KEY))
                        decrypted_result = cursor.fetchone()
                        if decrypted_result and decrypted_result[0] is not None:
                            sums[field] += float(decrypted_result[0])
                except Exception as e:
                    pass
        
        # Calculate basic pay
        basic_pay = sums['regular_pay'] - sums['absences'] - sums['tardiness_pay'] - sums['undertime_pay']
        
        # Format response
        analytics = {
            'basic': round(basic_pay, 2),
            'nsd': round(sums['night_diff'], 2),
            'ot': round(sums['overtime_pay'], 2),
            'holiday': round(sums['sunday_holiday'], 2),
            'paid_leave': round(sums['paid_leave_amount'], 2),
            'allowances': round(sums['allowances'], 2),
            'deminimis': round(sums['de_minimis'], 2),
            'bonuses': round(sums['bonuses'], 2),
            'other_comp': round(sums['other_compensation'], 2),
            'hazard_pay': round(sums['hazard_pay'], 2),
            'retro': round(sums['adjustment_1'], 2),
            'adj': round(sums['adjustment_2'], 2),
            'total_salary': round(sums['gross_pay'], 2)
        }
        
        cursor.close()
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/validate-company/<int:company_id>', methods=['GET'])
def validate_company(company_id):
    cursor = mysql.connection.cursor()
    query = """
        SELECT DISTINCT company_id 
        FROM payroll_payslip 
        WHERE company_id = %s 
        LIMIT 1
    """
    cursor.execute(query, (company_id,))
    result = cursor.fetchone()
    cursor.close()
    return jsonify({'valid': result is not None})

@app.route('/api/search-employees/<int:company_id>/<string:query>', methods=['GET'])
def search_employees(company_id, query):
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
    
    cursor.execute(search_query, (company_id, search_param))
    employees = [str(row[0]) for row in cursor.fetchall()]  # Convert to string to ensure consistent type
    
    cursor.close()
    return jsonify({'employees': employees})

@app.route('/api/dates/<int:company_id>/<string:emp_id>', methods=['GET'])
def get_employee_dates(company_id, emp_id):
    cursor = mysql.connection.cursor()
    
    # First get period_from dates
    period_from_query = """
        SELECT DISTINCT period_from
        FROM payroll_payslip
        WHERE company_id = %s
        AND period_from IS NOT NULL
    """
    
    params = [company_id]
    if emp_id != 'all':
        period_from_query += " AND emp_id = %s"
        params.append(emp_id)
    
    period_from_query += " ORDER BY period_from DESC"
    cursor.execute(period_from_query, tuple(params))
    period_from_results = cursor.fetchall()
    
    # Then get period_to dates
    period_to_query = """
        SELECT DISTINCT period_to
        FROM payroll_payslip
        WHERE company_id = %s
        AND period_to IS NOT NULL
    """
    
    params = [company_id]
    if emp_id != 'all':
        period_to_query += " AND emp_id = %s"
        params.append(emp_id)
    
    period_to_query += " ORDER BY period_to DESC"
    cursor.execute(period_to_query, tuple(params))
    period_to_results = cursor.fetchall()
    
    # Format dates
    period_from_dates = []
    for row in period_from_results:
        try:
            date_str = row[0].strftime('%Y-%m-%d')
            period_from_dates.append(date_str)
        except Exception:
            pass
            
    period_to_dates = []
    for row in period_to_results:
        try:
            date_str = row[0].strftime('%Y-%m-%d')
            period_to_dates.append(date_str)
        except Exception:
            pass
    
    cursor.close()
    return jsonify({
        'period_from_dates': period_from_dates,
        'period_to_dates': period_to_dates
    })

@app.route('/api/dates/<int:company_id>', methods=['GET'])
def get_company_dates(company_id):
    cursor = mysql.connection.cursor()
    
    # First get period_from dates
    period_from_query = """
        SELECT DISTINCT period_from
        FROM payroll_payslip
        WHERE company_id = %s
        AND period_from IS NOT NULL
        ORDER BY period_from DESC
    """
    cursor.execute(period_from_query, (company_id,))
    period_from_results = cursor.fetchall()
    
    # Then get period_to dates
    period_to_query = """
        SELECT DISTINCT period_to
        FROM payroll_payslip
        WHERE company_id = %s
        AND period_to IS NOT NULL
        ORDER BY period_to DESC
    """
    cursor.execute(period_to_query, (company_id,))
    period_to_results = cursor.fetchall()
    
    # Format dates
    period_from_dates = []
    for row in period_from_results:
        try:
            date_str = row[0].strftime('%Y-%m-%d')
            period_from_dates.append(date_str)
        except Exception:
            pass
            
    period_to_dates = []
    for row in period_to_results:
        try:
            date_str = row[0].strftime('%Y-%m-%d')
            period_to_dates.append(date_str)
        except Exception:
            pass
    
    cursor.close()
    return jsonify({
        'period_from_dates': period_from_dates,
        'period_to_dates': period_to_dates
    })

if __name__ == '__main__':
    app.run(debug=True, port=5002) 