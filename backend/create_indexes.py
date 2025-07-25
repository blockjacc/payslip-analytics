#!/usr/bin/env python3
"""
Script to create database indexes for performance optimization
"""
from flask import Flask
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_HOST'] = os.getenv('DB_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('DB_PORT', 3306))
app.config['MYSQL_USER'] = os.getenv('DB_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('DB_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('DB_NAME')

mysql = MySQL(app)

def index_exists(cursor, index_name, table_name):
    """Check if an index already exists on a given table"""
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.statistics 
        WHERE table_schema = %s 
        AND table_name = %s 
        AND index_name = %s
    """, (os.getenv('DB_NAME'), table_name, index_name))
    return cursor.fetchone()[0] > 0

def create_indexes():
    """Create performance indexes for the payroll_payslip and employee_payroll_information tables"""
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            
            # Index for main analytics queries (company + period)
            if not index_exists(cursor, 'idx_company_period', 'payroll_payslip'):
                print("Creating index for company and period queries...")
                cursor.execute("""
                    CREATE INDEX idx_company_period 
                    ON payroll_payslip(company_id, period_from, period_to)
                """)
                print("✅ Created idx_company_period")
            else:
                print("⏭️  Index idx_company_period already exists")
            
            # Index for employee-specific queries
            if not index_exists(cursor, 'idx_company_emp', 'payroll_payslip'):
                print("Creating index for employee queries...")
                cursor.execute("""
                    CREATE INDEX idx_company_emp 
                    ON payroll_payslip(company_id, emp_id)
                """)
                print("✅ Created idx_company_emp")
            else:
                print("⏭️  Index idx_company_emp already exists")
            
            # Composite index for both use cases
            if not index_exists(cursor, 'idx_company_emp_period', 'payroll_payslip'):
                print("Creating composite index...")
                cursor.execute("""
                    CREATE INDEX idx_company_emp_period 
                    ON payroll_payslip(company_id, emp_id, period_from, period_to)
                """)
                print("✅ Created idx_company_emp_period")
            else:
                print("⏭️  Index idx_company_emp_period already exists")
            
            # New indexes for employee_payroll_information
            epi_indexes = [
                ('idx_epi_company_department', 'department_id'),
                ('idx_epi_company_rank', 'rank_id'),
                ('idx_epi_company_employment_type', 'employment_type'),
                ('idx_epi_company_position', 'position'),
                ('idx_epi_company_cost_center', 'cost_center'),
                ('idx_epi_company_project', 'project_id'),
                ('idx_epi_company_location', 'location_and_offices_id'),
            ]
            for idx_name, col in epi_indexes:
                if not index_exists(cursor, idx_name, 'employee_payroll_information'):
                    print(f"Creating index {idx_name} on employee_payroll_information({col})...")
                    cursor.execute(f"""
                        CREATE INDEX {idx_name}
                        ON employee_payroll_information(company_id, {col})
                    """)
                    print(f"✅ Created {idx_name}")
                else:
                    print(f"⏭️  Index {idx_name} already exists")
            
            # New index for work_schedule (for allocation analytics)
            if not index_exists(cursor, 'idx_ws_company_type_status', 'work_schedule'):
                print("Creating index idx_ws_company_type_status on work_schedule(company_id, work_type_name, status)...")
                cursor.execute("""
                    CREATE INDEX idx_ws_company_type_status
                    ON work_schedule(comp_id, work_type_name, status)
                """)
                print("✅ Created idx_ws_company_type_status")
            else:
                print("⏭️  Index idx_ws_company_type_status already exists")

            # New index for employee_shifts_schedule (for allocation analytics)
            if not index_exists(cursor, 'idx_ess_company_sched_status', 'employee_shifts_schedule'):
                print("Creating index idx_ess_company_sched_status on employee_shifts_schedule(company_id, work_schedule_id, status)...")
                cursor.execute("""
                    CREATE INDEX idx_ess_company_sched_status
                    ON employee_shifts_schedule(company_id, work_schedule_id, status)
                """)
                print("✅ Created idx_ess_company_sched_status")
            else:
                print("⏭️  Index idx_ess_company_sched_status already exists")
            
            # Index for payroll group queries
            if not index_exists(cursor, 'idx_company_payroll_group', 'payroll_payslip'):
                print("Creating index for payroll group queries...")
                cursor.execute("""
                    CREATE INDEX idx_company_payroll_group 
                    ON payroll_payslip(company_id, payroll_group_id)
                """)
                print("✅ Created idx_company_payroll_group")
            else:
                print("⏭️  Index idx_company_payroll_group already exists")
            
            mysql.connection.commit()
            cursor.close()
            
            print("✅ All indexes created successfully!")
            
    except Exception as e:
        print(f"❌ Error creating indexes: {str(e)}")
        return False
    
    return True

if __name__ == "__main__":
    print("Creating database indexes for performance optimization...")
    success = create_indexes()
    if success:
        print("Index creation completed successfully!")
    else:
        print("Index creation failed!") 