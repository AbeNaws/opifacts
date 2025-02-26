#!/usr/bin/env python3
"""
OpiFacts - File Upload Utility for GitHub-hosted websites

SETUP INSTRUCTIONS:
1. Make this script executable:
   chmod +x opifacts.py

2. Run the script for the first time to set up configuration:
   ./opifacts.py setup

3. To upload files or folders:
   ./opifacts.py file1.txt folder1 file2.jpg ...
   or, if installed to PATH:
   opifacts file1.txt folder1 file2.jpg ...

4. To pull the latest changes from your repository:
   ./opifacts.py pull
   or:
   opifacts pull

5. To update the OpiFacts script itself:
   ./opifacts.py update
   or:
   opifacts update

The script will copy the files to a uniquely named folder in your repository,
commit the changes, and push them to GitHub. It will output a public URL
where you can access the files.
"""

import os
import sys
import shutil
import time
import hashlib
import subprocess
import json
import urllib.request
from pathlib import Path

# Configuration - these will be set during first-time setup
CONFIG_FILE = os.path.expanduser("~/.opifacts_config.json")
DEFAULT_CONFIG = {
    "GITHUB_REPO_PATH": "",        # Path to your GitHub repository
    "GITHUB_USERNAME": "",         # Your GitHub username
    "WEBSITE_URL": "",             # Your website URL (e.g., https://abenaws.dev)
    "OPIFACTS_SUBFOLDER": "opifacts",  # Subfolder name within the repo for uploaded content
    "SCRIPT_LOCATION": "",         # Where the script is installed (set during installation)
    "SCRIPT_UPDATE_URL": "https://raw.githubusercontent.com/AbeNaws/OpiFacts/main/opifacts", # Update source
    "setup_completed": False       # Flag to track if setup has been completed
}

# Load configuration
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Error reading config file. Using default configuration.")
            return DEFAULT_CONFIG.copy()
    return DEFAULT_CONFIG.copy()

# Save configuration
def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    # Make sure only the user can read the file (contains personal paths)
    os.chmod(CONFIG_FILE, 0o600)

# Global config object
CONFIG = load_config()

def get_bin_directories():
    """Get a list of available bin directories for installing the script"""
    bin_dirs = []
    
    # User bin directory (no sudo required)
    user_bin = os.path.expanduser("~/.local/bin")
    if os.path.exists(user_bin):
        bin_dirs.append((user_bin, False))  # (path, needs_sudo)
    
    # System bin directories (require sudo)
    system_bins = ["/usr/local/bin", "/usr/bin"]
    for path in system_bins:
        if os.path.exists(path):
            bin_dirs.append((path, True))  # (path, needs_sudo)
    
    return bin_dirs

def install_script(bin_dir, needs_sudo):
    """Install the script to the bin directory with the name 'opifacts'"""
    current_script = os.path.abspath(sys.argv[0])
    destination = os.path.join(bin_dir, "opifacts")
    
    try:
        if needs_sudo:
            print(f"Installing to {destination} (requires sudo)...")
            subprocess.run(["sudo", "cp", current_script, destination], check=True)
            subprocess.run(["sudo", "chmod", "+x", destination], check=True)
        else:
            print(f"Installing to {destination}...")
            shutil.copy2(current_script, destination)
            os.chmod(destination, 0o755)  # Make executable
        
        # Save the installation location to config
        CONFIG["SCRIPT_LOCATION"] = destination
        save_config(CONFIG)
        
        print(f"Successfully installed 'opifacts' to {bin_dir}")
        print("You can now run the script using just 'opifacts' command")
        return True
    except Exception as e:
        print(f"Error installing script: {e}")
        return False

