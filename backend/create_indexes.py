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

def index_exists(cursor, index_name):
    """Check if an index already exists"""
    cursor.execute("""
        SELECT COUNT(*) 
        FROM information_schema.statistics 
        WHERE table_schema = %s 
        AND table_name = 'payroll_payslip' 
        AND index_name = %s
    """, (os.getenv('DB_NAME'), index_name))
    return cursor.fetchone()[0] > 0

def create_indexes():
    """Create performance indexes for the payroll_payslip table"""
    try:
        with app.app_context():
            cursor = mysql.connection.cursor()
            
            # Index for main analytics queries (company + period)
            if not index_exists(cursor, 'idx_company_period'):
                print("Creating index for company and period queries...")
                cursor.execute("""
                    CREATE INDEX idx_company_period 
                    ON payroll_payslip(company_id, period_from, period_to)
                """)
                print("✅ Created idx_company_period")
            else:
                print("⏭️  Index idx_company_period already exists")
            
            # Index for employee-specific queries
            if not index_exists(cursor, 'idx_company_emp'):
                print("Creating index for employee queries...")
                cursor.execute("""
                    CREATE INDEX idx_company_emp 
                    ON payroll_payslip(company_id, emp_id)
                """)
                print("✅ Created idx_company_emp")
            else:
                print("⏭️  Index idx_company_emp already exists")
            
            # Composite index for both use cases
            if not index_exists(cursor, 'idx_company_emp_period'):
                print("Creating composite index...")
                cursor.execute("""
                    CREATE INDEX idx_company_emp_period 
                    ON payroll_payslip(company_id, emp_id, period_from, period_to)
                """)
                print("✅ Created idx_company_emp_period")
            else:
                print("⏭️  Index idx_company_emp_period already exists")
            
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