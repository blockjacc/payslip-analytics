from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os
from datetime import datetime
import logging
import sys
from payslip_fields import get_field_display_names_by_category, FieldCategory

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
        
        # Get selected fields from query parameters, default to a set of basic fields if not provided
        selected_fields = request.args.get('fields', None)
        if selected_fields:
            try:
                import json
                selected_fields = json.loads(selected_fields)
                if not isinstance(selected_fields, list):
                    selected_fields = None
            except:
                selected_fields = None
        
        # Default fields if none provided
        if not selected_fields:
            selected_fields = [
                'basic_pay', 'regular_pay', 'night_diff', 'overtime_pay', 'sunday_holiday',
                'adjustment_1', 'adjustment_2', 'gross_pay', 'absences', 'tardiness_pay',
                'undertime_pay', 'paid_leave_amount', 'allowances', 'de_minimis',
                'bonuses', 'other_compensation', 'hazard_pay'
            ]
            
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
                # Dynamically build the query based on selected fields
                query_fields = ", ".join(selected_fields)
                query = f"""
                    SELECT {query_fields}
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
                    
                # Initialize sums for this period with selected fields
                period_sums = {field: 0.0 for field in selected_fields}
                
                # Process each row for this period
                for row in rows:
                    for i, field in enumerate(selected_fields):
                        if row[i] and row[i] != 'NO_AUTO_VALUE_ON_ZERO':
                            decrypt_query = "SELECT CAST(AES_DECRYPT(%s, %s) AS DECIMAL(10,2)) as value"
                            cursor.execute(decrypt_query, (row[i], ENCRYPT_KEY))
                            decrypted_result = cursor.fetchone()
                            if decrypted_result and decrypted_result[0] is not None:
                                period_sums[field] += float(decrypted_result[0])
                
                # Add period data to result
                period_analytics = {}
                for field, value in period_sums.items():
                    # Map DB field names to API field names if needed
                    api_field = field
                    period_analytics[api_field] = round(value, 2)
                
                # Add total_salary (gross_pay) if it exists
                if 'gross_pay' in period_sums:
                    period_analytics['total_salary'] = round(period_sums['gross_pay'], 2)
                
                result['periods'].append({
                    'period': {
                        'from': period_start.strftime('%Y-%m-%d'),
                        'to': period_end.strftime('%Y-%m-%d')
                    },
                    'analytics': period_analytics
                })
            
            cursor.close()
            return jsonify(result)
            
        # For single/aggregate view
        # Dynamically build the query based on selected fields
        query_fields = ", ".join(selected_fields)
        query = f"""
            SELECT {query_fields}, period_from, period_to
            FROM payroll_payslip 
            WHERE company_id = %s
        """
        
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
            
        # Initialize sums with selected fields
        sums = {field: 0.0 for field in selected_fields}
            
        # Process each row
        for row in rows:
            for i, field in enumerate(selected_fields):
                if row[i] and row[i] != 'NO_AUTO_VALUE_ON_ZERO':
                    decrypt_query = "SELECT CAST(AES_DECRYPT(%s, %s) AS DECIMAL(10,2)) as value"
                    cursor.execute(decrypt_query, (row[i], ENCRYPT_KEY))
                    decrypted_result = cursor.fetchone()
                    if decrypted_result and decrypted_result[0] is not None:
                        sums[field] += float(decrypted_result[0])
        
        # Create result object with field sums
        result = {}
        for field, value in sums.items():
            # Map DB field names to API field names if needed
            api_field = field
            result[api_field] = round(value, 2)
        
        # Add total_salary (gross_pay) if it exists
        if 'gross_pay' in sums:
            result['total_salary'] = round(sums['gross_pay'], 2)
        
        cursor.close()
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error in analytics: {str(e)}")
        return jsonify({'error': f'Failed to retrieve analytics data: {str(e)}'}), 500

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

@app.route('/api/payslip-fields', methods=['GET'])
def get_payslip_fields():
    try:
        # Get field display names by category
        amount_fields = get_field_display_names_by_category(FieldCategory.AMOUNTS)
        hour_fields = get_field_display_names_by_category(FieldCategory.HOURS)
        tax_fields = get_field_display_names_by_category(FieldCategory.TAXES)
        
        # Return the field mappings
        return jsonify({
            'amount_fields': amount_fields,
            'hour_fields': hour_fields,
            'tax_fields': tax_fields
        })
    except Exception as e:
        app.logger.error(f"Error fetching payslip fields: {str(e)}")
        return jsonify({'error': 'Failed to retrieve payslip fields'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002) 