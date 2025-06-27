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
        
        # Get payroll group ID from query parameters (optional)
        payroll_group_id = request.args.get('payroll_group_id', None)
        
        # Get additional filter parameters from settings tables (optional)
        department_id = request.args.get('department_id', None)
        rank_id = request.args.get('rank_id', None)
        employment_type_id = request.args.get('employment_type_id', None)
        position_id = request.args.get('position_id', None)
        cost_center_id = request.args.get('cost_center_id', None)
        project_id = request.args.get('project_id', None)
        location_id = request.args.get('location_id', None)
        
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
            
            params = [company_id, period_from, period_to]
            
            if emp_id != 'all':
                periods_query += " AND emp_id = %s"
                params.append(emp_id)
            
            if payroll_group_id:
                periods_query += " AND payroll_group_id = %s"
                params.append(payroll_group_id)
            
            # Add additional filters from settings tables
            if department_id:
                periods_query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE department_id = %s)"
                params.append(department_id)
            
            if rank_id:
                periods_query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE rank_id = %s)"
                params.append(rank_id)
            
            if employment_type_id:
                periods_query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE employment_type = %s)"
                params.append(employment_type_id)
            
            if position_id:
                periods_query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE position = %s)"
                params.append(position_id)
            
            if cost_center_id:
                periods_query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE cost_center = %s)"
                params.append(cost_center_id)
            
            if project_id:
                periods_query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE project_id = %s)"
                params.append(project_id)
            
            if location_id:
                periods_query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE location_and_offices_id = %s)"
                params.append(location_id)
            
            cursor.execute(periods_query, tuple(params))
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
                
                if payroll_group_id:
                    query += " AND payroll_group_id = %s"
                    params.append(payroll_group_id)
                    
                # Add additional filters from settings tables
                if department_id:
                    query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE department_id = %s)"
                    params.append(department_id)
                
                if rank_id:
                    query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE rank_id = %s)"
                    params.append(rank_id)
                
                if employment_type_id:
                    query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE employment_type = %s)"
                    params.append(employment_type_id)
                
                if position_id:
                    query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE position = %s)"
                    params.append(position_id)
                
                if cost_center_id:
                    query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE cost_center = %s)"
                    params.append(cost_center_id)
                
                if project_id:
                    query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE project_id = %s)"
                    params.append(project_id)
                
                if location_id:
                    query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE location_and_offices_id = %s)"
                    params.append(location_id)
                
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
        
        # Build parameters array
        params = [company_id, period_from, period_to]
        
        # Add employee filter if not 'all'
        if emp_id != 'all':
            emp_filter = " AND emp_id = %s"
            query += emp_filter
            params.append(emp_id)
        
        # Add payroll group filter if provided
        if payroll_group_id:
            query += " AND payroll_group_id = %s"
            params.append(payroll_group_id)
        
        # Add additional filters from settings tables
        if department_id:
            query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE department_id = %s)"
            params.append(department_id)
        
        if rank_id:
            query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE rank_id = %s)"
            params.append(rank_id)
        
        if employment_type_id:
            query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE employment_type = %s)"
            params.append(employment_type_id)
        
        if position_id:
            query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE position = %s)"
            params.append(position_id)
        
        if cost_center_id:
            query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE cost_center = %s)"
            params.append(cost_center_id)
        
        if project_id:
            query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE project_id = %s)"
            params.append(project_id)
        
        if location_id:
            query += " AND emp_id IN (SELECT emp_id FROM employee_payroll_information WHERE location_and_offices_id = %s)"
            params.append(location_id)
        
        cursor.execute(query, tuple(params))
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

@app.route('/api/payroll-groups/<int:company_id>', methods=['GET'])
def get_payroll_groups(company_id):
    cursor = mysql.connection.cursor()
    
    # Get distinct payroll groups for the company
    query = """
        SELECT DISTINCT payroll_group_id 
        FROM payroll_payslip 
        WHERE company_id = %s 
        AND payroll_group_id IS NOT NULL
        ORDER BY payroll_group_id
    """
    
    cursor.execute(query, (company_id,))
    payroll_groups = [str(row[0]) for row in cursor.fetchall()]  # Convert to string for consistency
    
    cursor.close()
    return jsonify({'payroll_groups': payroll_groups})

