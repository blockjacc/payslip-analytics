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

# Utility function to get display name for a given id and table
def get_display_name(cursor, table, id_field, name_field, id_value, company_id):
    if not id_value:
        return None
    query = f"SELECT {name_field} FROM {table} WHERE {id_field} = %s AND company_id = %s AND status = 'Active' LIMIT 1"
    cursor.execute(query, (id_value, company_id))
    row = cursor.fetchone()
    return row[0] if row else None

# Reusable function for employee search with AES decryption and joins
def search_employees_by_name(cursor, company_id, name_search, context='all', limit=10):
    """
    Search employees by first name or last name with AES decryption.
    
    Args:
        cursor: Database cursor
        company_id: Company ID to filter by
        name_search: Search term for first/last name
        context: 'shifts', 'payslip', or 'all' - determines which tables to join
        limit: Maximum number of results to return
    
    Returns:
        List of employee dictionaries with emp_id, first_name, last_name, and context-specific fields
    """
    if not name_search or len(name_search) < 2:
        return []
    
    # Base query with employee name decryption
    base_query = """
        SELECT DISTINCT
            e.emp_id,
            CAST(AES_DECRYPT(e.last_name, %s) AS CHAR(150) CHARACTER SET utf8) AS last_name,
            CAST(AES_DECRYPT(e.first_name, %s) AS CHAR(150) CHARACTER SET utf8) AS first_name,
            COALESCE(lao.name, 'N/A') AS location_office,
            COALESCE(d.department_name, 'N/A') AS department_name,
            COALESCE(rk.rank_name, 'N/A') AS rank_name
        FROM employee e
        LEFT JOIN employee_payroll_information epi ON e.emp_id = epi.emp_id AND epi.company_id = %s
        LEFT JOIN location_and_offices lao ON epi.location_and_offices_id = lao.location_and_offices_id
        LEFT JOIN department d ON epi.department_id = d.dept_id AND d.company_id = %s
        LEFT JOIN `rank` rk ON epi.rank_id = rk.rank_id AND rk.company_id = %s
    """
    
    # Add context-specific filters
    if context == 'shifts':
        base_query += """
            INNER JOIN employee_shifts_schedule ess ON e.emp_id = ess.emp_id AND ess.company_id = %s
        """
    elif context == 'payslip':
        base_query += """
            INNER JOIN payroll_payslip pp ON e.emp_id = pp.emp_id AND pp.company_id = %s
        """
    
    # Add name search conditions
    base_query += """
        WHERE e.company_id = %s
        AND (CAST(AES_DECRYPT(e.last_name, %s) AS CHAR(150) CHARACTER SET utf8) LIKE %s
             OR CAST(AES_DECRYPT(e.first_name, %s) AS CHAR(150) CHARACTER SET utf8) LIKE %s)
        ORDER BY last_name ASC, first_name ASC
        LIMIT %s
    """
    
    # Build parameters array
    search_param = f"%{name_search}%"
    params = [
        ENCRYPT_KEY, ENCRYPT_KEY,  # For name decryption
        company_id, company_id, company_id,  # For joins
    ]
    
    # Add context-specific company_id parameter
    if context in ['shifts', 'payslip']:
        params.append(company_id)
    
    params.extend([
        company_id,  # For main WHERE clause
        ENCRYPT_KEY, search_param,  # For last_name search
        ENCRYPT_KEY, search_param,  # For first_name search
        limit
    ])
    
    cursor.execute(base_query, tuple(params))
    results = cursor.fetchall()
    
    # Format results into employee objects
    employees = []
    for row in results:
        employee = {
            'emp_id': row[0],
            'last_name': row[1] if row[1] else 'N/A',
            'first_name': row[2] if row[2] else 'N/A',
            'location_office': row[3] if row[3] else 'N/A',
            'department_name': row[4] if row[4] else 'N/A',
            'rank_name': row[5] if row[5] else 'N/A'
        }
        employees.append(employee)
    
    return employees

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
        
        # Ensure all filter variables are defined
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
            result = {'periods': [], 'filters': {}}

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
                # Build SQL for selected fields with AES decryption
                field_sql = ', '.join([
                    f"CAST(AES_DECRYPT({field}, %s) AS DECIMAL(10,2)) AS {field}" for field in selected_fields
                ])
                
                query = f"""
                    SELECT {field_sql}
                    FROM payroll_payslip 
                    WHERE company_id = %s
                    AND period_from = %s AND period_to = %s
                """
                
                # Build parameters array - include ENCRYPT_KEY for each field
                params = [ENCRYPT_KEY] * len(selected_fields)  # One ENCRYPT_KEY per field
                params.extend([company_id, period_start, period_end])
                
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
                
                # Process each row for this period - data is already decrypted
                for row in rows:
                    for i, field in enumerate(selected_fields):
                        if row[i] is not None:
                            period_sums[field] += float(row[i])
                
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
            
            # Get display names for all filters
            filter_display = {}
            filter_map = [
                (location_id, 'location_and_offices', 'location_and_offices_id', 'name', 'location_name'),
                (department_id, 'department', 'dept_id', 'department_name', 'department_name'),
                (rank_id, 'rank', 'rank_id', 'rank_name', 'rank_name'),
                (employment_type_id, 'employment_type', 'emp_type_id', 'name', 'employment_type_name'),
                (position_id, 'position', 'position_id', 'position_name', 'position_name'),
                (cost_center_id, 'cost_center', 'cost_center_id', 'cost_center_code', 'cost_center_code'),
                (project_id, 'project', 'project_id', 'project_name', 'project_name'),
            ]
            for id_value, table, id_field, name_field, resp_field in filter_map:
                if id_value:
                    display = get_display_name(cursor, table, id_field, name_field, id_value, company_id)
                    filter_display[resp_field] = display
            
            result['filters'] = filter_display
            
            cursor.close()
            return jsonify(result)
            
        # For single/aggregate view
        # Build SQL for selected fields with AES decryption
        field_sql = ', '.join([
            f"CAST(AES_DECRYPT({field}, %s) AS DECIMAL(10,2)) AS {field}" for field in selected_fields
        ])
        
        query = f"""
            SELECT {field_sql}, period_from, period_to
            FROM payroll_payslip 
            WHERE company_id = %s
        """
        
        # Handle date filtering based on aggregation type
        if aggregation_type == 'single':
            date_filter = " AND period_from = %s AND period_to = %s"
        else:  # 'aggregate'
            date_filter = " AND period_from >= %s AND period_to <= %s"
        query += date_filter
        
        # Build parameters array - include ENCRYPT_KEY for each field
        params = [ENCRYPT_KEY] * len(selected_fields)  # One ENCRYPT_KEY per field
        params.extend([company_id, period_from, period_to])
        
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
            
        # Process each row - data is already decrypted
        for row in rows:
            # Skip the last 2 columns (period_from, period_to) when processing fields
            for i, field in enumerate(selected_fields):
                if row[i] is not None:
                    sums[field] += float(row[i])
        
        # Create result object with field sums
        result = {}
        for field, value in sums.items():
            # Map DB field names to API field names if needed
            api_field = field
            result[api_field] = round(value, 2)
        
        # Add total_salary (gross_pay) if it exists
        if 'gross_pay' in sums:
            result['total_salary'] = round(sums['gross_pay'], 2)
        
        # Get display names for all filters
        filter_display = {}
        filter_map = [
            (location_id, 'location_and_offices', 'location_and_offices_id', 'name', 'location_name'),
            (department_id, 'department', 'dept_id', 'department_name', 'department_name'),
            (rank_id, 'rank', 'rank_id', 'rank_name', 'rank_name'),
            (employment_type_id, 'employment_type', 'emp_type_id', 'name', 'employment_type_name'),
            (position_id, 'position', 'position_id', 'position_name', 'position_name'),
            (cost_center_id, 'cost_center', 'cost_center_id', 'cost_center_code', 'cost_center_code'),
            (project_id, 'project', 'project_id', 'project_name', 'project_name'),
        ]
        for id_value, table, id_field, name_field, resp_field in filter_map:
            if id_value:
                display = get_display_name(cursor, table, id_field, name_field, id_value, company_id)
                filter_display[resp_field] = display
        
        result['filters'] = filter_display
        
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
    """
    Legacy endpoint for emp_id search - kept for backwards compatibility
    TODO: Remove after confirming all modules use new name-based search
    """
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

