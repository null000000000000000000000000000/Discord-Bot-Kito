#!/usr/bin/env python3
import sys
import os
import subprocess

def check_python_version():
    version = sys.version_info
    if version.major < 3 or version.minor < 10:
        print("❌ Python 3.10+ is required.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_dependencies():
    required = ["discord", "dotenv", "sqlalchemy", "aiofiles", "dateutil"]
    missing = []
    for pkg in required:
        try:
            __import__(pkg)
            print(f"✅ {pkg}")
        except ImportError:
            print(f"❌ {pkg} missing")
            missing.append(pkg)
    if missing:
        print(f"\nRun: pip install -r requirements.txt")
        return False
    return True

def check_files():
    files = [
        "bot.py",
        "run.py",
        "requirements.txt",
        ".env",
        "utils/config.py",
        "utils/logger.py",
        "utils/errors.py",
        "utils/helpers.py",
        "utils/cooldown.py",
        "utils/permissions.py",
        "database/models.py",
        "database/manager.py",
        "cogs/__init__.py",
    ]
    base = os.path.dirname(os.path.abspath(__file__))
    all_ok = True
    for f in files:
        path = os.path.join(base, f)
        if os.path.exists(path):
            print(f"✅ {f}")
        else:
            print(f"❌ {f} missing")
            all_ok = False
    return all_ok

def check_cogs():
    base = os.path.dirname(os.path.abspath(__file__))
    cogs_dir = os.path.join(base, "cogs")
    cogs = [f for f in os.listdir(cogs_dir) if f.endswith(".py") and not f.startswith("_")]
    print(f"\nFound {len(cogs)} cogs:")
    for cog in sorted(cogs):
        print(f"  ✅ {cog}")
    return True

def check_syntax():
    print("\nChecking syntax...")
    base = os.path.dirname(os.path.abspath(__file__))
    files = [
        "bot.py",
        "run.py",
        "utils/config.py",
        "utils/logger.py",
        "utils/errors.py",
        "utils/helpers.py",
        "utils/cooldown.py",
        "utils/permissions.py",
        "database/models.py",
        "database/manager.py",
    ]
    all_ok = True
    for f in files:
        path = os.path.join(base, f)
        result = subprocess.run([sys.executable, "-m", "py_compile", path], capture_output=True)
        if result.returncode == 0:
            print(f"✅ {f}")
        else:
            print(f"❌ {f}: {result.stderr.decode()}")
            all_ok = False
    return all_ok

if __name__ == "__main__":
    print("=" * 50)
    print("TAIKO Bot Verification")
    print("=" * 50)
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Core Files", check_files),
        ("Cogs", check_cogs),
        ("Syntax", check_syntax),
    ]
    
    passed = 0
    for name, check in checks:
        print(f"\n--- {name} ---")
        if check():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"Result: {passed}/{len(checks)} checks passed")
    print("=" * 50)
    
    if passed == len(checks):
        print("✅ Bot is ready to run!")
        print("Run with: python run.py")
    else:
        print("❌ Please fix the issues above before running.")
