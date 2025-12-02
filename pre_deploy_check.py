"""
Pre-Deployment Checklist
Verifies that everything is ready for deployment to VPS
"""

import os
import sqlite3
import subprocess
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def check_mark(passed):
    return f"{Colors.GREEN}✅{Colors.END}" if passed else f"{Colors.RED}❌{Colors.END}"

def warning_mark():
    return f"{Colors.YELLOW}⚠️{Colors.END}"

def print_header(text):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")

def check_git_status():
    """Check Git repository status."""
    print_header("Git Repository Status")
    
    try:
        # Check if git repo exists
        result = subprocess.run(['git', 'status'], 
                              capture_output=True, 
                              text=True, 
                              cwd=os.getcwd())
        
        if result.returncode != 0:
            print(f"{check_mark(False)} Not a git repository")
            return False
        
        print(f"{check_mark(True)} Git repository found")
        
        # Check for uncommitted changes
        if "nothing to commit" in result.stdout:
            print(f"{check_mark(True)} No uncommitted changes")
        else:
            print(f"{warning_mark()} Uncommitted changes detected:")
            print(result.stdout)
        
        # Check remote
        remote_result = subprocess.run(['git', 'remote', '-v'], 
                                      capture_output=True, 
                                      text=True)
        if remote_result.returncode == 0 and remote_result.stdout:
            print(f"{check_mark(True)} Remote repository configured:")
            print(f"  {remote_result.stdout.strip()}")
        else:
            print(f"{check_mark(False)} No remote repository configured")
        
        return True
        
    except FileNotFoundError:
        print(f"{check_mark(False)} Git not found in system")
        return False

def check_env_file():
    """Check .env file exists and has required variables."""
    print_header("Environment Configuration")
    
    env_path = ".env"
    
    if not os.path.exists(env_path):
        print(f"{check_mark(False)} .env file not found")
        return False
    
    print(f"{check_mark(True)} .env file exists")
    
    # Check for required variables
    required_vars = [
        "OPENAI_API_KEY",
        "GOOGLE_SHEETS_ESTRATEGIAS_ID",
        "GOOGLE_SHEETS_NEGOCIOS_ID"
    ]
    
    with open(env_path, 'r') as f:
        env_content = f.read()
    
    missing_vars = []
    for var in required_vars:
        if var in env_content:
            print(f"{check_mark(True)} {var} found")
        else:
            print(f"{check_mark(False)} {var} missing")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n{warning_mark()} Missing environment variables: {', '.join(missing_vars)}")
        return False
    
    return True

def check_gitignore():
    """Check .gitignore is properly configured."""
    print_header("Git Ignore Configuration")
    
    gitignore_path = ".gitignore"
    
    if not os.path.exists(gitignore_path):
        print(f"{check_mark(False)} .gitignore file not found")
        return False
    
    print(f"{check_mark(True)} .gitignore file exists")
    
    # Check for critical entries
    critical_entries = [
        ".env",
        "*.db",
        "__pycache__"
    ]
    
    with open(gitignore_path, 'r') as f:
        gitignore_content = f.read()
    
    all_present = True
    for entry in critical_entries:
        if entry in gitignore_content:
            print(f"{check_mark(True)} {entry} is ignored")
        else:
            print(f"{check_mark(False)} {entry} NOT ignored - SECURITY RISK!")
            all_present = False
    
    return all_present

def check_database():
    """Check database exists and has required tables."""
    print_header("Database Status")
    
    db_path = "users.db"
    
    if not os.path.exists(db_path):
        print(f"{check_mark(False)} Database file not found")
        return False
    
    print(f"{check_mark(True)} Database file exists")
    
    # Check database size
    db_size = os.path.getsize(db_path) / 1024  # KB
    print(f"  📦 Size: {db_size:.2f} KB")
    
    # Check tables
    required_tables = [
        "users",
        "estrategias",
        "tareas_diarias",
        "progreso_semanal",
        "logros_usuario",
        "schema_migrations"
    ]
    
    try:
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        
        c.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = {row[0] for row in c.fetchall()}
        
        all_present = True
        for table in required_tables:
            if table in existing_tables:
                # Get record count
                c.execute(f"SELECT COUNT(*) FROM {table}")
                count = c.fetchone()[0]
                print(f"{check_mark(True)} {table} ({count} records)")
            else:
                print(f"{check_mark(False)} {table} missing")
                all_present = False
        
        conn.close()
        return all_present
        
    except Exception as e:
        print(f"{check_mark(False)} Error checking database: {e}")
        return False