def update_script():
    """Update the OpiFacts script to the latest version"""
    script_location = CONFIG.get("SCRIPT_LOCATION", "")
    update_url = CONFIG.get("SCRIPT_UPDATE_URL", "")
    
    if not script_location or not os.path.exists(script_location):
        print("Error: Can't determine script location for update.")
        script_location = os.path.abspath(sys.argv[0])
        print(f"Attempting to update current script at: {script_location}")
    
    if not update_url:
        print("Error: Update URL not configured.")
        print("Please set the SCRIPT_UPDATE_URL in your config file (~/.opifacts_config.json)")
        return False
    
    print(f"Updating OpiFacts from: {update_url}")
    print(f"Current script location: {script_location}")
    
    try:
        # Check if we need sudo
        needs_sudo = not os.access(os.path.dirname(script_location), os.W_OK)
        
        # Create temporary file for download
        temp_file = os.path.join(os.path.dirname(script_location), ".opifacts.new")
        
        # Download the latest version
        print("Downloading latest version...")
        urllib.request.urlretrieve(update_url, temp_file)
        
        # Make it executable
        os.chmod(temp_file, 0o755)
        
        # Replace the current script
        if needs_sudo:
            print("Updating script (requires sudo)...")
            subprocess.run(["sudo", "mv", temp_file, script_location], check=True)
        else:
            print("Updating script...")
            shutil.move(temp_file, script_location)
        
        print("OpiFacts has been successfully updated!")
        return True
    except Exception as e:
        print(f"Error updating script: {e}")
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        return False

def guided_setup():
    """Interactive setup process for first-time users"""
    print("Welcome to OpiFacts Setup!")
    print("This will guide you through the configuration process.\n")
    
    config = CONFIG.copy()
    
    # GitHub repo path
    while True:
        repo_path = input(f"Enter the full path to your GitHub repository: ").strip()
        if os.path.exists(repo_path) and os.path.isdir(repo_path):
            config["GITHUB_REPO_PATH"] = repo_path
            break
        else:
            print(f"Error: The path '{repo_path}' does not exist or is not a directory. Please try again.")
    
    # GitHub username
    config["GITHUB_USERNAME"] = input("Enter your GitHub username: ").strip()
    
    # Website URL
    while True:
        website_url = input("Enter your website URL (e.g., https://abenaws.dev): ").strip()
        if website_url.startswith(("http://", "https://")):
            config["WEBSITE_URL"] = website_url.rstrip('/')
            break
        else:
            print("Error: URL must start with http:// or https://")
    
    # Script update URL
    update_url = input(f"Enter the URL for script updates (press Enter for default: {DEFAULT_CONFIG['SCRIPT_UPDATE_URL']}): ").strip()
    if update_url:
        config["SCRIPT_UPDATE_URL"] = update_url
    else:
        config["SCRIPT_UPDATE_URL"] = DEFAULT_CONFIG["SCRIPT_UPDATE_URL"]
    
    # Create opifacts subfolder in the repository if it doesn't exist
    opifacts_path = os.path.join(config["GITHUB_REPO_PATH"], config["OPIFACTS_SUBFOLDER"])
    if not os.path.exists(opifacts_path):
        try:
            os.makedirs(opifacts_path, exist_ok=True)
            print(f"Created '{config['OPIFACTS_SUBFOLDER']}' folder in your repository.")
        except Exception as e:
            print(f"Warning: Could not create '{config['OPIFACTS_SUBFOLDER']}' folder: {e}")
    
    # Ask about installing to bin directory
    bin_dirs = get_bin_directories()
    if bin_dirs:
        install_choice = input("\nWould you like to install 'opifacts' to your PATH? (y/n): ").strip().lower()
        if install_choice == 'y':
            print("\nAvailable installation locations:")
            for i, (path, needs_sudo) in enumerate(bin_dirs, 1):
                sudo_note = " (requires sudo)" if needs_sudo else ""
                print(f"{i}. {path}{sudo_note}")
            
            while True:
                try:
                    choice = input("\nSelect installation location (number) or 'n' to skip: ").strip()
                    if choice.lower() == 'n':
                        break
                        
                    choice_idx = int(choice) - 1
                    if 0 <= choice_idx < len(bin_dirs):
                        bin_dir, needs_sudo = bin_dirs[choice_idx]
                        install_script(bin_dir, needs_sudo)
                        break
                    else:
                        print(f"Please enter a number between 1 and {len(bin_dirs)}")
                except ValueError:
                    print("Please enter a valid number or 'n'")
    
    config["setup_completed"] = True
    save_config(config)
    
    print("\nSetup completed! You can now use OpiFacts to upload files.")
    print(f"Run: ./opifacts.py file1.txt folder1 ...")
    print(f"Or (if installed to PATH): opifacts file1.txt folder1 ...")
    
    return config

