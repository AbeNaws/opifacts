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

def create_hash_folder():
    """Create a folder name based on current time hash"""
    timestamp = str(time.time() * 100)  # Time to 100th of a second
    hash_obj = hashlib.md5(timestamp.encode())
    folder_name = hash_obj.hexdigest()
    
    # Create the folder in the repo
    folder_path = os.path.join(GITHUB_REPO_PATH, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    return folder_path

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
        
        # Git commands
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Add files to {os.path.basename(dest_folder)}"], check=True)
        
        # Use SSH for pushing (assumes SSH key is properly set up)
        # To set up SSH keys:
        # 1. Generate a new SSH key: ssh-keygen -t ed25519 -C "your_email@example.com"
        # 2. Add the SSH key to the ssh-agent: eval "$(ssh-agent -s)" and ssh-add ~/.ssh/id_ed25519
        # 3. Add the SSH key to your GitHub account: Copy the contents of ~/.ssh/id_ed25519.pub and add it to your GitHub SSH keys
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
