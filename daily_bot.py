import os
import subprocess
import random
from datetime import datetime

REPO_DIR = r"c:\Users\himan\project1"

def run_cmd(cmd):
    res = subprocess.run(cmd, shell=True, cwd=REPO_DIR, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return res.stdout.strip(), res.stderr.strip()

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"Running Daily Commit Bot for {today}...")

    # Check git status for modified/untracked files
    status_out, _ = run_cmd("git status --porcelain")
    
    if status_out:
        run_cmd("git add .")
        commit_msg = f"Update project files - {today}"
        run_cmd(f'git commit -m "{commit_msg}"')
        print(f"Committed changes: {commit_msg}")
        
        # Push to remote if remote exists
        remote_out, _ = run_cmd("git remote")
        if remote_out:
            push_out, err = run_cmd("git push origin main")
            print("Pushed commits to GitHub remote successfully.")
        else:
            print("No git remote configured yet. Add origin remote to enable automatic push.")
    else:
        print("No changes to commit today. Project is up to date!")

if __name__ == "__main__":
    main()
