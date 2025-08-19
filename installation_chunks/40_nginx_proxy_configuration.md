# Installation Chunk 40: Nginx Proxy Configuration

## Overview
This installation chunk covers how to configure and manage the Nginx reverse proxy for the CRE Intelligence Platform, including proxy settings, security headers, SSL termination, and performance optimization.

## Prerequisites
- Docker service deployment completed (Chunk 10)
- Docker service management completed (Chunk 22)
- Security hardening completed (Chunk 26)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Understand Nginx Architecture

#### Review Nginx Configuration
```bash
# Examine Nginx configuration in docker-compose.yml
cat docker-compose.yml | grep -A 20 -B 5 "nginx"

# Expected Nginx configuration:
# nginx:
#   image: nginx:alpine
#   container_name: reddit08-nginx
#   ports:
#     - "80:80"
#     - "443:443"
#   volumes:
#     - ./nginx.conf:/etc/nginx/nginx.conf
#     - ./ssl:/etc/nginx/ssl
#   depends_on:
#     - app
#   networks:
#     - reddit08-network
```

#### Analyze Nginx Configuration File
```bash
# Review Nginx configuration file
cat nginx.conf

# Check SSL directory
ls -la ssl/
```

### 3. Verify Nginx Configuration

#### Check Nginx Environment Variables
```bash
# Verify Nginx configuration
cat nginx.conf | grep -E "(server_name|listen|proxy_pass)"

# Expected configuration elements:
# server_name localhost;
# listen 80;
# proxy_pass http://app:8000;
```

#### Test Nginx Configuration Syntax
```bash
# Test Nginx configuration syntax
docker-compose exec nginx nginx -t

# Check Nginx status
docker-compose exec nginx nginx -T

# Verify Nginx processes
docker-compose exec nginx ps aux | grep nginx
```

### 4. Test Nginx Proxy Functionality

#### Create Nginx Proxy Test Script
```bash
# Create Nginx proxy test script
nano scripts/test_nginx_proxy.py
```

Example Nginx proxy test script:
```python
#!/usr/bin/env python3
import asyncio
import requests
import time
from datetime import datetime

async def test_nginx_proxy_functionality():
    """Test Nginx proxy functionality"""
    print("Testing Nginx proxy functionality...")
    start_time = datetime.now()
    
    try:
        # 1. Test basic proxy connectivity
        print("1. Testing basic proxy connectivity...")
        response = requests.get("http://localhost/", timeout=30)
        print(f"   ✓ Proxy connectivity successful")
        print(f"   Status code: {response.status_code}")
        print(f"   Response time: {response.elapsed.total_seconds():.2f}s")
        
        # 2. Test API endpoint proxying
        print("2. Testing API endpoint proxying...")
        api_response = requests.get("http://localhost/api/v1/health", timeout=30)
        print(f"   ✓ API endpoint proxying successful")
        print(f"   Status code: {api_response.status_code}")
        if api_response.status_code == 200:
            print(f"   Response: {api_response.json()}")
        
        # 3. Test static file proxying
        print("3. Testing static file proxying...")
        # This would test static file serving if configured
        static_response = requests.get("http://localhost/static/test.txt", timeout=30)
        if static_response.status_code == 200:
            print(f"   ✓ Static file proxying successful")
        else:
            print(f"   ⚠ Static file proxying: {static_response.status_code}")
        
        # 4. Test proxy headers
        print("4. Testing proxy headers...")
        headers_response = requests.get("http://localhost/api/v1/health", timeout=30)
        headers = headers_response.headers
        
        # Check for common proxy headers
        proxy_headers = [
            'X-Forwarded-For',
            'X-Forwarded-Proto',
            'X-Forwarded-Host',
            'X-Real-IP'
        ]
        
        found_headers = [header for header in proxy_headers if header in headers]
        print(f"   ✓ Found proxy headers: {found_headers}")
        
        # 5. Test load balancing (if configured)
        print("5. Testing load balancing...")
        # Make multiple requests to test load distribution
        responses = []
        for i in range(5):
            resp = requests.get("http://localhost/api/v1/health", timeout=30)
            responses.append(resp.status_code)
            time.sleep(0.1)  # Small delay between requests
        
        unique_status_codes = set(responses)
        print(f"   ✓ Load balancing test: {len(unique_status_codes)} unique responses")
        print(f"   Status codes: {responses}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"Nginx proxy functionality test completed in {duration:.2f} seconds")
        
        return True
        
    except requests.exceptions.ConnectionError as e:
        print(f"✗ Nginx proxy connection failed: {e}")
        return False
    except requests.exceptions.Timeout as e:
        print(f"✗ Nginx proxy timeout: {e}")
        return False
    except Exception as e:
        print(f"✗ Nginx proxy test failed: {e}")
        return False

def test_proxy_security_headers():
    """Test security headers in Nginx configuration"""
    print("Testing Nginx security headers...")
    
    try:
        response = requests.get("http://localhost/", timeout=30)
        headers = response.headers
        
        # Check for security headers
        security_headers = {
            'X-Frame-Options': 'SAMEORIGIN',
            'X-Content-Type-Options': 'nosniff',
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin'
        }
        
        print("Security Headers Check:")
        for header, expected_value in security_headers.items():
            if header in headers:
                actual_value = headers[header]
                status = "✓" if actual_value == expected_value else "⚠"
                print(f"  {status} {header}: {actual_value}")
            else:
                print(f"  ✗ {header}: Not found")
        
        # Check Content-Security-Policy
        if 'Content-Security-Policy' in headers:
            csp = headers['Content-Security-Policy']
            print(f"  ✓ Content-Security-Policy: {csp[:50]}...")
        else:
            print("  ⚠ Content-Security-Policy: Not found")
        
        return True
        
    except Exception as e:
        print(f"✗ Security headers test failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_nginx_proxy_functionality())
    if success:
        test_proxy_security_headers()
    exit(0 if success else 1)
```