@app.route('/api/search-employees-by-name/<int:company_id>/<string:name_search>', methods=['GET'])
def search_employees_by_name_endpoint(company_id, name_search):
    """
    Unified endpoint for searching employees by first name or last name.
    Used by both shifts and payslip modules for consistent employee search.
    """
    try:
        # Validate parameters
        if not all([company_id, name_search]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        if len(name_search) < 2:
            return jsonify({'employees': []})
            
        # Get context from query parameter (shifts, payslip, or all)
        context = request.args.get('context', 'all')
        limit = int(request.args.get('limit', 10))
        
        cursor = mysql.connection.cursor()
        
        # Use our reusable function
        employees = search_employees_by_name(cursor, company_id, name_search, context, limit)
        
        cursor.close()
        
        return jsonify({
            'employees': employees,
            'search_term': name_search,
            'company_id': company_id,
            'context': context,
            'total_results': len(employees)
        })
        
    except Exception as e:
        app.logger.error(f"Error in search-employees-by-name: {str(e)}")
        return jsonify({'error': f'Failed to search employees: {str(e)}'}), 500

@app.route('/api/shifts-changes-by-period/<int:company_id>/<string:date_from>/<string:date_to>', methods=['GET'])
def get_shifts_changes_by_period(company_id, date_from, date_to):
    """
    Detect all employees who had shift changes during a specific period (max 7 days).
    Uses efficient O(n) iteration to process shift data in memory.
    """
    try:
        # Validate parameters
        if not all([company_id, date_from, date_to]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Validate dates
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d')
            end_date = datetime.strptime(date_to, '%Y-%m-%d')
        except ValueError as e:
            return jsonify({'error': f'Invalid date format: {str(e)}'}), 400
            
        # Validate date range (max 7 days)
        diff_days = (end_date - start_date).days
        if diff_days > 7:
            return jsonify({'error': 'Date range cannot exceed 7 days'}), 400
        if diff_days < 0:
            return jsonify({'error': 'End date must be after start date'}), 400
            
        cursor = mysql.connection.cursor()
        
        # Single query to get all shift assignments during the period
        # Include employee names with AES decryption and joins
        query = '''
            SELECT 
                ess.emp_id,
                CAST(AES_DECRYPT(e.last_name, %s) AS CHAR(150) CHARACTER SET utf8) AS last_name,
                CAST(AES_DECRYPT(e.first_name, %s) AS CHAR(150) CHARACTER SET utf8) AS first_name,
                ws.work_schedule_id,
                ws.name AS shift_name,
                ws.work_type_name AS shift_type,
                ess.valid_from,
                ess.until,
                ess.status
            FROM employee_shifts_schedule ess
            JOIN employee e ON ess.emp_id = e.emp_id
            JOIN work_schedule ws ON ess.work_schedule_id = ws.work_schedule_id
            WHERE ess.company_id = %s 
                AND ws.comp_id = %s
                AND ess.status = 'Active'
                AND (
                    (ess.valid_from >= %s AND ess.valid_from <= %s) OR
                    (ess.until >= %s AND ess.until <= %s) OR
                    (ess.valid_from <= %s AND ess.until >= %s)
                )
            ORDER BY ess.emp_id ASC, ess.valid_from ASC
        '''
        
        params = [
            ENCRYPT_KEY, ENCRYPT_KEY,  # For name decryption
            company_id, company_id,    # For main filters
            date_from, date_to,        # For valid_from range
            date_from, date_to,        # For until range  
            date_from, date_to         # For overlapping assignments
        ]
        
        cursor.execute(query, tuple(params))
        shifts = cursor.fetchall()
        cursor.close()
        
        if not shifts:
            return jsonify({
                'employees_with_changes': [],
                'period': {'from': date_from, 'to': date_to},
                'company_id': company_id,
                'total_employees': 0,
                'total_changes': 0
            })
        
        # Efficient O(n) change detection
        changes = []
        last_shift_by_employee = {}
        
        for shift in shifts:
            emp_id = shift[0]
            last_name = shift[1] if shift[1] else 'N/A'
            first_name = shift[2] if shift[2] else 'N/A'
            work_schedule_id = shift[3]
            shift_name = shift[4] if shift[4] else 'Unknown'
            shift_type = shift[5] if shift[5] else 'N/A'
            valid_from = shift[6]
            until = shift[7]
            status = shift[8]
            
            # Check if this employee had a previous shift
            if emp_id in last_shift_by_employee:
                last_shift = last_shift_by_employee[emp_id]
                
                # Detect change if shift type or shift name changed
                if (last_shift['shift_type'] != shift_type or 
                    last_shift['shift_name'] != shift_name):
                    
                    changes.append({
                        'emp_id': emp_id,
                        'last_name': last_name,
                        'first_name': first_name,
                        'change_date': valid_from.strftime('%Y-%m-%d') if valid_from else None,
                        'from_shift_name': last_shift['shift_name'],
                        'from_shift_type': last_shift['shift_type'],
                        'to_shift_name': shift_name,
                        'to_shift_type': shift_type
                    })
            
            # Update tracking for this employee
            last_shift_by_employee[emp_id] = {
                'shift_name': shift_name,
                'shift_type': shift_type,
                'valid_from': valid_from,
                'last_name': last_name,
                'first_name': first_name
            }
        
        # Remove duplicates (same employee, same change)
        unique_changes = []
        seen_changes = set()
        
        for change in changes:
            change_key = (change['emp_id'], change['change_date'], 
                         change['from_shift_type'], change['to_shift_type'])
            if change_key not in seen_changes:
                unique_changes.append(change)
                seen_changes.add(change_key)
        
        # Sort by last name, then first name
        unique_changes.sort(key=lambda x: (x['last_name'], x['first_name']))
        
        return jsonify({
            'employees_with_changes': unique_changes,
            'period': {'from': date_from, 'to': date_to},
            'company_id': company_id,
            'total_employees': len(set(change['emp_id'] for change in unique_changes)),
            'total_changes': len(unique_changes)
        })
        
    except Exception as e:
        app.logger.error(f"Error in shifts-changes-by-period: {str(e)}")
        return jsonify({'error': f'Failed to analyze shift changes: {str(e)}'}), 500

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
        rank_id = request.args.get('rank_id', None)
        employment_type_id = request.args.get('employment_type_id', None)
        position_id = request.args.get('position_id', None)
        cost_center_id = request.args.get('cost_center_id', None)
        project_id = request.args.get('project_id', None)
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
            result = {'periods': [], 'filters': {}}
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
            # Get display names for all filters
            filter_display = {}
            filter_map = [
                (location_id, 'location_and_offices', 'location_and_offices_id', 'name', 'location_name'),
                (department_id, 'department', 'dept_id', 'department_name', 'department_name'),
                (rank_id, 'rank', 'rank_id', 'rank_name', 'rank_name'),
                (employment_type_id, 'employment_type', 'emp_type_id', 'name', 'employment_type_name'),
                (position_id, 'position', 'position_id', 'position_name', 'position_name'),
                (cost_center_id, 'cost_center', 'cost_center_id', 'cost_center_code', 'cost_center_code'),
                (project_id, 'project', 'project_id', 'project_name', 'project_name'),
            ]
            for id_value, table, id_field, name_field, resp_field in filter_map:
                if id_value:
                    display = get_display_name(cursor, table, id_field, name_field, id_value, company_id)
                    filter_display[resp_field] = display
            result['filters'] = filter_display
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
                # Get display names for all filters
                filter_display = {}
                filter_map = [
                    (location_id, 'location_and_offices', 'location_and_offices_id', 'name', 'location_name'),
                    (department_id, 'department', 'dept_id', 'department_name', 'department_name'),
                    (rank_id, 'rank', 'rank_id', 'rank_name', 'rank_name'),
                    (employment_type_id, 'employment_type', 'emp_type_id', 'name', 'employment_type_name'),
                    (position_id, 'position', 'position_id', 'position_name', 'position_name'),
                    (cost_center_id, 'cost_center', 'cost_center_id', 'cost_center_code', 'cost_center_code'),
                    (project_id, 'project', 'project_id', 'project_name', 'project_name'),
                ]
                for id_value, table, id_field, name_field, resp_field in filter_map:
                    if id_value:
                        display = get_display_name(cursor, table, id_field, name_field, id_value, company_id)
                        filter_display[resp_field] = display
                result = {k: round(v, 2) for k, v in summary.items()}
                result['filters'] = filter_display
                return jsonify(result)
    except Exception as e:
        app.logger.error(f"Error in analytics-prefetch: {str(e)}")
        return jsonify({'error': f'Failed to retrieve analytics-prefetch data: {str(e)}'}), 500

@app.route('/api/shifts/schedule-type-counts/<int:company_id>', methods=['GET'])
def get_schedule_type_counts(company_id):
    try:
        cursor = mysql.connection.cursor()
        # Query for active work schedules by type
        query = '''
            SELECT work_type_name, COUNT(*) as count
            FROM work_schedule
            WHERE comp_id = %s AND status = 'Active'
            GROUP BY work_type_name
            ORDER BY count ASC, work_type_name ASC
        '''
        cursor.execute(query, (company_id,))
        results = cursor.fetchall()
        cursor.close()
        # Format as list of dicts
        data = [
            {"work_type_name": row[0], "count": row[1]} for row in results
        ]
        return jsonify({"schedule_types": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/shifts/schedules/<int:company_id>/<string:schedule_type>', methods=['GET'])
def get_schedules_by_type(company_id, schedule_type):
    try:
        cursor = mysql.connection.cursor()
        # Query for all active schedules of the given type, with employee count
        query = '''
            SELECT ws.work_schedule_id, ws.name, COUNT(DISTINCT ess.emp_id) as employee_count
            FROM work_schedule ws
            LEFT JOIN employee_shifts_schedule ess
                ON ws.work_schedule_id = ess.work_schedule_id
                AND ess.status = 'Active'
                AND ess.company_id = %s
            WHERE ws.comp_id = %s AND ws.status = 'Active' AND ws.work_type_name = %s
            GROUP BY ws.work_schedule_id, ws.name
            ORDER BY employee_count DESC, ws.name ASC
        '''
        cursor.execute(query, (company_id, company_id, schedule_type))
        results = cursor.fetchall()
        cursor.close()
        data = [
            {"work_schedule_id": row[0], "name": row[1], "employee_count": row[2]} for row in results
        ]
        return jsonify({"schedules": data})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/shifts/allocation-drilldown/<int:company_id>/<string:schedule_type>/<int:shift_id>', methods=['GET'])
def get_shifts_allocation_drilldown(company_id, schedule_type, shift_id):
    try:
        ENCRYPT_KEY = os.getenv('MYSQL_ENCRYPT_KEY')
        cursor = mysql.connection.cursor()
        
        # Query to get all unique employees assigned to the specific shift
        # Join with employee and location_and_offices to get all required fields
        query = '''
            SELECT DISTINCT
                ess.emp_id,
                CAST(AES_DECRYPT(e.last_name, %s) AS CHAR(150) CHARACTER SET utf8) AS last_name,
                CAST(AES_DECRYPT(e.first_name, %s) AS CHAR(150) CHARACTER SET utf8) AS first_name,
                COALESCE(lao.name, 'N/A') AS location_office
            FROM employee_shifts_schedule ess
            JOIN employee e ON ess.emp_id = e.emp_id
            LEFT JOIN employee_payroll_information epi ON ess.emp_id = epi.emp_id AND epi.company_id = %s
            LEFT JOIN location_and_offices lao ON epi.location_and_offices_id = lao.location_and_offices_id
            WHERE ess.company_id = %s 
                AND ess.work_schedule_id = %s 
                AND ess.status = 'Active'
            ORDER BY last_name ASC, first_name ASC
        '''
        
        cursor.execute(query, (ENCRYPT_KEY, ENCRYPT_KEY, company_id, company_id, shift_id))
        results = cursor.fetchall()
        
        # Get shift name for context
        shift_query = '''
            SELECT name FROM work_schedule 
            WHERE work_schedule_id = %s AND comp_id = %s AND status = 'Active'
        '''
        cursor.execute(shift_query, (shift_id, company_id))
        shift_result = cursor.fetchone()
        shift_name = shift_result[0] if shift_result else 'Unknown Shift'
        
        cursor.close()
        
        # Format the response
        employees = []
        for row in results:
            employees.append({
                'emp_id': row[0],
                'last_name': row[1] if row[1] else 'N/A',
                'first_name': row[2] if row[2] else 'N/A',
                'location_office': row[3] if row[3] else 'N/A'
            })
        
        return jsonify({
            'shift_id': shift_id,
            'shift_name': shift_name,
            'schedule_type': schedule_type,
            'company_id': company_id,
            'employees': employees,
            'employee_count': len(employees)
        })
        
    except Exception as e:
        app.logger.error(f"Error in shifts allocation drilldown: {str(e)}")
        return jsonify({'error': f'Failed to retrieve shifts allocation drilldown data: {str(e)}'}), 500

@app.route('/api/shifts/by-start-time/<int:company_id>/<string:start_time>', methods=['GET'])
def get_shifts_by_start_time(company_id, start_time):
    """
    Get all active shifts that start at a specific time with configuration flags and employee counts.
    Follows unified endpoint pattern with single fetch and in-memory processing.
    """
    try:
        # Validate parameters
        if not all([company_id, start_time]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Normalize start_time format (accept "0800", "08:00", "8:00" etc.)
        try:
            # Remove any non-digit characters except colons
            clean_time = ''.join(c for c in start_time if c.isdigit() or c == ':')
            
            if ':' in clean_time:
                # Format like "08:00" or "8:00"
                time_parts = clean_time.split(':')
                if len(time_parts) >= 2:
                    hour = int(time_parts[0])
                    minute = int(time_parts[1])
                else:
                    return jsonify({'error': 'Invalid time format'}), 400
            else:
                # Format like "0800" or "800"
                if len(clean_time) == 3:
                    # "800" -> 8:00
                    hour = int(clean_time[0])
                    minute = int(clean_time[1:3])
                elif len(clean_time) == 4:
                    # "0800" -> 08:00
                    hour = int(clean_time[0:2])
                    minute = int(clean_time[2:4])
                else:
                    return jsonify({'error': 'Invalid time format'}), 400
            
            # Validate time range
            if hour < 0 or hour > 23 or minute < 0 or minute > 59:
                return jsonify({'error': 'Time must be between 00:00 and 23:59'}), 400
                
            # Format as MySQL TIME
            formatted_time = f"{hour:02d}:{minute:02d}:00"
            
        except (ValueError, IndexError) as e:
            return jsonify({'error': f'Invalid time format: {str(e)}'}), 400
            
        cursor = mysql.connection.cursor()
        
        # Single query to get all shifts starting at the specified time
        # Include configuration flags, values, and employee counts following in-memory compute principle
        query = '''
            SELECT DISTINCT
                ws.work_schedule_id,
                ws.name AS shift_name,
                ws.work_type_name AS shift_type,
                rs.work_start_time,
                rs.work_end_time,
                rs.total_work_hours,
                
                -- Configuration flags for filtering (break time management only)
                ws.enable_lunch_break,
                ws.enable_additional_breaks,
                ws.enable_shift_threshold,
                ws.enable_grace_period,
                ws.enable_advance_break_rules,
                
                -- Configuration values for display
                ws.assumed_breaks,
                ws.additional_break_started_after_1,
                rs.latest_time_in_allowed,
                ws.break_started_after,
                
                COUNT(DISTINCT ess.emp_id) as employee_count
                
            FROM work_schedule ws
            JOIN regular_schedule rs ON ws.work_schedule_id = rs.work_schedule_id
            LEFT JOIN employee_shifts_schedule ess ON ws.work_schedule_id = ess.work_schedule_id 
                AND ess.status = 'Active' 
                AND ess.company_id = %s
                
            WHERE ws.comp_id = %s 
                AND ws.status = 'Active'
                AND rs.company_id = %s
                AND rs.work_start_time = %s
                
            GROUP BY ws.work_schedule_id, ws.name, ws.work_type_name, 
                     rs.work_start_time, rs.work_end_time, rs.total_work_hours,
                     ws.enable_lunch_break, ws.enable_additional_breaks, ws.enable_shift_threshold,
                     ws.enable_grace_period, ws.enable_advance_break_rules,
                     ws.assumed_breaks, ws.additional_break_started_after_1, rs.latest_time_in_allowed,
                     ws.break_started_after
                     
            ORDER BY employee_count DESC, ws.name ASC
        '''
        
        cursor.execute(query, (company_id, company_id, company_id, formatted_time))
        results = cursor.fetchall()
        cursor.close()
        
        if not results:
            return jsonify({
                'shifts': [],
                'start_time': formatted_time,
                'start_time_input': start_time,
                'company_id': company_id,
                'total_shifts': 0,
                'total_employees': 0
            })
        
        # Get configuration filters from query parameters
        config_filters = {}
        supported_configs = [
            'enable_lunch_break', 'enable_additional_breaks', 'enable_shift_threshold',
            'enable_grace_period', 'enable_advance_break_rules'
        ]
        
        for config in supported_configs:
            if request.args.get(config) == 'true':
                config_filters[config] = True
        
        # Process results following in-memory compute principle
        shifts = []
        total_employees = 0
        
        for row in results:
            # Extract configuration flags (break time management only)
            config_flags = {
                'enable_lunch_break': row[6] == 'yes' if row[6] else False,
                'enable_additional_breaks': row[7] == 'yes' if row[7] else False,
                'enable_shift_threshold': row[8] == 'yes' if row[8] else False,
                'enable_grace_period': row[9] == 'yes' if row[9] else False,
                'enable_advance_break_rules': row[10] == 'yes' if row[10] else False
            }
            
            # Extract configuration values for display
            config_values = {
                'lunch_break_duration': row[11] if row[11] else None,  # assumed_breaks
                'additional_break_duration': row[12] if row[12] else None,  # additional_break_started_after_1
                'shift_threshold_mins': row[13] if row[13] else None,  # latest_time_in_allowed from regular_schedule
                'grace_period_mins': row[14] if row[14] else None,  # break_started_after
                'advance_break_rules': None  # No specific value, just enabled/disabled
            }
            
            # Apply configuration filters if any are specified
            if config_filters:
                # Check if this shift matches ANY of the specified config filters (OR logic)
                matches_filters = False
                for filter_key, filter_value in config_filters.items():
                    if config_flags.get(filter_key) == filter_value:
                        matches_filters = True
                        break
                
                # Skip this shift if it doesn't match any of the filters
                if not matches_filters:
                    continue
            
            shift_data = {
                'work_schedule_id': row[0],
                'shift_name': row[1] if row[1] else 'Unknown Shift',
                'shift_type': row[2] if row[2] else 'N/A',
                'work_start_time': str(row[3]) if row[3] else None,
                'work_end_time': str(row[4]) if row[4] else None,
                'total_work_hours': float(row[5]) if row[5] else 0.0,
                'employee_count': row[15] if row[15] else 0,  # Updated index for employee count
                'config_flags': config_flags,
                'config_values': config_values
            }
            
            shifts.append(shift_data)
            total_employees += shift_data['employee_count']
        
        # Add applied filters information to response
        response_data = {
            'shifts': shifts,
            'start_time': formatted_time,
            'start_time_input': start_time,
            'company_id': company_id,
            'total_shifts': len(shifts),
            'total_employees': total_employees,
            'applied_filters': config_filters if config_filters else None
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        app.logger.error(f"Error in shifts by start time: {str(e)}")
        return jsonify({'error': f'Failed to retrieve shifts by start time: {str(e)}'}), 500

@app.route('/api/employee-shifts/<int:company_id>/<string:name_search>', methods=['GET'])
def get_employee_shifts(company_id, name_search):
    """
    Get shift assignment history for employees by first name or last name search.
    Follows unified endpoint pattern with single fetch and in-memory processing.
    """
    try:
        # Validate parameters
        if not all([company_id, name_search]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        # Optional query parameters for filtering
        date_from = request.args.get('date_from', None)
        date_to = request.args.get('date_to', None)
        status_filter = request.args.get('status', 'Active')  # Default to Active only
        drilldown = request.args.get('drilldown', 'false').lower() == 'true'
        
        cursor = mysql.connection.cursor()
        
        # Main query: Get all employee shift assignments with proper decryption
        # Following pattern from existing shift allocation drilldown
        query = '''
            SELECT DISTINCT
                ess.emp_id,
                CAST(AES_DECRYPT(e.last_name, %s) AS CHAR(150) CHARACTER SET utf8) AS last_name,
                CAST(AES_DECRYPT(e.first_name, %s) AS CHAR(150) CHARACTER SET utf8) AS first_name,
                ws.work_schedule_id,
                ws.name AS shift_name,
                ws.work_type_name AS shift_type,
                ess.valid_from,
                ess.until,
                ess.status,
                COALESCE(lao.name, 'N/A') AS location_office,
                COALESCE(d.department_name, 'N/A') AS department_name,
                COALESCE(rk.rank_name, 'N/A') AS rank_name
            FROM employee_shifts_schedule ess
            JOIN employee e ON ess.emp_id = e.emp_id
            JOIN work_schedule ws ON ess.work_schedule_id = ws.work_schedule_id
            LEFT JOIN employee_payroll_information epi ON ess.emp_id = epi.emp_id AND epi.company_id = %s
            LEFT JOIN location_and_offices lao ON epi.location_and_offices_id = lao.location_and_offices_id
            LEFT JOIN department d ON epi.department_id = d.dept_id AND d.company_id = %s
            LEFT JOIN `rank` rk ON epi.rank_id = rk.rank_id AND rk.company_id = %s
            WHERE ess.company_id = %s 
                AND ws.comp_id = %s
                AND (CAST(AES_DECRYPT(e.last_name, %s) AS CHAR(150) CHARACTER SET utf8) LIKE %s
                     OR CAST(AES_DECRYPT(e.first_name, %s) AS CHAR(150) CHARACTER SET utf8) LIKE %s)
        '''
        
        # Build parameters array
        search_param = f"%{name_search}%"
        params = [
            ENCRYPT_KEY, ENCRYPT_KEY,  # For name decryption
            company_id, company_id, company_id,  # For joins
            company_id, company_id,  # For main filters
            ENCRYPT_KEY, search_param,  # For last_name search
            ENCRYPT_KEY, search_param   # For first_name search
        ]
        
        # Add optional filters
        if status_filter and status_filter != 'all':
            query += " AND ess.status = %s"
            params.append(status_filter)
            
        if date_from:
            query += " AND ess.valid_from >= %s"
            params.append(date_from)
            
        if date_to:
            query += " AND ess.until <= %s"
            params.append(date_to)
        
        # Order by employee name and date range
        query += " ORDER BY last_name ASC, first_name ASC, ess.valid_from DESC"
        
        cursor.execute(query, tuple(params))
        results = cursor.fetchall()
        cursor.close()
        
        if not results:
            return jsonify({
                'employees': [],
                'search_term': name_search,
                'company_id': company_id,
                'total_employees': 0,
                'total_assignments': 0
            })
        
        # Process results following in-memory compute principle
        employees_data = []
        employee_summary = {}
        
        for row in results:
            emp_id = row[0]
            employee_record = {
                'emp_id': emp_id,
                'last_name': row[1] if row[1] else 'N/A',
                'first_name': row[2] if row[2] else 'N/A',
                'work_schedule_id': row[3],
                'shift_name': row[4] if row[4] else 'Unknown Shift',
                'shift_type': row[5] if row[5] else 'N/A',
                'valid_from': row[6].strftime('%Y-%m-%d') if row[6] else None,
                'until': row[7].strftime('%Y-%m-%d') if row[7] else None,
                'status': row[8] if row[8] else 'N/A',
                'location_office': row[9] if row[9] else 'N/A',
                'department_name': row[10] if row[10] else 'N/A',
                'rank_name': row[11] if row[11] else 'N/A'
            }
            
            employees_data.append(employee_record)
            
            # Build employee summary for aggregated view
            if emp_id not in employee_summary:
                employee_summary[emp_id] = {
                    'emp_id': emp_id,
                    'last_name': employee_record['last_name'],
                    'first_name': employee_record['first_name'],
                    'location_office': employee_record['location_office'],
                    'department_name': employee_record['department_name'],
                    'rank_name': employee_record['rank_name'],
                    'shift_assignments': [],
                    'total_assignments': 0,
                    'active_assignments': 0,
                    'current_shifts': []
                }
            
            # Add to summary
            employee_summary[emp_id]['shift_assignments'].append({
                'shift_name': employee_record['shift_name'],
                'shift_type': employee_record['shift_type'],
                'valid_from': employee_record['valid_from'],
                'until': employee_record['until'],
                'status': employee_record['status']
            })
            employee_summary[emp_id]['total_assignments'] += 1
            
            if employee_record['status'] == 'Active':
                employee_summary[emp_id]['active_assignments'] += 1
                employee_summary[emp_id]['current_shifts'].append(employee_record['shift_name'])
        
        # Format response following established patterns
        if drilldown:
            # Return detailed per-assignment view
            return jsonify({
                'shift_assignments': employees_data,
                'search_term': name_search,
                'company_id': company_id,
                'total_assignments': len(employees_data),
                'filters': {
                    'status': status_filter,
                    'date_from': date_from,
                    'date_to': date_to
                }
            })
        else:
            # Return employee summary view
            employees_list = list(employee_summary.values())
            return jsonify({
                'employees': employees_list,
                'search_term': name_search,
                'company_id': company_id,
                'total_employees': len(employees_list),
                'total_assignments': len(employees_data),
                'filters': {
                    'status': status_filter,
                    'date_from': date_from,
                    'date_to': date_to
                }
            })
            
    except Exception as e:
        app.logger.error(f"Error in employee-shifts: {str(e)}")
        return jsonify({'error': f'Failed to retrieve employee shifts data: {str(e)}'}), 500

@app.route('/api/shift-details/<int:company_id>/<int:shift_id>', methods=['GET'])
def get_shift_details(company_id, shift_id):
    """
    Get comprehensive configuration details for a specific shift.
    Returns ALL fields from ALL shift-related tables exactly as shown in the comprehensive UI.
    """
    try:
        # Validate parameters
        if not all([company_id, shift_id]):
            return jsonify({'error': 'Missing required parameters'}), 400
            
        cursor = mysql.connection.cursor()
        
        # Comprehensive query to get ALL existing work_schedule fields
        work_schedule_query = '''
            SELECT 
                work_schedule_id, name, work_type_name, comp_id, flag_custom, status, `default`,
                category_id, employees_required, notes, bg_color, break_rules, assumed_breaks,
                advanced_settings, account_id, enable_lunch_break, break_type_1, track_break_1,
                break_schedule_1, break_started_after, enable_additional_breaks,
                num_of_additional_breaks, break_type_2, track_break_2, break_schedule_2,
                additional_break_started_after_1, additional_break_started_after_2,
                enable_shift_threshold, enable_grace_period, tardiness_rule, disable_premium_payments,
                enable_premium_payments_starts_on_holiday_restday, flag_migrate, enable_breaks_on_holiday,
                enable_working_on_restday, total_hrs_per_pay_period, total_hrs_per_day, period_type,
                advanced_rules_premium_pay, pay_holiday_premium_on_regular_workday,
                pay_holiday_premium_on_regular_workday_nsd, pay_holiday_premium_on_holiday,
                pay_holiday_premium_on_holiday_nsd, pay_restday_premium_on_regular_workday,
                pay_restday_premium_on_regular_workday_nsd, pay_holiday_premium_on_restday,
                pay_holiday_premium_on_restday_nsd, total_hrs_per_week, created_date, updated_date,
                created_by_account_id, updated_by_account_id, flag_default_restday,
                pay_ot_holiday_rates_workday_holiday, pay_ot_holiday_rates_holiday_workday,
                pay_ot_rest_day_rates_workday_restday, pay_ot_rest_day_rates_restday_workday,
                paycheck_total_hrs_per_pay_period, enable_advance_break_rules, archive, archived_date
            FROM work_schedule 
            WHERE work_schedule_id = %s AND comp_id = %s AND status = 'Active'
            LIMIT 1
        '''
        
        cursor.execute(work_schedule_query, (shift_id, company_id))
        ws_result = cursor.fetchone()
        
        if not ws_result:
            cursor.close()
            return jsonify({'error': 'Shift not found or inactive'}), 404
        
        # Map ALL work_schedule fields
        work_schedule_data = {
            'WORK_SCHEDULE_ID': ws_result[0],
            'NAME': ws_result[1] if ws_result[1] else 'N/A',
            'WORK_TYPE_NAME': ws_result[2] if ws_result[2] else 'N/A',
            'COMP_ID': ws_result[3] if ws_result[3] else 'N/A',
            'FLAG_CUSTOM': ws_result[4] if ws_result[4] else 'N/A',
            'STATUS': ws_result[5] if ws_result[5] else 'N/A',
            'DEFAULT': ws_result[6] if ws_result[6] else 'N/A',
            'CATEGORY_ID': ws_result[7] if ws_result[7] else 'N/A',
            'EMPLOYEES_REQUIRED': ws_result[8] if ws_result[8] else 'N/A',
            'NOTES': ws_result[9] if ws_result[9] else 'N/A',
            'BG_COLOR': ws_result[10] if ws_result[10] else 'N/A',
            'BREAK_RULES': ws_result[11] if ws_result[11] else 'N/A',
            'ASSUMED_BREAKS': ws_result[12] if ws_result[12] else 'N/A',
            'ADVANCED_SETTINGS': ws_result[13] if ws_result[13] else 'N/A',
            'ACCOUNT_ID': ws_result[14] if ws_result[14] else 'N/A',
            'ENABLE_LUNCH_BREAK': ws_result[15] if ws_result[15] else 'N/A',
            'BREAK_TYPE_1': ws_result[16] if ws_result[16] else 'N/A',
            'TRACK_BREAK_1': ws_result[17] if ws_result[17] else 'N/A',
            'BREAK_SCHEDULE_1': ws_result[18] if ws_result[18] else 'N/A',
            'BREAK_STARTED_AFTER': ws_result[19] if ws_result[19] else 'N/A',
            'ENABLE_ADDITIONAL_BREAKS': ws_result[20] if ws_result[20] else 'N/A',
            'NUM_OF_ADDITIONAL_BREAKS': ws_result[21] if ws_result[21] else 'N/A',
            'BREAK_TYPE_2': ws_result[22] if ws_result[22] else 'N/A',
            'TRACK_BREAK_2': ws_result[23] if ws_result[23] else 'N/A',
            'BREAK_SCHEDULE_2': ws_result[24] if ws_result[24] else 'N/A',
            'ADDITIONAL_BREAK_STARTED_AFTER_1': ws_result[25] if ws_result[25] else 'N/A',
            'ADDITIONAL_BREAK_STARTED_AFTER_2': ws_result[26] if ws_result[26] else 'N/A',
            'ENABLE_SHIFT_THRESHOLD': ws_result[27] if ws_result[27] else 'N/A',
            'ENABLE_GRACE_PERIOD': ws_result[28] if ws_result[28] else 'N/A',
            'TARDINESS_RULE': ws_result[29] if ws_result[29] else 'N/A',
            'DISABLE_PREMIUM_PAYMENTS': ws_result[30] if ws_result[30] else 'N/A',
            'ENABLE_PREMIUM_PAYMENTS_STARTS_ON_HOLIDAY_RESTDAY': ws_result[31] if ws_result[31] else 'N/A',
            'FLAG_MIGRATE': ws_result[32] if ws_result[32] else 'N/A',
            'ENABLE_BREAKS_ON_HOLIDAY': ws_result[33] if ws_result[33] else 'N/A',
            'ENABLE_WORKING_ON_RESTDAY': ws_result[34] if ws_result[34] else 'N/A',
            'TOTAL_HRS_PER_PAY_PERIOD': ws_result[35] if ws_result[35] else 'N/A',
            'TOTAL_HRS_PER_DAY': ws_result[36] if ws_result[36] else 'N/A',
            'PERIOD_TYPE': ws_result[37] if ws_result[37] else 'N/A',
            'ADVANCED_RULES_PREMIUM_PAY': ws_result[38] if ws_result[38] else 'N/A',
            'PAY_HOLIDAY_PREMIUM_ON_REGULAR_WORKDAY': ws_result[39] if ws_result[39] else 'N/A',
            'PAY_HOLIDAY_PREMIUM_ON_REGULAR_WORKDAY_NSD': ws_result[40] if ws_result[40] else 'N/A',
            'PAY_HOLIDAY_PREMIUM_ON_HOLIDAY': ws_result[41] if ws_result[41] else 'N/A',
            'PAY_HOLIDAY_PREMIUM_ON_HOLIDAY_NSD': ws_result[42] if ws_result[42] else 'N/A',
            'PAY_RESTDAY_PREMIUM_ON_REGULAR_WORKDAY': ws_result[43] if ws_result[43] else 'N/A',
            'PAY_RESTDAY_PREMIUM_ON_REGULAR_WORKDAY_NSD': ws_result[44] if ws_result[44] else 'N/A',
            'PAY_HOLIDAY_PREMIUM_ON_RESTDAY': ws_result[45] if ws_result[45] else 'N/A',
            'PAY_HOLIDAY_PREMIUM_ON_RESTDAY_NSD': ws_result[46] if ws_result[46] else 'N/A',
            'TOTAL_HRS_PER_WEEK': ws_result[47] if ws_result[47] else 'N/A',
            'CREATED_DATE': ws_result[48].strftime('%Y-%m-%d %H:%M:%S') if ws_result[48] else 'N/A',
            'UPDATED_DATE': ws_result[49].strftime('%Y-%m-%d %H:%M:%S') if ws_result[49] else 'N/A',
            'CREATED_BY_ACCOUNT_ID': ws_result[50] if ws_result[50] else 'N/A',
            'UPDATED_BY_ACCOUNT_ID': ws_result[51] if ws_result[51] else 'N/A',
            'FLAG_DEFAULT_RESTDAY': ws_result[52] if ws_result[52] else 'N/A',
            'PAY_OT_HOLIDAY_RATES_WORKDAY_HOLIDAY': ws_result[53] if ws_result[53] else 'N/A',
            'PAY_OT_HOLIDAY_RATES_HOLIDAY_WORKDAY': ws_result[54] if ws_result[54] else 'N/A',
            'PAY_OT_REST_DAY_RATES_WORKDAY_RESTDAY': ws_result[55] if ws_result[55] else 'N/A',
            'PAY_OT_REST_DAY_RATES_RESTDAY_WORKDAY': ws_result[56] if ws_result[56] else 'N/A',
            'PAYCHECK_TOTAL_HRS_PER_PAY_PERIOD': ws_result[57] if ws_result[57] else 'N/A',
            'ENABLE_ADVANCE_BREAK_RULES': ws_result[58] if ws_result[58] else 'N/A',
            'ARCHIVE': ws_result[59] if ws_result[59] else 'N/A',
            'ARCHIVED_DATE': ws_result[60].strftime('%Y-%m-%d %H:%M:%S') if ws_result[60] else 'N/A'
        }
        
        # Get ALL regular_schedule fields
        regular_schedule_query = '''
            SELECT 
                reg_work_sched_id, work_schedule_id, work_schedule_name, days_of_work,
                work_start_time, work_end_time, total_work_hours, company_id, break_in_min,
                latest_time_in_allowed, status, break_1, break_2, flag_half_day
            FROM regular_schedule 
            WHERE work_schedule_id = %s AND company_id = %s
            LIMIT 1
        '''
        
        cursor.execute(regular_schedule_query, (shift_id, company_id))
        rs_result = cursor.fetchone()
        
        regular_schedule_data = {}
        if rs_result:
            regular_schedule_data = {
                'REG_WORK_SCHED_ID': rs_result[0] if rs_result[0] else 'N/A',
                'WORK_SCHEDULE_ID': rs_result[1] if rs_result[1] else 'N/A',
                'WORK_SCHEDULE_NAME': rs_result[2] if rs_result[2] else 'N/A',
                'DAYS_OF_WORK': rs_result[3] if rs_result[3] else 'N/A',
                'WORK_START_TIME': str(rs_result[4]) if rs_result[4] else 'N/A',
                'WORK_END_TIME': str(rs_result[5]) if rs_result[5] else 'N/A',
                'TOTAL_WORK_HOURS': float(rs_result[6]) if rs_result[6] else 'N/A',
                'COMPANY_ID': rs_result[7] if rs_result[7] else 'N/A',
                'BREAK_IN_MIN': rs_result[8] if rs_result[8] else 'N/A',
                'LATEST_TIME_IN_ALLOWED': rs_result[9] if rs_result[9] else 'N/A',
                'STATUS': rs_result[10] if rs_result[10] else 'N/A',
                'BREAK_1': float(rs_result[11]) if rs_result[11] else 'N/A',
                'BREAK_2': float(rs_result[12]) if rs_result[12] else 'N/A',
                'FLAG_HALF_DAY': rs_result[13] if rs_result[13] else 'N/A'
            }
        
        # Get ALL flexible_hours fields if they exist
        flexible_hours_query = '''
            SELECT 
                workday_settings_id, not_required_login, total_hours_for_the_day, 
                total_hours_for_the_week, total_days_per_year, latest_time_in_allowed,
                number_of_breaks_per_day, duration_of_lunch_break_per_day, 
                duration_of_short_break_per_day, work_schedule_id, company_id
            FROM flexible_hours 
            WHERE work_schedule_id = %s AND company_id = %s
            LIMIT 1
        '''
        
        cursor.execute(flexible_hours_query, (shift_id, company_id))
        fh_result = cursor.fetchone()
        
        flexible_hours_data = {}
        if fh_result:
            flexible_hours_data = {
                'WORKDAY_SETTINGS_ID': fh_result[0] if fh_result[0] else 'N/A',
                'NOT_REQUIRED_LOGIN': fh_result[1] if fh_result[1] else 'N/A',
                'TOTAL_HOURS_FOR_THE_DAY': fh_result[2] if fh_result[2] else 'N/A',
                'TOTAL_HOURS_FOR_THE_WEEK': fh_result[3] if fh_result[3] else 'N/A',
                'TOTAL_DAYS_PER_YEAR': fh_result[4] if fh_result[4] else 'N/A',
                'LATEST_TIME_IN_ALLOWED': str(fh_result[5]) if fh_result[5] else 'N/A',
                'NUMBER_OF_BREAKS_PER_DAY': fh_result[6] if fh_result[6] else 'N/A',
                'DURATION_OF_LUNCH_BREAK_PER_DAY': fh_result[7] if fh_result[7] else 'N/A',
                'DURATION_OF_SHORT_BREAK_PER_DAY': fh_result[8] if fh_result[8] else 'N/A',
                'WORK_SCHEDULE_ID': fh_result[9] if fh_result[9] else 'N/A',
                'COMPANY_ID': fh_result[10] if fh_result[10] else 'N/A'
            }
        
        # Get ALL rest_day entries
        rest_day_query = '''
            SELECT 
                rest_day_id, rest_day, company_id, work_schedule_id, status, deleted
            FROM rest_day 
            WHERE work_schedule_id = %s AND company_id = %s AND status = 'Active' AND deleted = '0'
        '''
        
        cursor.execute(rest_day_query, (shift_id, company_id))
        rd_results = cursor.fetchall()
        
        rest_days_data = []
        for rd_result in rd_results:
            rest_days_data.append({
                'REST_DAY_ID': rd_result[0] if rd_result[0] else 'N/A',
                'REST_DAY': rd_result[1] if rd_result[1] else 'N/A',
                'COMPANY_ID': rd_result[2] if rd_result[2] else 'N/A',
                'WORK_SCHEDULE_ID': rd_result[3] if rd_result[3] else 'N/A',
                'STATUS': rd_result[4] if rd_result[4] else 'N/A',
                'DELETED': rd_result[5] if rd_result[5] else 'N/A'
            })
        
        # Get employee count for summary
        count_query = '''
            SELECT COUNT(DISTINCT ess.emp_id) as employee_count
            FROM employee_shifts_schedule ess
            WHERE ess.work_schedule_id = %s 
                AND ess.status = 'Active' 
                AND ess.company_id = %s
        '''
        cursor.execute(count_query, (shift_id, company_id))
        count_result = cursor.fetchone()
        employee_count = count_result[0] if count_result else 0
        
        cursor.close()
        
        # Return comprehensive data exactly as shown in the UI
        response = {
            'shift_summary': {
                'shift_name': work_schedule_data['NAME'],
                'employee_count': employee_count
            },
            'work_schedule': work_schedule_data,
            'regular_schedule': regular_schedule_data,
            'flexible_hours': flexible_hours_data if flexible_hours_data else None,
            'rest_days': rest_days_data,
            'company_id': company_id,
            'shift_id': shift_id
        }
        
        return jsonify(response)
        
    except Exception as e:
        app.logger.error(f"Error in shift details: {str(e)}")
        return jsonify({'error': f'Failed to retrieve shift details: {str(e)}'}), 500

@app.route('/api/shift-employees/<int:company_id>/<int:shift_id>', methods=['GET'])
def get_shift_employees(company_id, shift_id):
    """
    Get all employees assigned to a specific shift with download capability.
    """
    try:
        cursor = mysql.connection.cursor()
        
        # Query to get all employees assigned to the shift
        query = '''
            SELECT DISTINCT
                ess.emp_id,
                CAST(AES_DECRYPT(e.last_name, %s) AS CHAR(150) CHARACTER SET utf8) AS last_name,
                CAST(AES_DECRYPT(e.first_name, %s) AS CHAR(150) CHARACTER SET utf8) AS first_name,
                COALESCE(lao.name, 'N/A') AS location_office,
                COALESCE(d.department_name, 'N/A') AS department_name,
                COALESCE(rk.rank_name, 'N/A') AS rank_name,
                ess.valid_from,
                ess.until,
                ess.status
            FROM employee_shifts_schedule ess
            JOIN employee e ON ess.emp_id = e.emp_id
            LEFT JOIN employee_payroll_information epi ON ess.emp_id = epi.emp_id AND epi.company_id = %s
            LEFT JOIN location_and_offices lao ON epi.location_and_offices_id = lao.location_and_offices_id
            LEFT JOIN department d ON epi.department_id = d.dept_id AND d.company_id = %s
            LEFT JOIN `rank` rk ON epi.rank_id = rk.rank_id AND rk.company_id = %s
            WHERE ess.company_id = %s 
                AND ess.work_schedule_id = %s 
                AND ess.status = 'Active'
            ORDER BY last_name ASC, first_name ASC
        '''
        
        cursor.execute(query, (ENCRYPT_KEY, ENCRYPT_KEY, company_id, company_id, company_id, company_id, shift_id))
        results = cursor.fetchall()
        cursor.close()
        
        # Format employee data
        employees = []
        for row in results:
            employees.append({
                'emp_id': row[0],
                'last_name': row[1] if row[1] else 'N/A',
                'first_name': row[2] if row[2] else 'N/A',
                'full_name': f"{row[1]}, {row[2]}" if row[1] and row[2] else 'N/A',
                'location_office': row[3] if row[3] else 'N/A',
                'department_name': row[4] if row[4] else 'N/A',
                'rank_name': row[5] if row[5] else 'N/A',
                'valid_from': row[6].strftime('%Y-%m-%d') if row[6] else 'N/A',
                'until': row[7].strftime('%Y-%m-%d') if row[7] else 'N/A',
                'status': row[8] if row[8] else 'N/A'
            })
        
        return jsonify({
            'employees': employees,
            'employee_count': len(employees),
            'company_id': company_id,
            'shift_id': shift_id
        })
        
    except Exception as e:
        app.logger.error(f"Error in shift employees: {str(e)}")
        return jsonify({'error': f'Failed to retrieve shift employees: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002) 