@app.route('/api/dates/<int:company_id>/<string:emp_id>', methods=['GET'])
def get_employee_dates(company_id, emp_id):
    cursor = mysql.connection.cursor()
    
    # Get payroll group ID from query parameters (optional)
    payroll_group_id = request.args.get('payroll_group_id', None)
    
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
    
    if payroll_group_id:
        period_from_query += " AND payroll_group_id = %s"
        params.append(payroll_group_id)
    
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
    
    if payroll_group_id:
        period_to_query += " AND payroll_group_id = %s"
        params.append(payroll_group_id)
    
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
        # Get all field categories
        categories = {}
        for category in FieldCategory:
            categories[category.value] = get_field_display_names_by_category(category)
        # Also provide the old keys for compatibility
        return jsonify({
            'amount_fields': categories.get('AMOUNTS', {}),
            'hour_fields': categories.get('HOURS', {}),
            'tax_fields': categories.get('TAXES', {}),
            **categories
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/settings-options/<int:company_id>/<string:table_name>', methods=['GET'])
def get_settings_options(company_id, table_name):
    try:
        # Validate table name to prevent SQL injection
        valid_tables = {
            'department': {'id_field': 'dept_id', 'name_field': 'department_name'},
            'rank': {'id_field': 'rank_id', 'name_field': 'rank_name'},
            'employment_type': {'id_field': 'emp_type_id', 'name_field': 'name'},
            'position': {'id_field': 'position_id', 'name_field': 'position_name'},
            'cost_center': {'id_field': 'cost_center_id', 'name_field': 'cost_center_code'},
            'project': {'id_field': 'project_id', 'name_field': 'project_name'},
            'location_and_offices': {'id_field': 'location_and_offices_id', 'name_field': 'name'}
        }
        
        if table_name not in valid_tables:
            return jsonify({'error': 'Invalid table name'}), 400
        
        table_config = valid_tables[table_name]
        id_field = table_config['id_field']
        name_field = table_config['name_field']
        
        cursor = mysql.connection.cursor()
        
        # Query the settings table for active records
        query = f"""
            SELECT {id_field}, {name_field}
            FROM `{table_name}`
            WHERE company_id = %s AND status = 'Active'
            ORDER BY {name_field}
        """
        
        cursor.execute(query, (company_id,))
        rows = cursor.fetchall()
        cursor.close()
        
        # Format the response
        options = []
        for row in rows:
            options.append({
                'id': row[0],
                'name': row[1]
            })
        
        return jsonify({
            'table_name': table_name,
            'options': options,
            'count': len(options)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/analytics-prefetch/<int:company_id>/<string:period_from>/<string:period_to>/<string:aggregation_type>', methods=['GET'])
def analytics_prefetch(company_id, period_from, period_to, aggregation_type):
    try:
        import json
        ENCRYPT_KEY = os.getenv('MYSQL_ENCRYPT_KEY')
        # Parse fields from query param
        selected_fields = request.args.get('fields', None)
        if selected_fields:
            try:
                selected_fields = json.loads(selected_fields)
                if not isinstance(selected_fields, list):
                    selected_fields = None
            except:
                selected_fields = None
        if not selected_fields:
            return jsonify({'error': 'No fields specified'}), 400
        # Optional filters
        location_id = request.args.get('location_id', None)
        department_id = request.args.get('department_id', None)
        # ... add other filters as needed ...
        drilldown = request.args.get('drilldown', 'false').lower() == 'true'
        # Build SQL for selected fields
        field_sql = ', '.join([
            f"CAST(AES_DECRYPT(p.{field}, '{ENCRYPT_KEY}') AS DECIMAL(10,2)) AS {field}" for field in selected_fields
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
        '''
        params = [company_id, period_from, period_to]
        if location_id:
            query += ''' AND p.emp_id IN (
                SELECT emp_id FROM employee_payroll_information epi
                WHERE epi.location_and_offices_id = %s
            )'''
            params.append(location_id)
        # ... add other filters as needed ...
        query += ' ORDER BY p.period_from, p.period_to, last_name, first_name'
        cursor = mysql.connection.cursor()
        cursor.execute(query, tuple(params))
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        data = [dict(zip(colnames, row)) for row in rows]
        # Group by period if 'separate', else aggregate
        if aggregation_type == 'separate':
            periods = {}
            for row in data:
                period_key = (row['period_from'], row['period_to'])
                if period_key not in periods:
                    periods[period_key] = []
                periods[period_key].append(row)
            result = {'periods': []}
            for (from_date, to_date), employees in sorted(periods.items()):
                if drilldown:
                    # Drill-down: return all employee rows for this period
                    result['periods'].append({
                        'period': {'from': str(from_date), 'to': str(to_date)},
                        'employees': employees
                    })
                else:
                    # Summary: aggregate by field
                    summary = {field: 0.0 for field in selected_fields}
                    for emp in employees:
                        for field in selected_fields:
                            summary[field] += float(emp[field] or 0)
                    result['periods'].append({
                        'period': {'from': str(from_date), 'to': str(to_date)},
                        'summary': {k: round(v, 2) for k, v in summary.items()}
                    })
            if not drilldown:
                # Add total across all periods
                total = {field: 0.0 for field in selected_fields}
                for period in result['periods']:
                    for field in selected_fields:
                        total[field] += period['summary'][field]
                result['total'] = {k: round(v, 2) for k, v in total.items()}
            return jsonify(result)
        else:
            # Aggregate or single: all data in one group
            if drilldown:
                # Drill-down: return all employee rows
                return jsonify({'employees': data})
            else:
                # Summary: aggregate by field
                summary = {field: 0.0 for field in selected_fields}
                for row in data:
                    for field in selected_fields:
                        summary[field] += float(row[field] or 0)
                return jsonify({'summary': {k: round(v, 2) for k, v in summary.items()}})
    except Exception as e:
        app.logger.error(f"Error in analytics-prefetch: {str(e)}")
        return jsonify({'error': f'Failed to retrieve analytics-prefetch data: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002) 