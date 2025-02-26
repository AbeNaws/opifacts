#!/usr/bin/env python3
import os
import sys
import shutil
import time
import hashlib
import subprocess
from pathlib import Path

# Configuration
GITHUB_REPO_PATH = "/home/lincoln/Programs/opifacts/"  # Change this to your actual repo path
GITHUB_USERNAME = "your-github-username"  # Add your GitHub username here

def create_hash_folder():
    """Create a folder name based on current time hash"""
    timestamp = str(time.time() * 100)  # Time to 100th of a second
    hash_obj = hashlib.md5(timestamp.encode())
    folder_name = hash_obj.hexdigest()
    
    # Create the folder in the repo
    folder_path = os.path.join(GITHUB_REPO_PATH, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    return folder_path

def ensure_ssh_remote():
    """Ensure the repository is using SSH for the remote URL"""
    try:
        # Get the current remote URL
        os.chdir(GITHUB_REPO_PATH)
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"], 
            capture_output=True, 
            text=True,
            check=True
        )
        current_url = result.stdout.strip()
        
        # Check if it's already an SSH URL
        if current_url.startswith("git@github.com:"):
            print("Remote already using SSH URL")
            return True
        
        # Extract repo name from HTTPS URL
        # Format: https://github.com/username/repo.git or https://github.com/username/repo
        if current_url.startswith("https://github.com/"):
            parts = current_url.replace("https://github.com/", "").split("/")
            if len(parts) >= 2:
                username = parts[0]
                repo_name = parts[1]
                if repo_name.endswith(".git"):
                    repo_name = repo_name[:-4]
                
                # Set the new SSH URL
                ssh_url = f"git@github.com:{username}/{repo_name}.git"
                subprocess.run(["git", "remote", "set-url", "origin", ssh_url], check=True)
                print(f"Updated remote URL to use SSH: {ssh_url}")
                return True
        
        print(f"Warning: Could not automatically convert remote URL: {current_url}")
        print("Please manually set your remote to use SSH with:")
        print(f"  git remote set-url origin git@github.com:{GITHUB_USERNAME}/reponame.git")
        return False
    except subprocess.CalledProcessError as e:
        print(f"Error checking/updating remote URL: {e}")
        return False

def ensure_ssh_agent():
    """Ensure the SSH agent is running"""
    try:
        # Check if SSH agent is running
        result = subprocess.run(
            ["ssh-add", "-l"], 
            capture_output=True, 
            text=True
        )
        if "The agent has no identities" in result.stdout:
            print("SSH agent is running but has no keys")
            print("Please add your SSH key to the agent:")
            print("  ssh-add ~/.ssh/id_ed25519")
            return False
        elif result.returncode == 0:
            print("SSH agent is running with keys")
            return True
        else:
            # Try to start the SSH agent
            print("Starting SSH agent...")
            result = subprocess.run(
                ["eval", "$(ssh-agent -s)"], 
                shell=True,
                capture_output=True,
                text=True
            )
            print("Please add your SSH key to the agent:")
            print("  ssh-add ~/.ssh/id_ed25519")
            return False
    except Exception as e:
        print(f"Error checking SSH agent: {e}")
        return False

def copy_files_to_repo(sources):
    """Copy files or folder contents to the repo in a new hash folder"""
    if not os.path.exists(GITHUB_REPO_PATH):
        print(f"Error: Repository path {GITHUB_REPO_PATH} does not exist")
        sys.exit(1)
        
    # Create a new folder with hash name
    dest_folder = create_hash_folder()
    print(f"Created folder: {dest_folder}")
    
    # Process each source
    for source in sources:
        if not os.path.exists(source):
            print(f"Warning: {source} does not exist, skipping")
            continue
            
        if os.path.isfile(source):
            # Copy file
            shutil.copy2(source, dest_folder)
            print(f"Copied file: {source} to {dest_folder}")
        elif os.path.isdir(source):
            # Copy directory contents
            for item in os.listdir(source):
                item_path = os.path.join(source, item)
                if os.path.isfile(item_path):
                    shutil.copy2(item_path, dest_folder)
                    print(f"Copied file: {item_path} to {dest_folder}")
    
    # Push changes to GitHub
    try:
        # Change to repo directory
        os.chdir(GITHUB_REPO_PATH)
        
        # Check SSH configuration
        ssh_remote_ok = ensure_ssh_remote()
        ssh_agent_ok = ensure_ssh_agent()
        
        if not ssh_remote_ok or not ssh_agent_ok:
            print("SSH configuration needs attention. See messages above.")
            print("Changes committed locally but not pushed to GitHub.")
            # Still commit locally even if we can't push
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"Add files to {os.path.basename(dest_folder)}"], check=True)
            return
        
        # Git commands
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Add files to {os.path.basename(dest_folder)}"], check=True)
        
        # Test SSH connection to GitHub before pushing
        print("Testing SSH connection to GitHub...")
        test_result = subprocess.run(
            ["ssh", "-T", "git@github.com"],
            capture_output=True,
            text=True
        )
        # GitHub returns non-zero exit code even on success, but includes a greeting
        if "successfully authenticated" in test_result.stderr:
            print("SSH connection to GitHub verified")
        else:
            print("Warning: SSH authentication to GitHub may not be set up correctly")
            print(test_result.stderr)
            user_choice = input("Continue with git push anyway? (y/n): ")
            if user_choice.lower() != 'y':
                print("Push aborted. Changes committed locally.")
                return
        
        # Push with SSH
        subprocess.run(["git", "push"], check=True)
        print("Successfully pushed changes to GitHub using SSH key")
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        sys.exit(1)

def update_repo():
    """Pull the latest changes from the GitHub repository"""
    if not os.path.exists(GITHUB_REPO_PATH):
        print(f"Error: Repository path {GITHUB_REPO_PATH} does not exist")
        sys.exit(1)
        
    try:
        # Change to repo directory
        os.chdir(GITHUB_REPO_PATH)
        
        # Ensure SSH is configured properly
        ensure_ssh_remote()
        
        # Git pull
        subprocess.run(["git", "pull"], check=True)
        
        print("Successfully updated the repository")
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        sys.exit(1)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  opifact <file1> <file2> ... <folder1> ...")
        print("  opifact update")
        sys.exit(1)
        
    if sys.argv[1] == "update":
        update_repo()
    else:
        # Files/folders to copy are all arguments
        sources = sys.argv[1:]
        copy_files_to_repo(sources)

if __name__ == "__main__":
    main()
