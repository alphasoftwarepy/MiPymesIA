#!/usr/bin/env python3
"""
Cron script to expire users daily at 2 AM.
Add to crontab: 0 2 * * * /path/to/python /path/to/expire_users_cron.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import auth

if __name__ == "__main__":
    print("Running daily user expiration check...")
    expired_count = auth.check_and_expire_users()
    print(f"Expired {expired_count} users")