def create_hash_folder():
    """Create a folder name based on current time hash inside the opifacts folder"""
    timestamp = str(time.time() * 100)  # Time to 100th of a second
    hash_obj = hashlib.md5(timestamp.encode())
    folder_name = hash_obj.hexdigest()
    
    # Create the opifacts folder if it doesn't exist
    opifacts_path = os.path.join(CONFIG["GITHUB_REPO_PATH"], CONFIG["OPIFACTS_SUBFOLDER"])
    os.makedirs(opifacts_path, exist_ok=True)
    
    # Create the hash folder inside opifacts
    folder_path = os.path.join(opifacts_path, folder_name)
    os.makedirs(folder_path, exist_ok=True)
    
    return folder_path, folder_name

def ensure_ssh_remote():
    """Ensure the repository is using SSH for the remote URL"""
    try:
        # Get the current remote URL
        os.chdir(CONFIG["GITHUB_REPO_PATH"])
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
        print(f"  git remote set-url origin git@github.com:{CONFIG['GITHUB_USERNAME']}/reponame.git")
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
    if not os.path.exists(CONFIG["GITHUB_REPO_PATH"]):
        print(f"Error: Repository path {CONFIG['GITHUB_REPO_PATH']} does not exist")
        sys.exit(1)
        
    # Create a new folder with hash name inside opifacts folder
    dest_folder, folder_hash = create_hash_folder()
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
        os.chdir(CONFIG["GITHUB_REPO_PATH"])
        
        # Check SSH configuration
        ssh_remote_ok = ensure_ssh_remote()
        ssh_agent_ok = ensure_ssh_agent()
        
        if not ssh_remote_ok or not ssh_agent_ok:
            print("SSH configuration needs attention. See messages above.")
            print("Changes committed locally but not pushed to GitHub.")
            # Still commit locally even if we can't push
            subprocess.run(["git", "add", "."], check=True)
            subprocess.run(["git", "commit", "-m", f"Add files to {CONFIG['OPIFACTS_SUBFOLDER']}/{os.path.basename(dest_folder)}"], check=True)
            return
        
        # Git commands
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", f"Add files to {CONFIG['OPIFACTS_SUBFOLDER']}/{os.path.basename(dest_folder)}"], check=True)
        
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
        
        # Print the public URL
        public_url = f"{CONFIG['WEBSITE_URL']}/{CONFIG['OPIFACTS_SUBFOLDER']}/{folder_hash}"
        print("\nFiles are now available at:")
        print(public_url)
        
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        sys.exit(1)

def pull_repo():
    """Pull the latest changes from the GitHub repository"""
    if not os.path.exists(CONFIG["GITHUB_REPO_PATH"]):
        print(f"Error: Repository path {CONFIG['GITHUB_REPO_PATH']} does not exist")
        sys.exit(1)
        
    try:
        # Change to repo directory
        os.chdir(CONFIG["GITHUB_REPO_PATH"])
        
        # Ensure SSH is configured properly
        ensure_ssh_remote()
        
        # Git pull
        subprocess.run(["git", "pull"], check=True)
        
        print("Successfully pulled the latest changes from the repository")
    except subprocess.CalledProcessError as e:
        print(f"Error during git operations: {e}")
        sys.exit(1)

def main():
    global CONFIG
    
    # Check if setup is needed
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        CONFIG = guided_setup()
        return
    
    # Check if setup is completed
    if not CONFIG["setup_completed"]:
        print("OpiFacts hasn't been set up yet.")
        user_input = input("Would you like to run the setup now? (y/n): ")
        if user_input.lower() == 'y':
            CONFIG = guided_setup()
        else:
            print("Setup aborted. Please run './opifacts.py setup' when you're ready.")
            sys.exit(1)
        return

    if len(sys.argv) < 2:
        print("Usage:")
        print("  ./opifacts.py <file1> <file2> ... <folder1> ...")
        print("  ./opifacts.py pull       (pull latest changes from repository)")
        print("  ./opifacts.py update     (update the OpiFacts script)")
        print("  ./opifacts.py setup      (run setup again)")
        sys.exit(1)
        
    if sys.argv[1] == "pull":
        pull_repo()
    elif sys.argv[1] == "update":
        update_script()
    else:
        # Files/folders to copy are all arguments
        sources = sys.argv[1:]
        copy_files_to_repo(sources)

if __name__ == "__main__":
    main()
