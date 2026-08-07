"""
Automated Git Commit & Push Trigger Script
Repository: abdulnabii/priv

Features:
  • Auto-syncs with remote (pull/merge) to prevent rejection errors mid-batch
  • Automatic push retry logic with fallback
  • Batch commit & push execution
  • Interactive prompt menu & Command-line flags
"""

import os
import sys
import time
import argparse
import subprocess
from datetime import datetime

LOG_FILE = "activity_log.txt"
BRANCH = "main"

def run_cmd(cmd, cwd=None, quiet=False):
    """Run a shell command and return success status."""
    if not quiet:
        print(f"Running: {cmd}")
    result = subprocess.run(cmd, shell=True, cwd=cwd, text=True, capture_output=True)
    if not quiet:
        if result.stdout.strip():
            print(f"  [stdout] {result.stdout.strip()}")
        if result.stderr.strip():
            print(f"  [stderr] {result.stderr.strip()}")
    return result.returncode == 0

def sync_remote():
    """Pull remote changes to avoid non-fast-forward push rejections."""
    print("[INFO] Syncing with remote repository...")
    run_cmd(f"git pull origin {BRANCH} --no-rebase -X ours", quiet=True)
    run_cmd(f"git add {LOG_FILE}", quiet=True)
    run_cmd("git commit -m 'chore: sync remote'", quiet=True)

def safe_push(retries=3):
    """Attempt git push with automatic sync retry if rejected."""
    for attempt in range(1, retries + 1):
        if run_cmd(f"git push origin {BRANCH}", quiet=True):
            return True
        print(f"[WARN] Push attempt {attempt}/{retries} failed. Syncing with remote and retrying...")
        sync_remote()
        time.sleep(1.0)
    return False

def update_activity_file(index=1, total=1):
    """Append a timestamp entry to activity_log.txt."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{now}] Automated commit trigger ({index}/{total})\n"
    
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)
    
    print(f"[OK] ({index}/{total}) Updated {LOG_FILE}: {entry.strip()}")

def execute_batch_commits(count=1, custom_msg="", push_strategy="each", delay=1.0):
    """
    Execute batch commits and pushes with auto-recovery logic.
    """
    print("\n" + "=" * 55)
    print(f"  Starting Batch Commit Process")
    print(f"  Total Commits : {count}")
    print(f"  Push Strategy : {push_strategy.upper()}")
    print(f"  Delay         : {delay}s between commits")
    print("=" * 55 + "\n")

    # Initial sync before starting batch
    sync_remote()

    successful_commits = 0

    for i in range(1, count + 1):
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if custom_msg:
            commit_msg = f"{custom_msg} ({i}/{count})" if count > 1 else custom_msg
        else:
            commit_msg = f"chore: automated activity commit {i}/{count} at {now_str}"

        # 1. Update activity log
        update_activity_file(index=i, total=count)

        # 2. Git Add
        if not run_cmd("git add -A", quiet=True):
            print(f"[ERROR] Failed to stage files for commit {i}")
            continue

        # 3. Git Commit
        if not run_cmd(f'git commit -m "{commit_msg}"', quiet=True):
            print(f"[WARN] Commit {i} failed or no changes to commit.")
            continue

        successful_commits += 1
        print(f"[SUCCESS] Created commit {i}/{count}: '{commit_msg}'")

        # 4. Push if strategy is 'each'
        if push_strategy == "each":
            print(f"[INFO] Pushing commit {i}/{count} to remote...")
            if safe_push(retries=3):
                print(f"[SUCCESS] Pushed commit {i}/{count} to GitHub!")
            else:
                print(f"[ERROR] Failed to push commit {i}/{count}. It will be pushed in final batch sync.")

        # Delay if not last iteration
        if i < count and delay > 0:
            time.sleep(delay)

    # Final guarantee push for all commits
    if successful_commits > 0 and push_strategy != "none":
        print("\n[INFO] Running final verification push for all commits...")
        if safe_push(retries=3):
            print("[SUCCESS] All commits are 100% synced & pushed to GitHub!")
        else:
            print("[ERROR] Final push failed. Please check internet connection.")

    print("\n" + "=" * 55)
    print(f"  Batch Complete: {successful_commits}/{count} commits created & processed.")
    print("=" * 55 + "\n")
    return successful_commits > 0

def interactive_menu():
    """Prompt user interactively for options."""
    print("=" * 60)
    print("      Git Automated Commit & Push Activity Trigger 🚀")
    print("      Repository: abdulnabii/priv")
    print("=" * 60)

    # 1. Ask count
    while True:
        try:
            raw = input("\n👉 How many commits/pushes would you like to make? [Default: 1]: ").strip()
            count = int(raw) if raw else 1
            if count > 0:
                break
            print("  Please enter a positive integer > 0.")
        except ValueError:
            print("  Invalid number. Please enter an integer.")

    # 2. Ask custom message
    custom_msg = input("👉 Enter custom commit message (Press Enter for default timestamp message): ").strip()

    # 3. Ask push strategy
    if count > 1:
        print("\n👉 Choose Push Strategy:")
        print("   [1] Push after EACH commit (triggers multiple GitHub activity points)")
        print("   [2] Push ONCE at the end (faster execution & recommended for large batches)")
        print("   [3] Local commits only (Do not push)")
        choice = input("   Select option (1/2/3) [Default: 1]: ").strip()
        
        if choice == "2":
            push_strategy = "end"
        elif choice == "3":
            push_strategy = "none"
        else:
            push_strategy = "each"
    else:
        push_choice = input("👉 Push commit to GitHub? (y/n) [Default: y]: ").strip().lower()
        push_strategy = "each" if push_choice in ("", "y", "yes") else "none"

    # 4. Ask delay
    if count > 1:
        try:
            raw_delay = input("👉 Enter delay between commits in seconds [Default: 1.0]: ").strip()
            delay = float(raw_delay) if raw_delay else 1.0
        except ValueError:
            delay = 1.0
    else:
        delay = 0.0

    return execute_batch_commits(
        count=count,
        custom_msg=custom_msg,
        push_strategy=push_strategy,
        delay=delay
    )

def main():
    parser = argparse.ArgumentParser(description="Automated Git Commit & Push Activity Trigger")
    parser.add_argument("-c", "--count", type=int, default=None, help="Number of commits to make")
    parser.add_argument("-m", "--message", type=str, default="", help="Custom commit message")
    parser.add_argument("-p", "--push-strategy", choices=["each", "end", "none"], default="each", help="Push strategy")
    parser.add_argument("-d", "--delay", type=float, default=1.0, help="Delay in seconds between commits")
    parser.add_argument("-i", "--interactive", action="store_true", help="Force interactive mode")

    args = parser.parse_args()

    if args.count is not None and not args.interactive:
        success = execute_batch_commits(
            count=args.count,
            custom_msg=args.message,
            push_strategy=args.push_strategy,
            delay=args.delay
        )
        sys.exit(0 if success else 1)
    else:
        success = interactive_menu()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
