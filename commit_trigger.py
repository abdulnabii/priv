"""
Automated Git Commit & Push Trigger Script
Repository: abdulnabii/priv

This script updates a log file, stages changes, creates a Git commit,
and pushes it to GitHub to trigger repository commit activity.
"""

import os
import sys
import subprocess
from datetime import datetime

LOG_FILE = "activity_log.txt"
BRANCH = "main"

def run_cmd(cmd, cwd=None):
    """Run a shell command and return stdout/stderr."""
    print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True)
    if result.stdout.strip():
        print(f"  [stdout] {result.stdout.strip()}")
    if result.stderr.strip():
        print(f"  [stderr] {result.stderr.strip()}")
    return result.returncode == 0

def update_activity_file():
    """Append a timestamp entry to activity_log.txt."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{now}] Automated commit activity trigger\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"[OK] Updated {LOG_FILE} with entry: {entry.strip()}")

def trigger_commit(message=None, push=True):
    """Stage, commit, and optionally push to remote."""
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    commit_msg = message or f"chore: automated activity commit at {now_str}"
    
    # 1. Update activity log file
    update_activity_file()
    
    # 2. Git Add (stage activity log, script, and workflow)
    if not run_cmd("git add -A"):
        print("[ERROR] Failed to stage files.")
        return False
        
    # 3. Git Commit
    if not run_cmd(f'git commit -m "{commit_msg}"'):
        print("[WARN] Nothing to commit or commit failed.")
        return False
        
    print("[SUCCESS] Commit created successfully!")
    
    # 4. Git Push
    if push:
        print("[INFO] Pushing to remote...")
        if run_cmd(f"git push origin {BRANCH}"):
            print("[SUCCESS] Pushed commit to GitHub repository!")
            return True
        else:
            print("[ERROR] Git push failed. Check remote credentials.")
            return False
            
    return True

if __name__ == "__main__":
    msg = sys.argv[1] if len(sys.argv) > 1 else None
    success = trigger_commit(message=msg, push=True)
    sys.exit(0 if success else 1)
