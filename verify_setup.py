#!/usr/bin/env python3
"""
V8 Trading Bot - Setup Verification Script
Checks if all requirements are met before running the system.
"""

import sys
import os
from pathlib import Path

def check_files():
    """Check if all required files exist"""
    required_files = [
        'live_paper_trade_v8.py',
        'api_server.py',
        'requirements.txt',
        '.env',
        'live_state.json',
        'start.sh'
    ]

    print("📁 Checking required files...")
    all_exist = True
    for file in required_files:
        exists = Path(file).exists()
        status = "✅" if exists else "❌"
        print(f"   {status} {file}")
        if not exists:
            all_exist = False

    return all_exist

def check_env():
    """Check environment variables"""
    print("\n🔑 Checking environment configuration...")

    if not Path('.env').exists():
        print("   ❌ .env file not found")
        return False

    with open('.env', 'r') as f:
        content = f.read()

    if 'CEREBRAS_API_KEY' not in content:
        print("   ❌ CEREBRAS_API_KEY not found in .env")
        return False

    if 'your_cerebras_api_key_here' in content:
        print("   ⚠️  CEREBRAS_API_KEY is placeholder - update with real key")
        return False

    print("   ✅ CEREBRAS_API_KEY configured")
    return True

def check_python_modules():
    """Check if required Python modules are available"""
    print("\n📦 Checking Python dependencies...")

    required_modules = [
        'pandas',
        'numpy',
        'yfinance',
        'openai',
        'fastapi',
        'uvicorn',
        'pandas_ta',
        'dotenv'
    ]

    missing = []
    for module in required_modules:
        try:
            if module == 'dotenv':
                __import__('dotenv')
            elif module == 'pandas_ta':
                __import__('pandas_ta')
            else:
                __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} (not installed)")
            missing.append(module)

    return len(missing) == 0, missing

def check_node():
    """Check Node.js setup for dashboard"""
    print("\n🌐 Checking dashboard setup...")

    dashboard_path = Path('dashboard-next')
    if not dashboard_path.exists():
        print("   ❌ dashboard-next directory not found")
        return False

    node_modules = dashboard_path / 'node_modules'
    if not node_modules.exists():
        print("   ⚠️  node_modules not found - run: cd dashboard-next && npm install")
        return False

    print("   ✅ Dashboard dependencies installed")
    return True

def main():
    print("=" * 60)
    print("🚀 V8 TRADING BOT - SETUP VERIFICATION")
    print("=" * 60)

    files_ok = check_files()
    env_ok = check_env()
    modules_ok, missing_modules = check_python_modules()
    node_ok = check_node()

    print("\n" + "=" * 60)
    print("📊 VERIFICATION SUMMARY")
    print("=" * 60)

    if files_ok and env_ok and modules_ok and node_ok:
        print("\n✅ All checks passed! System is ready to run.")
        print("\n🚀 To start the system, run:")
        print("   ./start.sh")
        print("\n📊 Then open: http://localhost:3000")
        return 0
    else:
        print("\n⚠️  Some requirements are not met:\n")

        if not files_ok:
            print("   ❌ Missing required files")

        if not env_ok:
            print("   ❌ Environment configuration incomplete")
            print("      → Update CEREBRAS_API_KEY in .env file")

        if not modules_ok:
            print("   ❌ Missing Python dependencies")
            print("      → Run: pip3 install -r requirements.txt")
            if missing_modules:
                print(f"      Missing: {', '.join(missing_modules)}")

        if not node_ok:
            print("   ❌ Dashboard dependencies not installed")
            print("      → Run: cd dashboard-next && npm install")

        print("\n📚 See QUICK_START.md for detailed setup instructions")
        return 1

if __name__ == "__main__":
    sys.exit(main())
