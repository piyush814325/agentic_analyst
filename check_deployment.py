#!/usr/bin/env python3
"""
Quick deployment check script for Vercel
Verifies all necessary files and configurations are in place.
"""

import os
import json
from pathlib import Path

def check_file_exists(filepath, description):
    """Check if a file exists and report status"""
    exists = Path(filepath).exists()
    status = "✅" if exists else "❌"
    print(f"{status} {description}: {filepath}")
    return exists

def check_environment_vars():
    """Check if all required environment variables are set."""
    required_vars = ['GROQ_API_KEY']
    supabase_vars = ['SUPABASE_URL', 'SUPABASE_ANON_KEY']
    legacy_db_var = 'DATABASE_URL'

    print("\n📋 Environment Variables Check:")
    missing = []

    for var in required_vars:
        has_var = var in os.environ
        status = "✅" if has_var else "❌"
        print(f"{status} {var}")
        if not has_var:
            missing.append(var)

    has_supabase = all(var in os.environ for var in supabase_vars)
    has_legacy_db = legacy_db_var in os.environ
    status = "✅" if has_supabase or has_legacy_db else "❌"
    print(f"{status} Supabase credentials ({' or '.join(supabase_vars + [legacy_db_var])})")
    if not (has_supabase or has_legacy_db):
        missing.extend(supabase_vars)

    return len(missing) == 0, missing

def check_vercel_config():
    """Check if Vercel configuration is valid"""
    print("\n⚙️  Vercel Configuration Check:")
    
    vercel_json_path = 'vercel.json'
    if Path(vercel_json_path).exists():
        try:
            with open(vercel_json_path, 'r') as f:
                config = json.load(f)
            print(f"✅ vercel.json is valid JSON")
            
            required_keys = ['buildCommand', 'functions']
            for key in required_keys:
                if key in config:
                    print(f"✅ {key} configured")
                else:
                    print(f"❌ {key} missing")
            return True
        except json.JSONDecodeError:
            print(f"❌ vercel.json is not valid JSON")
            return False
    else:
        print(f"❌ vercel.json not found")
        return False

def check_requirements():
    """Check if requirements.txt exists and has dependencies"""
    print("\n📦 Dependencies Check:")
    
    req_path = 'requirements.txt'
    if Path(req_path).exists():
        with open(req_path, 'r') as f:
            packages = f.read().strip().split('\n')
        
        required_packages = ['chainlit', 'langgraph', 'langchain', 'sqlalchemy', 'psycopg2']
        
        for pkg in required_packages:
            found = any(pkg.lower() in line.lower() for line in packages)
            status = "✅" if found else "❌"
            print(f"{status} {pkg}")
        
        return True
    else:
        print(f"❌ requirements.txt not found")
        return False

def main():
    """Run all deployment checks"""
    print("=" * 60)
    print("🚀 VERCEL DEPLOYMENT READINESS CHECK")
    print("=" * 60)
    
    # Check files
    print("\n📁 Configuration Files Check:")
    checks = [
        check_file_exists('vercel.json', 'Vercel config'),
        check_file_exists('runtime.txt', 'Python runtime'),
        check_file_exists('.vercelignore', 'Vercel ignore'),
        check_file_exists('requirements.txt', 'Dependencies'),
        check_file_exists('VERCEL_DEPLOYMENT.md', 'Deployment guide'),
        check_file_exists('app.py', 'Main application'),
    ]
    
    # Check config validity
    vercel_ok = check_vercel_config()
    req_ok = check_requirements()
    
    # Check environment variables
    env_ok, missing_vars = check_environment_vars()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEPLOYMENT READINESS SUMMARY")
    print("=" * 60)
    
    all_files_ok = all(checks)
    
    if all_files_ok and vercel_ok and req_ok:
        print("✅ Configuration files: READY")
    else:
        print("❌ Configuration files: MISSING OR INVALID")
    
    if env_ok:
        print("✅ Environment variables: READY")
    else:
        print(f"❌ Environment variables: MISSING")
        print(f"   Missing: {', '.join(missing_vars)}")
    
    print("\n📝 Next Steps:")
    if not all_files_ok or not vercel_ok or not req_ok:
        print("1. Ensure all configuration files exist")
        print("2. Check vercel.json is valid JSON")
        print("3. Verify requirements.txt has all dependencies")
    
    if not env_ok:
        print("1. Set environment variables in .env file locally")
        print("2. Add them to Vercel project settings before deployment")
        print(f"3. Required: {', '.join(missing_vars)}")
    
    if all_files_ok and vercel_ok and req_ok:
        print("\n✅ YOUR PROJECT IS READY FOR VERCEL DEPLOYMENT!")
        print("\n1. Push code to GitHub:")
        print("   git push origin main")
        print("\n2. Go to Vercel (https://vercel.com)")
        print("3. Import your GitHub repository")
        print("4. Add environment variables in project settings")
        print("5. Deploy!")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    main()
