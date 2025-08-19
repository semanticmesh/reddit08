# Installation Chunk 02: Docker Installation and Verification

## Overview
This installation chunk installs and verifies Docker and Docker Compose for Docker-based deployment of the CRE Intelligence Platform.

## Prerequisites
- System requirements verification completed (Chunk 01)
- Administrative access to install Docker

## Procedure

### 1. Install Docker Desktop (Windows/macOS)
1. Download Docker Desktop from https://www.docker.com/products/docker-desktop
2. Run the installer with default settings
3. Restart your computer if prompted

### 2. Install Docker Engine (Linux)
For Ubuntu/Debian:
```bash
# Update package index
sudo apt-get update

# Install prerequisites
sudo apt-get install apt-transport-https ca-certificates curl gnupg lsb-release

# Add Docker's official GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Add Docker repository
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Update package index again
sudo apt-get update

# Install Docker Engine
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin
```

For other Linux distributions, follow the official Docker installation guide at https://docs.docker.com/engine/install/

### 3. Verify Docker Installation
Check Docker version:
```bash
docker --version
```

Expected output: Docker version 20.10 or higher

Check Docker Compose version:
```bash
docker-compose --version
```

Expected output: docker-compose version 1.29 or higher

### 4. Start Docker Service
On Linux systems, start Docker service:
```bash
sudo systemctl start docker
sudo systemctl enable docker
```

### 5. Verify Docker Functionality
Test Docker with a simple container:
```bash
docker run hello-world
```

Expected output should show:
- "Hello from Docker!"
- Information about Docker installation

Test Docker Compose:
```bash
docker-compose --help
```

### 6. Configure Docker Permissions (Linux)
Add your user to the docker group to run Docker without sudo:
```bash
sudo usermod -aG docker $USER
```

Log out and log back in for the changes to take effect.

## Verification
After completing the above steps, you should have:
- [ ] Docker Engine 20.10 or higher installed
- [ ] Docker Compose 1.29 or higher installed
- [ ] Docker service running
- [ ] Docker functionality verified with hello-world container
- [ ] Proper permissions configured (Linux only)

## Troubleshooting
If Docker is not working:
1. Ensure Docker service is running: `sudo systemctl status docker`
2. Check Docker logs: `sudo journalctl -u docker.service`
3. Restart Docker service: `sudo systemctl restart docker`
4. Verify your user is in the docker group: `groups`

## Next Steps
Proceed to Chunk 07: Repository Cloning to download the CRE Intelligence Platform source code.