def check_dependencies():
    """Check requirements.txt exists."""
    print_header("Dependencies")
    
    req_path = "requirements.txt"
    
    if not os.path.exists(req_path):
        print(f"{check_mark(False)} requirements.txt not found")
        return False
    
    print(f"{check_mark(True)} requirements.txt exists")
    
    with open(req_path, 'r') as f:
        deps = f.readlines()
    
    print(f"  📦 {len(deps)} dependencies listed")
    
    return True

def check_migrations():
    """Check migration system is ready."""
    print_header("Database Migrations")
    
    migration_file = "db_migrations.py"
    
    if not os.path.exists(migration_file):
        print(f"{check_mark(False)} db_migrations.py not found")
        return False
    
    print(f"{check_mark(True)} Migration system exists")
    
    # Check if migrations table exists
    db_path = "users.db"
    if os.path.exists(db_path):
        try:
            conn = sqlite3.connect(db_path)
            c = conn.cursor()
            
            c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='schema_migrations'")
            if c.fetchone():
                print(f"{check_mark(True)} Migrations tracking table exists")
                
                # List executed migrations
                c.execute("SELECT migration_name, executed_at FROM schema_migrations ORDER BY id")
                migrations = c.fetchall()
                
                if migrations:
                    print(f"\n  Executed migrations:")
                    for name, executed_at in migrations:
                        print(f"    ✓ {name} ({executed_at})")
                else:
                    print(f"{warning_mark()} No migrations executed yet")
            else:
                print(f"{warning_mark()} Migrations tracking table not initialized")
            
            conn.close()
            
        except Exception as e:
            print(f"{check_mark(False)} Error checking migrations: {e}")
            return False
    
    return True

def check_critical_files():
    """Check that critical files exist."""
    print_header("Critical Files")
    
    critical_files = [
        "main.py",
        "auth.py",
        "ai_logic.py",
        "pdf_gen.py",
        "tasks_manager.py",
        "Dockerfile",
        "db_migrations.py"
    ]
    
    all_present = True
    for file in critical_files:
        if os.path.exists(file):
            size = os.path.getsize(file) / 1024  # KB
            print(f"{check_mark(True)} {file} ({size:.2f} KB)")
        else:
            print(f"{check_mark(False)} {file} missing")
            all_present = False
    
    return all_present

def generate_deployment_summary():
    """Generate a summary for deployment."""
    print_header("Deployment Summary")
    
    summary = {
        "timestamp": datetime.now().isoformat(),
        "ready": True
    }
    
    # Run all checks
    checks = {
        "Git Status": check_git_status(),
        "Environment File": check_env_file(),
        "Git Ignore": check_gitignore(),
        "Database": check_database(),
        "Dependencies": check_dependencies(),
        "Migrations": check_migrations(),
        "Critical Files": check_critical_files()
    }
    
    summary["checks"] = checks
    
    # Print summary
    print_header("Final Summary")
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    print(f"Checks passed: {passed}/{total}\n")
    
    for check_name, result in checks.items():
        print(f"  {check_mark(result)} {check_name}")
    
    if all(checks.values()):
        print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT{Colors.END}")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
        
        print("Next steps:")
        print("  1. Review DEPLOY.md for deployment instructions")
        print("  2. Commit and push changes to GitHub")
        print("  3. Deploy to VPS following the guide")
    else:
        print(f"\n{Colors.RED}{'='*60}{Colors.END}")
        print(f"{Colors.RED}❌ SOME CHECKS FAILED - FIX ISSUES BEFORE DEPLOYING{Colors.END}")
        print(f"{Colors.RED}{'='*60}{Colors.END}\n")
        
        print("Failed checks:")
        for check_name, result in checks.items():
            if not result:
                print(f"  ❌ {check_name}")

if __name__ == "__main__":
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}{'MiPymesIA - Pre-Deployment Checklist':^60}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    generate_deployment_summary()