#### Test Proxy Performance
```bash
# Create proxy performance test script
nano scripts/test_nginx_performance.py
```

Example proxy performance test script:
```python
#!/usr/bin/env python3
import requests
import time
import statistics
from datetime import datetime

def test_nginx_performance():
    """Test Nginx proxy performance"""
    print("Testing Nginx proxy performance...")
    
    # Test parameters
    num_requests = 100
    test_url = "http://localhost/api/v1/health"
    
    try:
        # Measure request performance
        print(f"Making {num_requests} requests to {test_url}...")
        start_time = time.time()
        
        response_times = []
        status_codes = []
        
        for i in range(num_requests):
            request_start = time.time()
            try:
                response = requests.get(test_url, timeout=30)
                request_time = time.time() - request_start
                response_times.append(request_time)
                status_codes.append(response.status_code)
            except Exception as e:
                print(f"  Request {i+1} failed: {e}")
                response_times.append(30.0)  # Timeout value
                status_codes.append(0)
        
        total_time = time.time() - start_time
        print(f"✓ Completed {num_requests} requests in {total_time:.2f} seconds")
        
        # Calculate performance metrics
        if response_times:
            avg_response_time = statistics.mean(response_times)
            median_response_time = statistics.median(response_times)
            min_response_time = min(response_times)
            max_response_time = max(response_times)
            
            print(f"  Average response time: {avg_response_time*1000:.2f} ms")
            print(f"  Median response time: {median_response_time*1000:.2f} ms")
            print(f"  Min response time: {min_response_time*1000:.2f} ms")
            print(f"  Max response time: {max_response_time*1000:.2f} ms")
        
        # Analyze status codes
        successful_requests = sum(1 for code in status_codes if 200 <= code < 300)
        failed_requests = num_requests - successful_requests
        print(f"  Successful requests: {successful_requests}/{num_requests}")
        print(f"  Failed requests: {failed_requests}/{num_requests}")
        
        # Test concurrent requests
        print("Testing concurrent requests...")
        concurrent_requests = 10
        concurrent_start = time.time()
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = [executor.submit(requests.get, test_url, timeout=30) for _ in range(concurrent_requests)]
            concurrent_results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        concurrent_time = time.time() - concurrent_start
        print(f"✓ Completed {concurrent_requests} concurrent requests in {concurrent_time:.2f} seconds")
        
        print("✓ Nginx performance test completed")
        return True
        
    except Exception as e:
        print(f"✗ Nginx performance test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_nginx_performance()
    exit(0 if success else 1)
```

### 5. Monitor Nginx Proxy Status

#### Create Nginx Monitoring Script
```bash
# Create Nginx monitoring script
nano scripts/monitor_nginx.py
```

