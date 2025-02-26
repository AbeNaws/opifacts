# OpiFacts

OpiFacts is a command-line utility that makes it easy to upload files to your GitHub-hosted website. It copies your files to a uniquely named folder in your repository, commits the changes, and pushes them to GitHub, then provides you with a public URL to access your files.

## Features

- Simple command-line interface for uploading files and folders
- Creates a unique folder for each upload using MD5 hash
- Automatically commits and pushes changes to your GitHub repository
- Manages SSH authentication for secure GitHub access
- Outputs a direct URL to access your uploaded content
- Easy installation to your system PATH
- Self-update capability to get the latest version

## Requirements

- Python 3.6+
- Git installed and configured
- A GitHub repository connected to a web server/hosting service
- SSH key set up for GitHub authentication

## Installation

### Quick Install

1. Download the script:
   ```bash
   wget https://raw.githubusercontent.com/yourusername/opifacts/main/opifacts.py
   ```

2. Make it executable:
   ```bash
   chmod +x opifacts.py
   ```

3. Run the setup:
   ```bash
   ./opifacts.py setup
   ```
   
4. During setup, you'll be prompted to install the script to your PATH.

### Manual Installation

If you prefer to install manually after downloading:

1. Copy the script to a directory in your PATH (e.g., ~/.local/bin/):
   ```bash
   cp opifacts.py ~/.local/bin/opifacts
   ```

2. Make it executable:
   ```bash
   chmod +x ~/.local/bin/opifacts
   ```

## Setup

When you first run OpiFacts, it will guide you through a one-time setup process:

1. Specify your GitHub website repository path (local directory)
2. Enter your GitHub username
3. Provide your website URL (e.g., https://yourdomain.com)
4. Set the URL for script updates (or accept the default)
5. Choose whether to install the script to your PATH

The setup process will also:
- Create an "opifacts" folder in your repository (if it doesn't exist)
- Test your Git SSH configuration
- Save your configuration for future use

## Usage

### Upload Files

To upload one or more files:

```bash
opifacts file1.jpg file2.txt
```

To upload all files in a directory:

```bash
opifacts /path/to/directory
```

After uploading, OpiFacts will output a URL where you can access your files, such as:
```
Files are now available at:
https://yourdomain.com/opifacts/a1b2c3d4e5f6g7h8i9j0
```

### Pull Repository Changes

To pull the latest changes from your GitHub repository:

```bash
opifacts pull
```

### Update OpiFacts

To update the OpiFacts script itself to the latest version:

```bash
opifacts update
```

### Run Setup Again

If you need to reconfigure OpiFacts:

```bash
opifacts setup
```

## How It Works

1. OpiFacts creates a unique folder name using an MD5 hash of the current timestamp
2. It creates this folder inside the "opifacts" directory of your GitHub repository
3. It copies the specified files into this folder
4. It commits the changes with a descriptive message
5. It pushes the changes to GitHub using SSH authentication
6. It provides you with the public URL to access your files

## Configuration

OpiFacts stores its configuration in `~/.opifacts_config.json`. This includes:

- Your GitHub repository path
- Your GitHub username
- Your website URL
- The subfolder name for uploads (default: "opifacts")
- The location where the script is installed
- The URL for script updates

## Troubleshooting

### SSH Authentication Issues

If you encounter SSH authentication problems:

1. Ensure your SSH key is added to your GitHub account
2. Check if your SSH agent is running: `ssh-add -l`
3. Add your key to the SSH agent: `ssh-add ~/.ssh/id_ed25519`
4. Test GitHub SSH connection: `ssh -T git@github.com`

### Repository Issues

- Make sure your repository path is correct
- Ensure you have write access to the repository
- Check that the repository has a remote origin configured

### Installation Issues

If the installation to PATH fails:

1. Make sure the target directory exists
2. Check that you have write permissions to the directory
3. For system directories (/usr/local/bin, /usr/bin), you need sudo access

### Update Issues

If the self-update fails:

1. Check your internet connection
2. Verify that the update URL is correct in your configuration
3. Ensure you have write permissions to the script location
4. If the script is installed in a system directory, you may need sudo access

## License

This project is open source and available under the [MIT License](LICENSE).

## Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue for bugs, feature requests, or improvements.
