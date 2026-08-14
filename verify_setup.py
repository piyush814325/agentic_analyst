"""
Setup verification script for Agentic SQL Data Analyst.
Checks all dependencies, configuration, and database connectivity.
Run this after setup: python verify_setup.py
"""

import sys
import os
from pathlib import Path


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}")


def print_ok(text):
    print(f"✅ {text}")


def print_error(text):
    print(f"❌ {text}")


def print_warning(text):
    print(f"⚠️  {text}")


def check_python_version():
    """Check Python version >= 3.8"""
    print_header("1. Python Version")
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print_ok(f"Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print_error(f"Python 3.8+ required. Current: {version.major}.{version.minor}")
        return False


def check_project_structure():
    """Check all required files and directories exist"""
    print_header("2. Project Structure")
    
    required_files = [
        "config.py",
        "app.py",
        "requirements.txt",
        ".env.example",
        "db/__init__.py",
        "db/connection.py",
        "db/ingestion.py",
        "db/utils.py",
        "agent/__init__.py",
        "agent/state.py",
        "agent/nodes.py",
        "agent/graph.py",
        "README.md",
        "QUICK_START.md",
        "TESTING.md",
        "PROJECT_STRUCTURE.md",
    ]
    
    all_present = True
    for file in required_files:
        if Path(file).exists():
            print_ok(file)
        else:
            print_error(file)
            all_present = False
    
    return all_present


def check_env_file():
    """Check .env file exists and has required Supabase config keys."""
    print_header("3. Environment Configuration (.env)")

    if not Path(".env").exists():
        print_error(".env file not found")
        print_warning("Please copy .env.example to .env and fill in your credentials:")
        print("  cp .env.example .env")
        return False

    print_ok(".env file found")

    required_keys = ["GROQ_API_KEY"]
    supabase_keys = ["SUPABASE_URL", "SUPABASE_ANON_KEY"]
    optional_db_keys = ["DATABASE_URL", "SUPABASE_DB_URL"]

    env_content = Path(".env").read_text()
    all_present = True

    for key in required_keys:
        if key in env_content:
            if f"{key}=your_" in env_content or f"{key}=" in env_content and "your_" in env_content:
                print_warning(f"{key} = placeholder value (not configured)")
            else:
                print_ok(f"{key} configured")
        else:
            print_error(f"{key} missing from .env")
            all_present = False

    has_supabase = all(key in env_content for key in supabase_keys)
    has_db_url = any(key in env_content for key in optional_db_keys)

    if has_supabase:
        print_ok("Supabase URL and anon key configured")
    else:
        print_error("SUPABASE_URL and SUPABASE_ANON_KEY missing from .env")
        all_present = False

    if has_db_url:
        print_ok("Database connection URL configured for server-side SQL access")
    else:
        print_warning("No DATABASE_URL/SUPABASE_DB_URL configured. Add one for direct SQLAlchemy database access.")

    return all_present


def check_dependencies():
    """Check all Python dependencies are installed"""
    print_header("4. Python Dependencies")

    dependencies = {
        "chainlit": "Chainlit UI framework",
        "langgraph": "LangGraph agent orchestration",
        "langchain": "LangChain core",
        "langchain_groq": "Groq LLM integration",
        "sqlalchemy": "SQLAlchemy ORM",
        "psycopg2": "PostgreSQL driver",
        "pandas": "Pandas data manipulation",
        "openpyxl": "Excel file support",
        "dotenv": "Environment variable loader",
    }
    
    all_installed = True
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            print_ok(f"{package:20} - {description}")
        except ImportError:
            print_error(f"{package:20} - NOT INSTALLED")
            all_installed = False
    
    if not all_installed:
        print_warning("\nInstall missing dependencies:")
        print("  pip install -r requirements.txt")
    
    return all_installed


def check_mysql_connection():
    """Check PostgreSQL database connectivity for Supabase."""
    print_header("5. PostgreSQL Database Connection")

    try:
        from config import DB_CONNECTION_STRING
        from db import get_db_engine

        engine = get_db_engine()

        from sqlalchemy import text
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            print_ok(f"Connected to PostgreSQL: {DB_CONNECTION_STRING.split('@')[1]}")
            return True

    except Exception as e:
        print_error(f"PostgreSQL connection failed: {str(e)}")
        print_warning("\nMake sure:")
        print("  • SUPABASE_URL and SUPABASE_ANON_KEY are configured")
        print("  • DATABASE_URL or SUPABASE_DB_URL is set for server-side SQL access")
        print("  • Supabase project is active and database is reachable")
        return False


def check_groq_api():
    """Check Groq API key validity"""
    print_header("6. Groq API Configuration")
    
    try:
        from config import GROQ_API_KEY
        from langchain_groq import ChatGroq
        
        if not GROQ_API_KEY:
            print_error("GROQ_API_KEY not configured in .env")
            return False
        
        if GROQ_API_KEY.startswith("your_"):
            print_error("GROQ_API_KEY is placeholder value")
            return False
        
        # Try to initialize LLM (doesn't make API call)
        llm = ChatGroq(
            temperature=0,
            model_name="llama-3.3-70b-versatile",
            api_key=GROQ_API_KEY
        )
        print_ok("Groq API key configured")
        print_warning("Full API test requires internet connection")
        return True
    
    except Exception as e:
        print_error(f"Groq API check failed: {str(e)}")
        return False


def check_database_tables():
    """Check if database has any tables"""
    print_header("7. Database Tables")
    
    try:
        from db import get_db_inspector
        
        inspector = get_db_inspector()
        tables = inspector.get_table_names()
        
        if tables:
            print_ok(f"Database has {len(tables)} table(s):")
            for table in tables:
                print(f"    • {table}")
        else:
            print_warning("No tables found (upload a CSV/XLSX file to create tables)")
        
        return True
    
    except Exception as e:
        print_error(f"Failed to check tables: {str(e)}")
        return False


def print_summary(results):
    """Print setup verification summary"""
    print_header("VERIFICATION SUMMARY")
    
    checks = [
        ("Python Version", results[0]),
        ("Project Structure", results[1]),
        ("Environment Config (.env)", results[2]),
        ("Python Dependencies", results[3]),
        ("MySQL Connection", results[4]),
        ("Groq API Configuration", results[5]),
        ("Database Tables", results[6]),
    ]
    
    passed = sum(1 for _, result in checks if result)
    total = len(checks)
    
    print()
    for name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{name:35} {status}")
    
    print()
    print(f"Result: {passed}/{total} checks passed")
    
    if passed == total:
        print_ok("🎉 Setup verification complete! You're ready to start.")
        print("\nStart the application with:")
        print("  Windows: start.bat")
        print("  Linux/macOS: ./start.sh")
        print("  Or: chainlit run app.py -w")
    else:
        print_error("Some checks failed. Please review the errors above.")
        print("\nFor help, see QUICK_START.md or README.md")
    
    return passed == total


def main():
    """Run all verification checks"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "AGENTIC SQL DATA ANALYST - SETUP VERIFICATION" + " " * 3 + "║")
    print("╚" + "═" * 58 + "╝")
    
    results = [
        check_python_version(),
        check_project_structure(),
        check_env_file(),
        check_dependencies(),
        check_mysql_connection(),
        check_groq_api(),
        check_database_tables(),
    ]
    
    success = print_summary(results)
    
    print("\n")
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