Example Nginx monitoring script:
```python
#!/usr/bin/env python3
import json
import time
import subprocess
from datetime import datetime

class NginxMonitor:
    """Monitor Nginx proxy status and performance"""
    
    def __init__(self):
        self.nginx_container = "reddit08-nginx"
    
    def get_nginx_status(self):
        """Get current Nginx status"""
        try:
            # Check if Nginx container is running
            result = subprocess.run([
                'docker', 'ps', '--filter', f'name={self.nginx_container}', '--format', '{{.Status}}'
            ], capture_output=True, text=True)
            
            is_running = 'Up' in result.stdout if result.stdout.strip() else False
            
            # Get Nginx process information
            try:
                ps_result = subprocess.run([
                    'docker', 'exec', self.nginx_container, 'ps', 'aux'
                ], capture_output=True, text=True)
                nginx_processes = ps_result.stdout.count('nginx')
            except:
                nginx_processes = 0
            
            # Get port mappings
            try:
                port_result = subprocess.run([
                    'docker', 'port', self.nginx_container
                ], capture_output=True, text=True)
                ports = port_result.stdout.strip().split('\n') if port_result.stdout.strip() else []
            except:
                ports = []
            
            return {
                'timestamp': datetime.now().isoformat(),
                'container_running': is_running,
                'nginx_processes': nginx_processes,
                'port_mappings': ports,
                'container_name': self.nginx_container
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def monitor_nginx(self, interval=30):
        """Monitor Nginx continuously"""
        print("Starting Nginx proxy monitoring...")
        print(f"Monitoring interval: {interval} seconds")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            while True:
                status = self.get_nginx_status()
                
                # Save status to log file
                with open("logs/nginx_monitoring.json", "a") as f:
                    f.write(json.dumps(status) + "\n")
                
                # Display status
                timestamp = status['timestamp']
                print(f"[{timestamp}] Nginx Proxy Status:")
                
                if 'error' in status:
                    print(f"  ✗ Error: {status['error']}")
                else:
                    print(f"  ✓ Container running: {status['container_running']}")
                    print(f"  Nginx processes: {status['nginx_processes']}")
                    if status['port_mappings']:
                        print("  Port mappings:")
                        for port in status['port_mappings']:
                            print(f"    {port}")
                    else:
                        print("  No port mappings found")
                
                print("-" * 50)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
    
    def get_nginx_metrics(self):
        """Get Nginx performance metrics"""
        try:
            # Get Nginx status information
            try:
                status_result = subprocess.run([
                    'docker', 'exec', self.nginx_container, 'nginx', '-T'
                ], capture_output=True, text=True)
                config_info = len(status_result.stdout.split('\n')) if status_result.stdout else 0
            except:
                config_info = 0
            
            # Get resource usage
            try:
                stats_result = subprocess.run([
                    'docker', 'stats', '--no-stream', '--format', 
                    '{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}', self.nginx_container
                ], capture_output=True, text=True)
                
                if stats_result.stdout.strip():
                    parts = stats_result.stdout.strip().split('\t')
                    cpu_usage = parts[0] if len(parts) > 0 else 'N/A'
                    memory_usage = parts[1] if len(parts) > 1 else 'N/A'
                    network_io = parts[2] if len(parts) > 2 else 'N/A'
                else:
                    cpu_usage = 'N/A'
                    memory_usage = 'N/A'
                    network_io = 'N/A'
            except:
                cpu_usage = 'N/A'
                memory_usage = 'N/A'
                network_io = 'N/A'
            
            return {
                'timestamp': datetime.now().isoformat(),
                'config_lines': config_info,
                'cpu_usage': cpu_usage,
                'memory_usage': memory_usage,
                'network_io': network_io
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

if __name__ == "__main__":
    monitor = NginxMonitor()
    
    # Run continuous monitoring if requested
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        monitor.monitor_nginx()
    else:
        # Run single status check
        status = monitor.get_nginx_status()
        print(json.dumps(status, indent=2))
        
        # Show metrics
        metrics = monitor.get_nginx_metrics()
        print("\nNginx Metrics:")
        print(json.dumps(metrics, indent=2))
```

### 6. Configure Nginx Optimization

#### Optimize Nginx Configuration
```bash
# Create optimized Nginx configuration
nano nginx.optimized.conf
```

