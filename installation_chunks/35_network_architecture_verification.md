# Installation Chunk 35: Network Architecture Verification

## Overview
This installation chunk covers how to verify and optimize the network architecture of the CRE Intelligence Platform, including container networking, external connectivity, security configurations, and performance optimization.

## Prerequisites
- Docker service deployment completed (Chunk 10)
- Container relationship verification completed (Chunk 34)
- Security hardening completed (Chunk 26)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Understand Network Architecture

#### Review Docker Network Configuration
```bash
# Examine docker-compose.yml for network configuration
cat docker-compose.yml | grep -A 10 -B 5 "networks"

# Expected network configuration:
# networks:
#   reddit08-network:
#     driver: bridge
```

#### Analyze Network Architecture Documentation
```bash
# Review network architecture in documentation
cat DEPLOYMENT_ARCHITECTURE.md | grep -A 30 "Network Architecture"

# Expected architecture:
# - Internal network for container communication
# - External access through nginx proxy
# - Port mappings for external services
# - Network isolation and security
```

### 3. Verify Current Network Configuration

#### Check Docker Networks
```bash
# List all Docker networks
docker network ls

# Inspect the main network
docker network inspect reddit08-network

# Check network configuration details
docker network inspect reddit08-network | grep -A 20 "Config"

# Verify network driver and options
docker network inspect reddit08-network | grep -A 10 "Driver"
```

#### Examine Container Network Attachments
```bash
# Check which containers are attached to the network
docker network inspect reddit08-network | grep -A 30 "Containers"

# Verify container IP addresses
docker inspect reddit08-cre-platform | grep -A 5 "Networks"
docker inspect reddit08-postgres | grep -A 5 "Networks"
docker inspect reddit08-redis | grep -A 5 "Networks"
docker inspect reddit08-celery | grep -A 5 "Networks"
docker inspect reddit08-celery-beat | grep -A 5 "Networks"
docker inspect reddit08-nginx | grep -A 5 "Networks"
```

### 4. Test Network Connectivity

#### Test Internal Network Communication
```bash
# Test container-to-container communication
docker-compose exec app ping -c 3 postgres
docker-compose exec app ping -c 3 redis
docker-compose exec celery-worker ping -c 3 postgres
docker-compose exec celery-worker ping -c 3 redis
docker-compose exec nginx ping -c 3 app

# Test DNS resolution within containers
docker-compose exec app nslookup postgres
docker-compose exec app nslookup redis
docker-compose exec celery-worker nslookup postgres
docker-compose exec celery-worker nslookup redis

# Test service port connectivity
docker-compose exec app telnet postgres 5432
docker-compose exec app telnet redis 6379
docker-compose exec celery-worker telnet postgres 5432
docker-compose exec celery-worker telnet redis 6379
```

#### Test External Network Access
```bash
# Test external connectivity from containers
docker-compose exec app ping -c 3 google.com
docker-compose exec postgres ping -c 3 google.com
docker-compose exec redis ping -c 3 google.com

# Test external API access
docker-compose exec app curl -I https://api.openai.com
docker-compose exec app curl -I https://oauth.reddit.com
docker-compose exec app curl -I https://newsapi.org

# Check DNS resolution for external services
docker-compose exec app nslookup api.openai.com
docker-compose exec app nslookup oauth.reddit.com
```

### 5. Verify Port Configuration and Security

#### Check Port Mappings
```bash
# List port mappings for all containers
docker-compose ps --format "table {{.Name}}\t{{.Ports}}"

# Expected port mappings:
# reddit08-cre-platform: 8000/tcp
# reddit08-postgres: 5432/tcp
# reddit08-redis: 6379/tcp
# reddit08-nginx: 80/tcp, 443/tcp

# Check specific container ports
docker port reddit08-cre-platform
docker port reddit08-postgres
docker port reddit08-redis
docker port reddit08-nginx
```

#### Test Port Accessibility
```bash
# Test external port accessibility
netstat -tuln | grep -E "(8000|5432|6379|80|443)"

# Test port connectivity from localhost
curl -f http://localhost:8000/health
curl -f http://localhost:80/health
telnet localhost 5432
telnet localhost 6379

# Check firewall rules
sudo ufw status
sudo iptables -L
```

### 6. Implement Network Security

#### Configure Network Isolation
```bash
# Update docker-compose.yml for enhanced network security
nano docker-compose.yml
```

