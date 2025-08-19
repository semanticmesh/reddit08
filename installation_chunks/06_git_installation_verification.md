# Installation Chunk 06: Git Installation Verification

## Overview
This installation chunk verifies Git installation and basic configuration for the CRE Intelligence Platform.

## Prerequisites
- System requirements verification completed (Chunk 01)

## Procedure

### 1. Verify Git Installation
Check if Git is installed:
```bash
git --version
```

Expected output: git version 2.0 or higher

If Git is not installed:

#### Windows
1. Download Git from https://git-scm.com/downloads
2. Run the installer with default settings
3. Choose "Git from the command line and also from 3rd-party software" during installation

#### macOS
Using Homebrew:
```bash
brew install git
```

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install git
```

#### CentOS/RHEL/Fedora
```bash
sudo yum install git
# or for newer versions:
sudo dnf install git
```

### 2. Configure Git User Information
Set your Git user name and email:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

Verify the configuration:
```bash
git config --global user.name
git config --global user.email
```

### 3. Configure Git Default Editor
Set your preferred text editor (optional):
```bash
# For VS Code
git config --global core.editor "code --wait"

# For Vim (default on many systems)
git config --global core.editor "vim"

# For Nano
git config --global core.editor "nano"
```

### 4. Configure Git Line Ending Settings
#### Windows
```bash
git config --global core.autocrlf true
```

#### macOS/Linux
```bash
git config --global core.autocrlf input
```

### 5. Test Git Functionality
Create a test directory and initialize a Git repository:
```bash
mkdir git-test
cd git-test
git init
```

Create a test file:
```bash
echo "# Git Test" > README.md
```

Add and commit the file:
```bash
git add README.md
git commit -m "Initial commit"
```

View commit history:
```bash
git log --oneline
```

Clean up:
```bash
cd ..
rm -rf git-test
```

### 6. Verify SSH Key Setup (for GitHub access)
Check if SSH keys exist:
```bash
ls -al ~/.ssh
```

Generate SSH key if needed:
```bash
ssh-keygen -t ed25519 -C "your.email@example.com"
```

Start SSH agent and add key:
```bash
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519
```

Copy the public key to clipboard:
#### Windows
```bash
clip < ~/.ssh/id_ed25519.pub
```

#### macOS
```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

#### Linux
```bash
cat ~/.ssh/id_ed25519.pub
# Manually copy the output
```

Add the SSH key to your GitHub account at https://github.com/settings/keys

Test SSH connection:
```bash
ssh -T git@github.com
```

Expected output: "Hi username! You've successfully authenticated..."

## Verification
After completing the above steps, you should have:
- [ ] Git 2.0 or higher installed
- [ ] Git user name and email configured
- [ ] Git default editor configured (optional)
- [ ] Git line ending settings configured
- [ ] Git functionality tested with sample repository
- [ ] SSH key setup for GitHub access (if using SSH)

## Troubleshooting
If Git is not working:

1. **Command not found**:
   - Ensure Git is in your PATH
   - Restart terminal/command prompt after installation

2. **Permission denied (publickey)**:
   - Verify SSH key is added to ssh-agent
   - Check SSH key is added to GitHub account
   - Test with `ssh -T git@github.com`

3. **Git configuration issues**:
   - Check global config: `git config --global --list`
   - Check local config: `git config --local --list`

## Next Steps
Proceed to Chunk 07: Repository Cloning to download the CRE Intelligence Platform source code.