Example optimized Nginx configuration:
```nginx
events {
    worker_connections 1024;
    use epoll;  # For Linux
    multi_accept on;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    keepalive_requests 100;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;
    
    # Buffer settings
    client_body_buffer_size 128k;
    client_max_body_size 10m;
    client_header_buffer_size 1k;
    large_client_header_buffers 4 4k;
    output_buffers 1 32k;
    postpone_output 1460;
    
    # Timeouts
    client_header_timeout 3m;
    client_body_timeout 3m;
    send_timeout 3m;
    
    # Cache settings
    open_file_cache max=1000 inactive=20s;
    open_file_cache_valid 30s;
    open_file_cache_min_uses 2;
    open_file_cache_errors on;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login:10m rate=1r/s;
    
    # Upstream backend
    upstream backend {
        server app:8000;
        keepalive 32;
    }
    
    # HTTP server
    server {
        listen 80;
        server_name localhost _;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:;" always;
        
        # Rate limiting
        limit_req zone=api burst=20 nodelay;
        
        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://backend/health;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_pass_header Server;
        }
        
        # API endpoints
        location /api/ {
            access_log /var/log/nginx/api.access.log;
            error_log /var/log/nginx/api.error.log;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # Buffer settings
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
            proxy_busy_buffers_size 8k;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        # Static files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
            
            # Security for static files
            location ~ \.php$ {
                deny all;
            }
        }
        
        # Root endpoint
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 30s;
            proxy_send_timeout 30s;
            proxy_read_timeout 30s;
        }
        
        # Error pages
        error_page 400 401 403 404 /errors/4xx.html;
        error_page 500 502 503 504 /errors/5xx.html;
        
        location ^~ /errors/ {
            internal;
            root /usr/share/nginx/html;
        }
    }
    
    # HTTPS server (uncomment and configure SSL for production)
    # server {
    #     listen 443 ssl http2;
    #     server_name your-domain.com;
    #
    #     # SSL configuration
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #     ssl_protocols TLSv1.2 TLSv1.3;
    #     ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    #     ssl_prefer_server_ciphers off;
    #
    #     # SSL session caching
    #     ssl_session_cache shared:SSL:10m;
    #     ssl_session_timeout 10m;
    #     ssl_session_tickets off;
    #
    #     # HSTS
    #     add_header Strict-Transport-Security "max-age=63072000" always;
    #
    #     # Include the same location blocks as HTTP server
    #     # ... location blocks ...
    # }
}
```

#### Implement Proxy Health Checks
```bash
# Create proxy health check script
nano scripts/health_check_nginx.py
```