Example enhanced network configuration:
```yaml
services:
  app:
    # ... other configuration
    networks:
      reddit08-network:
        aliases:
          - cre-platform
    expose:
      - "8000"
    # Remove direct port mapping for internal services
    
  postgres:
    # ... other configuration
    networks:
      reddit08-network:
        aliases:
          - database
    expose:
      - "5432"
    # Remove external port mapping
    
  redis:
    # ... other configuration
    networks:
      reddit08-network:
        aliases:
          - cache
    expose:
      - "6379"
    # Remove external port mapping
    
  nginx:
    # ... other configuration
    networks:
      reddit08-network:
        aliases:
          - proxy
    ports:
      - "80:80"
      - "443:443"
    # Only expose necessary external ports

networks:
  reddit08-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1
    driver_opts:
      com.docker.network.bridge.name: br-reddit08
```

#### Implement Network Security Rules
```bash
# Create network security script
nano scripts/network_security.sh
```

Example network security script:
```bash
#!/bin/bash

# Network security configuration for CRE Intelligence Platform

echo "Configuring network security..."

# Create custom network with specific subnet
docker network create --driver bridge \
  --subnet=172.20.0.0/16 \
  --gateway=172.20.0.1 \
  --opt com.docker.network.bridge.name=br-reddit08 \
  reddit08-secure-network

# Configure firewall rules
if command -v ufw &> /dev/null; then
    echo "Configuring UFW rules..."
    
    # Allow necessary ports
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS
    
    # Deny unnecessary ports
    ufw deny 5432/tcp   # PostgreSQL (internal only)
    ufw deny 6379/tcp   # Redis (internal only)
    ufw deny 8000/tcp   # App direct access (internal only)
    
    # Enable firewall
    echo "y" | ufw enable
fi

# Configure iptables rules (if UFW not available)
if command -v iptables &> /dev/null; then
    echo "Configuring iptables rules..."
    
    # Allow established connections
    iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT
    
    # Allow loopback
    iptables -A INPUT -i lo -j ACCEPT
    
    # Allow SSH
    iptables -A INPUT -p tcp --dport 22 -j ACCEPT
    
    # Allow HTTP and HTTPS
    iptables -A INPUT -p tcp --dport 80 -j ACCEPT
    iptables -A INPUT -p tcp --dport 443 -j ACCEPT
    
    # Deny internal ports from external access
    iptables -A INPUT -p tcp --dport 5432 -j DROP
    iptables -A INPUT -p tcp --dport 6379 -j DROP
    iptables -A INPUT -p tcp --dport 8000 -j DROP
    
    # Save iptables rules
    iptables-save > /etc/iptables/rules.v4
fi

echo "Network security configuration completed"
```

### 7. Monitor Network Performance

#### Create Network Monitoring Script
```bash
# Create network monitoring script
nano scripts/monitor_network.py
```

Example network monitoring script:
```python
#!/usr/bin/env python3
import subprocess
import json
import time
from datetime import datetime
import psutil

def monitor_container_networks():
    """Monitor container network usage"""
    containers = [
        "reddit08-cre-platform",
        "reddit08-postgres",
        "reddit08-redis",
        "reddit08-celery",
        "reddit08-celery-beat",
        "reddit08-nginx"
    ]
    
    network_stats = {}
    
    for container in containers:
        try:
            # Get container network stats
            result = subprocess.run(
                ["docker", "stats", "--no-stream", "--format", 
                 "{{.Name}}\t{{.NetIO}}\t{{.PIDs}}", container],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.stdout.strip():
                parts = result.stdout.strip().split('\t')
                if len(parts) >= 2:
                    network_stats[container] = {
                        "network_io": parts[1],
                        "pids": parts[2] if len(parts) > 2 else "N/A"
                    }
        except Exception as e:
            network_stats[container] = {"error": str(e)}
    
    return network_stats

def monitor_host_network():
    """Monitor host network usage"""
    net_io = psutil.net_io_counters()
    return {
        "bytes_sent": net_io.bytes_sent,
        "bytes_recv": net_io.bytes_recv,
        "packets_sent": net_io.packets_sent,
        "packets_recv": net_io.packets_recv,
        "errin": net_io.errin,
        "errout": net_io.errout,
        "dropin": net_io.dropin,
        "dropout": net_io.dropout
    }

def monitor_network_performance():
    """Monitor network performance continuously"""
    print("Starting network performance monitoring...")
    
    while True:
        timestamp = datetime.now().isoformat()
        
        # Monitor container networks
        container_stats = monitor_container_networks()
        
        # Monitor host network
        host_stats = monitor_host_network()
        
        # Save monitoring data
        monitoring_data = {
            "timestamp": timestamp,
            "container_networks": container_stats,
            "host_network": host_stats
        }
        
        with open("logs/network_monitoring.json", "a") as f:
            f.write(json.dumps(monitoring_data) + "\n")
        
        # Display summary
        print(f"[{timestamp}] Network monitoring completed")
        for container, stats in container_stats.items():
            if "error" not in stats:
                print(f"  {container}: {stats.get('network_io', 'N/A')}")
        
        # Wait before next check
        time.sleep(60)

if __name__ == "__main__":
    monitor_network_performance()
```