Example proxy health check script:
```python
#!/usr/bin/env python3
import sys
import requests
import subprocess
from datetime import datetime

def health_check_nginx():
    """Perform health check on Nginx proxy"""
    print("Performing Nginx proxy health check...")
    
    try:
        # 1. Check Nginx container status
        print("1. Checking Nginx container status...")
        result = subprocess.run([
            'docker', 'ps', '--filter', 'name=reddit08-nginx', '--format', '{{.Status}}'
        ], capture_output=True, text=True)
        
        if 'Up' in result.stdout:
            print("   ✓ Nginx container is running")
        else:
            print("   ✗ Nginx container is not running")
            return False
        
        # 2. Test basic connectivity
        print("2. Testing basic connectivity...")
        try:
            response = requests.get("http://localhost/", timeout=10)
            print(f"   ✓ Basic connectivity successful")
            print(f"   Status code: {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("   ✗ Basic connectivity failed - connection refused")
            return False
        except requests.exceptions.Timeout:
            print("   ✗ Basic connectivity failed - timeout")
            return False
        
        # 3. Test API endpoint
        print("3. Testing API endpoint...")
        try:
            api_response = requests.get("http://localhost/api/v1/health", timeout=10)
            print(f"   ✓ API endpoint accessible")
            print(f"   Status code: {api_response.status_code}")
            if api_response.status_code == 200:
                print(f"   Response: {api_response.json()}")
        except Exception as e:
            print(f"   ⚠ API endpoint test: {e}")
        
        # 4. Check security headers
        print("4. Checking security headers...")
        try:
            headers_response = requests.get("http://localhost/", timeout=10)
            headers = headers_response.headers
            
            required_headers = [
                'X-Frame-Options',
                'X-Content-Type-Options',
                'X-XSS-Protection'
            ]
            
            missing_headers = [header for header in required_headers if header not in headers]
            if missing_headers:
                print(f"   ⚠ Missing security headers: {missing_headers}")
            else:
                print("   ✓ All required security headers present")
        except Exception as e:
            print(f"   ⚠ Security headers check: {e}")
        
        # 5. Test proxy configuration
        print("5. Testing proxy configuration...")
        try:
            # Test Nginx configuration syntax
            config_result = subprocess.run([
                'docker', 'exec', 'reddit08-nginx', 'nginx', '-t'
            ], capture_output=True, text=True)
            
            if config_result.returncode == 0:
                print("   ✓ Nginx configuration syntax is valid")
            else:
                print("   ✗ Nginx configuration syntax error")
                print(f"   Error: {config_result.stderr}")
                return False
        except Exception as e:
            print(f"   ⚠ Configuration test: {e}")
        
        print("✓ All Nginx proxy health checks passed")
        return True
        
    except Exception as e:
        print(f"✗ Nginx health check failed: {e}")
        return False

def detailed_health_check():
    """Perform detailed health check"""
    print("Performing detailed Nginx health check...")
    
    try:
        # Get detailed Nginx information
        print("Detailed Nginx Information:")
        
        # Configuration information
        print("  Configuration:")
        try:
            config_result = subprocess.run([
                'docker', 'exec', 'reddit08-nginx', 'nginx', '-T'
            ], capture_output=True, text=True)
            
            if config_result.stdout:
                config_lines = len(config_result.stdout.split('\n'))
                print(f"    Configuration lines: {config_lines}")
        except Exception as e:
            print(f"    Configuration check failed: {e}")
        
        # Process information
        print("  Processes:")
        try:
            ps_result = subprocess.run([
                'docker', 'exec', 'reddit08-nginx', 'ps', 'aux'
            ], capture_output=True, text=True)
            
            nginx_processes = ps_result.stdout.count('nginx')
            print(f"    Nginx processes: {nginx_processes}")
            
            if nginx_processes > 0:
                print("    Process details:")
                for line in ps_result.stdout.split('\n'):
                    if 'nginx' in line:
                        print(f"      {line}")
        except Exception as e:
            print(f"    Process check failed: {e}")
        
        # Resource usage
        print("  Resource Usage:")
        try:
            stats_result = subprocess.run([
                'docker', 'stats', '--no-stream', '--format', 
                'CPU: {{.CPUPerc}}, Memory: {{.MemUsage}}, Network: {{.NetIO}}', 
                'reddit08-nginx'
            ], capture_output=True, text=True)
            
            if stats_result.stdout.strip():
                print(f"    {stats_result.stdout.strip()}")
        except Exception as e:
            print(f"    Resource usage check failed: {e}")
        
        # Port information
        print("  Port Information:")
        try:
            port_result = subprocess.run([
                'docker', 'port', 'reddit08-nginx'
            ], capture_output=True, text=True)
            
            if port_result.stdout.strip():
                print("    Port mappings:")
                for line in port_result.stdout.strip().split('\n'):
                    print(f"      {line}")
            else:
                print("    No port mappings found")
        except Exception as e:
            print(f"    Port check failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"✗ Detailed health check failed: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--detailed":
        success = detailed_health_check()
    else:
        success = health_check_nginx()
    
    exit(0 if success else 1)
```

### 7. Troubleshoot Nginx Proxy Issues

#### Diagnose Common Nginx Issues
```bash
# Check Nginx logs
docker-compose logs nginx

# Monitor for common errors
docker-compose logs nginx | grep -E "(error|failed|exception|timeout)"

# Check for configuration errors
docker-compose logs nginx | grep -E "(config|syntax|invalid)"

# Monitor for proxy errors
docker-compose logs nginx | grep -E "(proxy|upstream|502|503|504)"

# Check for security issues
docker-compose logs nginx | grep -E "(denied|forbidden|unauthorized)"
```

#### Resolve Nginx Proxy Issues
```bash
# Restart Nginx
docker-compose restart nginx

# Test configuration syntax
docker-compose exec nginx nginx -t

# Reload Nginx configuration
docker-compose exec nginx nginx -s reload

# Check Nginx processes
docker-compose exec nginx ps aux | grep nginx

# Verify port mappings
docker-compose port nginx 80
docker-compose port nginx 443

# Check backend connectivity
docker-compose exec nginx curl -f http://app:8000/health

# Test proxy configuration
docker-compose exec nginx curl -H "Host: localhost" http://localhost/
```

### 8. Configure Advanced Proxy Features

#### Implement Load Balancing
```bash
# Update Nginx configuration for load balancing
nano nginx.loadbalancer.conf
```

Example load balancing configuration:
```nginx
http {
    # Upstream backend with multiple servers
    upstream backend {
        # Load balancing methods:
        # least_conn;  # Least connections
        # ip_hash;     # IP hash for session persistence
        # fair;        # Fair balancing (requires nginx-upstream-fair module)
        
        server app1:8000 weight=3 max_fails=3 fail_timeout=30s;
        server app2:8000 weight=2 max_fails=3 fail_timeout=30s;
        server app3:8000 weight=1 max_fails=3 fail_timeout=30s;
        
        # Health checks
        keepalive 32;
    }
    
    # HTTP server with load balancing
    server {
        listen 80;
        server_name localhost;
        
        # Proxy to load balanced backend
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 5s;
            proxy_send_timeout 10s;
            proxy_read_timeout 10s;
            
            # Buffer settings
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://backend/health;
            proxy_set_header Host $host;
        }
    }
}
```

#### Implement Caching
```bash
# Create caching configuration
nano nginx.caching.conf
```

Example caching configuration:
```nginx
http {
    # Cache settings
    proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=my_cache:10m max_size=10g 
                     inactive=60m use_temp_path=off;
    
    # HTTP server with caching
    server {
        listen 80;
        server_name localhost;
        
        # Cache API responses
        location /api/ {
            proxy_cache my_cache;
            proxy_cache_valid 200 5m;  # Cache 200 responses for 5 minutes
            proxy_cache_valid 404 1m;   # Cache 404 responses for 1 minute
            proxy_cache_use_stale error timeout updating http_500 http_502 http_503 http_504;
            proxy_cache_lock on;
            
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Add cache headers
            add_header X-Cache-Status $upstream_cache_status;
        }
        
        # Cache static files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }
    }
}
```

### 9. Verify Nginx Proxy Setup
```bash
# Test final Nginx proxy setup
python scripts/test_nginx_proxy.py

# Run health check
python scripts/health_check_nginx.py

# Check Nginx status
docker-compose exec nginx nginx -t

# Monitor proxy performance
python scripts/monitor_nginx.py --test

# Verify proxy functionality
curl -f http://localhost/
curl -f http://localhost/api/v1/health
curl -f http://localhost/health
```

## Verification
After completing the above steps, you should be able to:
- [ ] Understand Nginx proxy architecture and configuration
- [ ] Verify Nginx proxy configuration and connectivity
- [ ] Test Nginx proxy functionality and performance
- [ ] Monitor Nginx proxy status and metrics
- [ ] Configure Nginx optimization and security
- [ ] Implement proxy health checks and monitoring
- [ ] Troubleshoot Nginx proxy issues and errors
- [ ] Configure advanced proxy features like load balancing
- [ ] Verify Nginx proxy setup and resolution

## Common Nginx Proxy Issues and Solutions

### Connectivity Issues
- **"502 Bad Gateway"**: Check backend service connectivity and configuration
- **"503 Service Unavailable"**: Verify backend service is running and responsive
- **"504 Gateway Timeout"**: Increase proxy timeout values or check backend performance
- **"Connection refused"**: Verify port mappings and service availability

### Configuration Issues
- **"Configuration syntax error"**: Check Nginx configuration syntax with `nginx -t`
- **"Invalid proxy pass"**: Verify upstream server configuration and connectivity
- **"Missing headers"**: Check proxy header configuration
- **"SSL configuration error"**: Verify SSL certificate and key files

### Performance Issues
- **"Slow response times"**: Optimize buffer settings and timeout values
- **"High memory usage"**: Configure proper worker processes and connections
- **"Connection limits exceeded"**: Increase worker connections and system limits
- **"Cache misses"**: Optimize cache configuration and size

## Troubleshooting Checklist

### Quick Fixes
- [ ] Check Nginx logs for errors
- [ ] Verify backend service connectivity
- [ ] Test Nginx configuration syntax
- [ ] Restart Nginx service
- [ ] Check port mappings and firewall
- [ ] Review proxy header configuration

### Advanced Diagnostics
- [ ] Implement detailed proxy monitoring
- [ ] Analyze request processing patterns
- [ ] Optimize proxy configuration and buffers
- [ ] Configure load balancing and caching
- [ ] Implement comprehensive error handling
- [ ] Set up proper logging and alerting

## Next Steps
Proceed to Chunk 41: SSL Certificate Setup to learn how to configure and manage SSL certificates for secure HTTPS connections in the CRE Intelligence Platform.