### 8. Troubleshoot Network Issues

#### Diagnose Network Problems
```bash
# Check for network connectivity issues
docker-compose logs --since="1h" | grep -E "(network|connection|timeout|refused)"

# Monitor network errors
dmesg | grep -E "(network|eth|bridge)"

# Check system network configuration
ip addr show
ip route show

# Test DNS resolution
docker-compose exec app cat /etc/resolv.conf
docker-compose exec app dig google.com
```

#### Resolve Network Issues
```bash
# Restart Docker networking
sudo systemctl restart docker

# Recreate container network
docker-compose down
docker network prune -f
docker-compose up -d

# Check for network conflicts
docker network ls | grep -E "(reddit08|bridge)"

# Verify network configuration
docker network inspect reddit08-network
```

### 9. Optimize Network Performance

#### Configure Network Optimization
```bash
# Optimize Docker network performance
# Add to docker-compose.yml:
# networks:
#   reddit08-network:
#     driver: bridge
#     driver_opts:
#       com.docker.network.driver.mtu: 1500
#       com.docker.network.bridge.enable_icc: "true"
#       com.docker.network.bridge.enable_ip_masquerade: "true"
```

#### Implement Connection Optimization
```bash
# Optimize application network connections
# Edit src/mcp/fastapi_app/network/optimized_connections.py

import asyncio
import aiohttp
from typing import Optional

class OptimizedNetworkClient:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        # Configure connection pooling
        connector = aiohttp.TCPConnector(
            limit=100,  # Max connections
            limit_per_host=30,  # Max connections per host
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30  # Keep-alive timeout
        )
        
        self.session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def fetch(self, url: str) -> str:
        if not self.session:
            raise RuntimeError("Session not initialized")
        
        async with self.session.get(url) as response:
            return await response.text()
```

### 10. Verify Network Architecture Resolution
```bash
# Test final network configuration
python scripts/monitor_network.py --test

# Verify network security
sudo ufw status
iptables -L | grep -E "(5432|6379|8000)"

# Test container network isolation
docker-compose exec app nc -zv postgres 5432
docker-compose exec app nc -zv redis 6379

# Verify external access control
nmap -p 5432,6379,8000 localhost  # Should show filtered/closed

# Test application network performance
ab -n 1000 -c 10 http://localhost:8000/health
```

## Verification
After completing the above steps, you should be able to:
- [ ] Understand network architecture and configuration
- [ ] Verify current network configuration and connectivity
- [ ] Test internal and external network communication
- [ ] Verify port configuration and security
- [ ] Implement network security measures
- [ ] Monitor network performance and usage
- [ ] Troubleshoot network issues and problems
- [ ] Optimize network performance and configuration
- [ ] Verify network architecture resolution

## Common Network Architecture Issues and Solutions

### Connectivity Issues
- **"Connection timeout"**: Check network configuration and firewall rules
- **"Host not found"**: Verify DNS resolution and network connectivity
- **"Network unreachable"**: Check network routes and gateway configuration
- **"Port refused"**: Verify service is running and port is accessible

### Security Issues
- **"Unauthorized access"**: Implement proper network isolation
- **"Port scanning detected"**: Configure firewall rules and access controls
- **"Network exposure"**: Remove unnecessary port mappings
- **"DNS hijacking"**: Use secure DNS configuration

### Performance Issues
- **"Slow network"**: Optimize network configuration and connection pooling
- **"High latency"**: Check network routes and bandwidth
- **"Packet loss"**: Monitor network errors and connectivity
- **"Connection timeouts"**: Increase timeout values and optimize connections

## Troubleshooting Checklist

### Quick Fixes
- [ ] Verify network configuration: `docker network inspect`
- [ ] Check port mappings: `docker-compose ps --format`
- [ ] Test connectivity: `docker-compose exec ping`
- [ ] Review firewall rules: `ufw status`
- [ ] Restart networking: `systemctl restart docker`
- [ ] Recreate network: `docker-compose down && up`

### Advanced Diagnostics
- [ ] Monitor network performance continuously
- [ ] Analyze network traffic patterns
- [ ] Check for network bottlenecks
- [ ] Implement network security monitoring
- [ ] Test failover scenarios
- [ ] Optimize network configuration

## Next Steps
Proceed to Chunk 36: Data Flow Verification to learn how to verify and optimize the data flow within the CRE Intelligence Platform.