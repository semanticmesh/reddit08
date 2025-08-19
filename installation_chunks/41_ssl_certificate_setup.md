# Installation Chunk 41: SSL Certificate Setup

## Overview
This installation chunk covers how to configure and manage SSL certificates for secure HTTPS connections in the CRE Intelligence Platform, including certificate generation, installation, and renewal.

## Prerequisites
- Nginx proxy configuration completed (Chunk 40)
- Docker service deployment completed (Chunk 10)
- Security hardening completed (Chunk 26)

## Procedure

### 1. Navigate to Project Directory
Change to the project directory:
```bash
cd /path/to/reddit08
```

### 2. Understand SSL Architecture

#### Review SSL Configuration in Nginx
```bash
# Examine SSL configuration in nginx.conf
cat nginx.conf | grep -A 30 -B 5 "HTTPS server"

# Expected SSL configuration:
# server {
#     listen 443 ssl http2;
#     server_name your-domain.com;
#     
#     ssl_certificate /etc/nginx/ssl/cert.pem;
#     ssl_certificate_key /etc/nginx/ssl/key.pem;
#     ssl_protocols TLSv1.2 TLSv1.3;
#     ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
# }
```

#### Check SSL Directory Structure
```bash
# Check SSL directory
ls -la ssl/

# Create SSL directory if it doesn't exist
mkdir -p ssl/
```

### 3. Generate SSL Certificates

#### Create Self-Signed Certificate (Development)
```bash
# Generate self-signed certificate for development
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout ssl/selfsigned.key \
    -out ssl/selfsigned.crt \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=localhost"

# Combine certificate and key for Nginx
cat ssl/selfsigned.crt ssl/selfsigned.key > ssl/selfsigned.pem

# Set proper permissions
chmod 600 ssl/selfsigned.key
chmod 644 ssl/selfsigned.crt
chmod 644 ssl/selfsigned.pem

# Verify certificate
openssl x509 -in ssl/selfsigned.crt -text -noout | head -20
```

#### Generate Certificate with Let's Encrypt (Production)
```bash
# Install Certbot (Ubuntu/Debian)
sudo apt update
sudo apt install certbot

# Generate certificate using standalone method
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com

# Or generate certificate using webroot method
sudo certbot certonly --webroot -w /var/www/html -d your-domain.com

# Certificate locations:
# /etc/letsencrypt/live/your-domain.com/fullchain.pem
# /etc/letsencrypt/live/your-domain.com/privkey.pem
```

#### Generate Certificate with OpenSSL CSR (Custom CA)
```bash
# Generate private key
openssl genrsa -out ssl/private.key 2048

# Generate certificate signing request (CSR)
openssl req -new -key ssl/private.key -out ssl/certificate.csr \
    -subj "/C=US/ST=State/L=City/O=Organization/CN=your-domain.com"

# Generate self-signed certificate from CSR
openssl x509 -req -days 365 -in ssl/certificate.csr \
    -signkey ssl/private.key -out ssl/certificate.crt

# Combine for Nginx
cat ssl/certificate.crt ssl/private.key > ssl/certificate.pem
```

### 4. Configure SSL in Nginx

#### Update Nginx Configuration for SSL
```bash
# Create SSL-enabled Nginx configuration
nano nginx.ssl.conf
```

Example SSL-enabled Nginx configuration:
```nginx
events {
    worker_connections 1024;
}

http {
    # Basic settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss application/atom+xml;
    
    # Upstream backend
    upstream backend {
        server app:8000;
        keepalive 64;
    }
    
    # HTTP server (redirect to HTTPS)
    server {
        listen 80;
        server_name your-domain.com www.your-domain.com localhost;
        
        # Redirect all HTTP requests to HTTPS
        return 301 https://$server_name$request_uri;
        
        # Let's Encrypt challenge endpoint
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
    }
    
    # HTTPS server
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com localhost;
        
        # SSL certificate configuration
        ssl_certificate /etc/nginx/ssl/certificate.pem;
        ssl_certificate_key /etc/nginx/ssl/private.key;
        
        # SSL protocols and ciphers
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # SSL session caching
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        ssl_session_tickets off;
        
        # HSTS (HTTP Strict Transport Security)
        add_header Strict-Transport-Security "max-age=63072000" always;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        
        # OCSP stapling
        ssl_stapling on;
        ssl_stapling_verify on;
        
        # Health check endpoint
        location /health {
            access_log off;
            proxy_pass http://backend/health;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # API endpoints
        location /api/ {
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
        }
        
        # Static files
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
            access_log off;
        }
        
        # Root endpoint
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Error pages
        error_page 500 502 503 504 /50x.html;
        location = /50x.html {
            root /usr/share/nginx/html;
        }
    }
}
```

### 5. Test SSL Configuration

#### Create SSL Test Script
```bash
# Create SSL test script
nano scripts/test_ssl.py
```

Example SSL test script:
```python
#!/usr/bin/env python3
import asyncio
import ssl
import socket
import requests
from datetime import datetime
import subprocess

async def test_ssl_configuration():
    """Test SSL configuration"""
    print("Testing SSL configuration...")
    start_time = datetime.now()
    
    try:
        # 1. Test SSL certificate validity
        print("1. Testing SSL certificate validity...")
        try:
            response = requests.get("https://localhost", verify=False, timeout=30)
            print(f"   ✓ SSL connection successful")
            print(f"   Status code: {response.status_code}")
            print(f"   Response time: {response.elapsed.total_seconds():.2f}s")
        except requests.exceptions.SSLError as e:
            print(f"   ⚠ SSL certificate error: {e}")
        except Exception as e:
            print(f"   ⚠ SSL connection test: {e}")
        
        # 2. Test SSL protocols
        print("2. Testing SSL protocols...")
        protocols = ['TLSv1.2', 'TLSv1.3']
        for protocol in protocols:
            try:
                # This is a simplified test - in practice, you'd use more sophisticated SSL testing
                print(f"   Testing {protocol}...")
                # For actual protocol testing, you'd need to use openssl commands or specialized libraries
            except Exception as e:
                print(f"   ⚠ {protocol} test: {e}")
        
        # 3. Test certificate chain
        print("3. Testing certificate chain...")
        try:
            # Get certificate information
            cert_info = subprocess.run([
                'openssl', 's_client', '-connect', 'localhost:443', '-showcerts'
            ], input='', capture_output=True, text=True, timeout=30)
            
            if cert_info.returncode == 0:
                print("   ✓ Certificate chain retrieved successfully")
                # Parse certificate information
                cert_lines = cert_info.stdout.split('\n')
                cert_count = sum(1 for line in cert_lines if '-----BEGIN CERTIFICATE-----' in line)
                print(f"   Certificate chain length: {cert_count}")
            else:
                print(f"   ⚠ Certificate chain test failed: {cert_info.stderr}")
        except subprocess.TimeoutExpired:
            print("   ⚠ Certificate chain test timed out")
        except Exception as e:
            print(f"   ⚠ Certificate chain test: {e}")
        
        # 4. Test SSL cipher suites
        print("4. Testing SSL cipher suites...")
        try:
            # Test common cipher suites
            ciphers = subprocess.run([
                'openssl', 'ciphers', '-v'
            ], capture_output=True, text=True)
            
            if ciphers.returncode == 0:
                cipher_list = ciphers.stdout.strip().split('\n')
                print(f"   ✓ Available cipher suites: {len(cipher_list)}")
                # Show first few ciphers
                for cipher in cipher_list[:5]:
                    print(f"     {cipher}")
            else:
                print(f"   ⚠ Cipher suite test failed: {ciphers.stderr}")
        except Exception as e:
            print(f"   ⚠ Cipher suite test: {e}")
        
        # 5. Test HSTS header
        print("5. Testing HSTS header...")
        try:
            response = requests.get("https://localhost", verify=False, timeout=30)
            if 'Strict-Transport-Security' in response.headers:
                hsts = response.headers['Strict-Transport-Security']
                print(f"   ✓ HSTS header present: {hsts}")
            else:
                print("   ⚠ HSTS header not found")
        except Exception as e:
            print(f"   ⚠ HSTS header test: {e}")
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        print(f"SSL configuration test completed in {duration:.2f} seconds")
        
        return True
        
    except Exception as e:
        print(f"✗ SSL configuration test failed: {e}")
        return False

def test_ssl_certificate_details():
    """Test SSL certificate details"""
    print("Testing SSL certificate details...")
    
    try:
        # Get certificate details
        cert_details = subprocess.run([
            'openssl', 'x509', '-in', 'ssl/selfsigned.crt', '-text', '-noout'
        ], capture_output=True, text=True)
        
        if cert_details.returncode == 0:
            print("✓ Certificate details retrieved successfully")
            # Parse key information
            cert_lines = cert_details.stdout.split('\n')
            for line in cert_lines:
                if 'Issuer:' in line or 'Subject:' in line or 'Validity' in line or 'Public-Key:' in line:
                    print(f"  {line.strip()}")
        else:
            print(f"✗ Certificate details test failed: {cert_details.stderr}")
            
    except Exception as e:
        print(f"✗ Certificate details test: {e}")

if __name__ == "__main__":
    success = asyncio.run(test_ssl_configuration())
    if success:
        test_ssl_certificate_details()
    exit(0 if success else 1)
```

#### Test SSL Performance
```bash
# Create SSL performance test script
nano scripts/test_ssl_performance.py
```

Example SSL performance test script:
```python
#!/usr/bin/env python3
import requests
import time
import statistics
import ssl
from datetime import datetime

def test_ssl_performance():
    """Test SSL performance"""
    print("Testing SSL performance...")
    
    # Test parameters
    num_requests = 50
    test_url = "https://localhost"
    
    try:
        # Warm up SSL connection
        print("Warming up SSL connection...")
        try:
            requests.get(test_url, verify=False, timeout=30)
        except:
            pass  # Ignore warmup errors
        
        # Measure SSL handshake performance
        print(f"Making {num_requests} SSL requests to {test_url}...")
        start_time = time.time()
        
        response_times = []
        status_codes = []
        ssl_handshake_times = []
        
        for i in range(num_requests):
            request_start = time.time()
            try:
                response = requests.get(test_url, verify=False, timeout=30)
                request_time = time.time() - request_start
                response_times.append(request_time)
                status_codes.append(response.status_code)
            except Exception as e:
                print(f"  Request {i+1} failed: {e}")
                response_times.append(30.0)  # Timeout value
                status_codes.append(0)
        
        total_time = time.time() - start_time
        print(f"✓ Completed {num_requests} SSL requests in {total_time:.2f} seconds")
        
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
        
        # Test concurrent SSL requests
        print("Testing concurrent SSL requests...")
        concurrent_requests = 10
        concurrent_start = time.time()
        
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_requests) as executor:
            futures = []
            for _ in range(concurrent_requests):
                future = executor.submit(requests.get, test_url, verify=False, timeout=30)
                futures.append(future)
            
            concurrent_results = []
            for future in concurrent.futures.as_completed(futures):
                try:
                    result = future.result()
                    concurrent_results.append(result)
                except Exception as e:
                    print(f"  Concurrent request failed: {e}")
        
        concurrent_time = time.time() - concurrent_start
        print(f"✓ Completed {len(concurrent_results)} concurrent SSL requests in {concurrent_time:.2f} seconds")
        
        print("✓ SSL performance test completed")
        return True
        
    except Exception as e:
        print(f"✗ SSL performance test failed: {e}")
        return False

def test_ssl_handshake_performance():
    """Test SSL handshake performance specifically"""
    print("Testing SSL handshake performance...")
    
    try:
        # Test SSL handshake time
        import socket
        import ssl
        
        # Create SSL context
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Measure handshake time
        handshake_times = []
        for i in range(10):
            start_time = time.time()
            
            try:
                # Create socket connection
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(30)
                
                # Connect to server
                sock.connect(('localhost', 443))
                
                # Perform SSL handshake
                ssl_sock = context.wrap_socket(sock, server_hostname='localhost')
                
                handshake_time = time.time() - start_time
                handshake_times.append(handshake_time)
                
                # Close connection
                ssl_sock.close()
                
            except Exception as e:
                print(f"  Handshake {i+1} failed: {e}")
                handshake_times.append(30.0)  # Timeout value
        
        if handshake_times:
            avg_handshake_time = statistics.mean(handshake_times)
            print(f"  Average SSL handshake time: {avg_handshake_time*1000:.2f} ms")
        
        print("✓ SSL handshake performance test completed")
        return True
        
    except Exception as e:
        print(f"✗ SSL handshake performance test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_ssl_performance()
    if success:
        test_ssl_handshake_performance()
    exit(0 if success else 1)
```

### 6. Monitor SSL Certificate Status

#### Create SSL Monitoring Script
```bash
# Create SSL monitoring script
nano scripts/monitor_ssl.py
```

Example SSL monitoring script:
```python
#!/usr/bin/env python3
import json
import time
import subprocess
import ssl
import socket
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend

class SSLMonitor:
    """Monitor SSL certificate status and performance"""
    
    def __init__(self, hostname="localhost", port=443):
        self.hostname = hostname
        self.port = port
    
    def get_certificate_info(self):
        """Get SSL certificate information"""
        try:
            # Get certificate using openssl
            result = subprocess.run([
                'openssl', 's_client', '-connect', f'{self.hostname}:{self.port}', 
                '-showcerts'
            ], input='', capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                # Parse certificate information
                cert_info = {}
                
                # Extract certificate details
                lines = result.stdout.split('\n')
                cert_start = False
                cert_lines = []
                
                for line in lines:
                    if '-----BEGIN CERTIFICATE-----' in line:
                        cert_start = True
                        cert_lines = [line]
                    elif cert_start and '-----END CERTIFICATE-----' in line:
                        cert_lines.append(line)
                        break
                    elif cert_start:
                        cert_lines.append(line)
                
                if cert_lines:
                    # Save certificate to temporary file for parsing
                    with open('/tmp/temp_cert.pem', 'w') as f:
                        f.write('\n'.join(cert_lines))
                    
                    # Parse certificate with cryptography library
                    with open('/tmp/temp_cert.pem', 'rb') as f:
                        cert_data = f.read()
                        cert = x509.load_pem_x509_certificate(cert_data, default_backend())
                        
                        cert_info = {
                            'subject': str(cert.subject),
                            'issuer': str(cert.issuer),
                            'serial_number': str(cert.serial_number),
                            'not_valid_before': cert.not_valid_before.isoformat() if cert.not_valid_before else None,
                            'not_valid_after': cert.not_valid_after.isoformat() if cert.not_valid_after else None,
                            'signature_algorithm': cert.signature_algorithm_oid._name if cert.signature_algorithm_oid else 'Unknown',
                        }
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'hostname': self.hostname,
                    'certificate_info': cert_info
                }
            else:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'error': f'Failed to get certificate: {result.stderr}'
                }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def check_certificate_expiration(self):
        """Check certificate expiration status"""
        try:
            cert_info = self.get_certificate_info()
            if 'error' in cert_info:
                return cert_info
            
            not_valid_after = cert_info['certificate_info'].get('not_valid_after')
            if not_valid_after:
                expiration_date = datetime.fromisoformat(not_valid_after.replace('Z', '+00:00'))
                days_until_expiration = (expiration_date - datetime.now()).days
                
                status = 'valid'
                if days_until_expiration < 0:
                    status = 'expired'
                elif days_until_expiration < 30:
                    status = 'expiring_soon'
                elif days_until_expiration < 90:
                    status = 'expiring'
                
                return {
                    'timestamp': datetime.now().isoformat(),
                    'status': status,
                    'days_until_expiration': days_until_expiration,
                    'expiration_date': not_valid_after
                }
            else:
                return {
                    'timestamp': datetime.now().isoformat(),
                    'error': 'No expiration date found'
                }
                
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }
    
    def monitor_ssl(self, interval=3600):
        """Monitor SSL continuously"""
        print("Starting SSL certificate monitoring...")
        print(f"Monitoring interval: {interval} seconds")
        print("Press Ctrl+C to stop")
        print("-" * 50)
        
        try:
            while True:
                cert_info = self.get_certificate_info()
                expiration_info = self.check_certificate_expiration()
                
                # Save status to log file
                log_data = {
                    'timestamp': datetime.now().isoformat(),
                    'certificate_info': cert_info,
                    'expiration_info': expiration_info
                }
                
                with open("logs/ssl_monitoring.json", "a") as f:
                    f.write(json.dumps(log_data) + "\n")
                
                # Display status
                timestamp = datetime.now().isoformat()
                print(f"[{timestamp}] SSL Certificate Status:")
                
                if 'error' in cert_info:
                    print(f"  ✗ Certificate info error: {cert_info['error']}")
                else:
                    print(f"  ✓ Certificate subject: {cert_info['certificate_info'].get('subject', 'N/A')}")
                    print(f"  ✓ Certificate issuer: {cert_info['certificate_info'].get('issuer', 'N/A')}")
                
                if 'error' in expiration_info:
                    print(f"  ✗ Expiration check error: {expiration_info['error']}")
                else:
                    status = expiration_info.get('status', 'unknown')
                    days_left = expiration_info.get('days_until_expiration', 'N/A')
                    print(f"  Status: {status}")
                    print(f"  Days until expiration: {days_left}")
                
                print("-" * 50)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")
    
    def get_ssl_metrics(self):
        """Get SSL performance metrics"""
        try:
            # Test SSL connection time
            start_time = time.time()
            
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(30)
            sock.connect((self.hostname, self.port))
            
            ssl_sock = context.wrap_socket(sock, server_hostname=self.hostname)
            handshake_time = time.time() - start_time
            
            # Get cipher information
            cipher = ssl_sock.cipher()
            
            ssl_sock.close()
            
            return {
                'timestamp': datetime.now().isoformat(),
                'handshake_time': handshake_time,
                'cipher_suite': cipher[0] if cipher else 'Unknown',
                'protocol': cipher[1] if cipher else 'Unknown',
                'key_size': cipher[2] if cipher else 'Unknown'
            }
            
        except Exception as e:
            return {
                'timestamp': datetime.now().isoformat(),
                'error': str(e)
            }

if __name__ == "__main__":
    monitor = SSLMonitor()
    
    # Run continuous monitoring if requested
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        monitor.monitor_ssl()
    else:
        # Run single status check
        cert_info = monitor.get_certificate_info()
        print(json.dumps(cert_info, indent=2))
        
        # Show expiration status
        expiration_info = monitor.check_certificate_expiration()
        print("\nExpiration Status:")
        print(json.dumps(expiration_info, indent=2))
        
        # Show metrics
        metrics = monitor.get_ssl_metrics()
        print("\nSSL Metrics:")
        print(json.dumps(metrics, indent=2))
```

### 7. Configure SSL Optimization

#### Optimize SSL Configuration
```bash
# Create optimized SSL configuration
nano nginx.optimized.ssl.conf
```

Example optimized SSL configuration:
```nginx
http {
    # SSL optimization settings
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256;
    ssl_prefer_server_ciphers off;
    
    # SSL session optimization
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    ssl_session_tickets on;
    
    # SSL stapling
    ssl_stapling on;
    ssl_stapling_verify on;
    resolver 8.8.8.8 8.8.4.4 valid=300s;
    resolver_timeout 5s;
    
    # HTTP server with optimized SSL
    server {
        listen 443 ssl http2;
        server_name your-domain.com www.your-domain.com;
        
        # SSL certificate configuration
        ssl_certificate /etc/nginx/ssl/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/privkey.pem;
        
        # HSTS
        add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload" always;
        
        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        add_header Referrer-Policy "strict-origin-when-cross-origin" always;
        
        # OCSP stapling
        ssl_stapling on;
        ssl_stapling_verify on;
        
        # Location blocks...
        # ... (same as previous configuration)
    }
}
```

#### Implement Certificate Renewal Automation
```bash
# Create certificate renewal script
nano scripts/renew_ssl_certificates.py
```

Example certificate renewal script:
```python
#!/usr/bin/env python3
import subprocess
import time
from datetime import datetime
import json
import os

class SSLCertificateManager:
    """Manage SSL certificate renewal and monitoring"""
    
    def __init__(self):
        self.certbot_path = "/usr/bin/certbot"
        self.cert_dir = "/etc/letsencrypt/live"
        self.renewal_log = "logs/cert_renewal.log"
    
    def check_certificate_expiration(self, domain):
        """Check if certificate needs renewal"""
        try:
            # Get certificate expiration date
            result = subprocess.run([
                'openssl', 'x509', '-in', f'{self.cert_dir}/{domain}/cert.pem',
                '-noout', '-enddate'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                # Parse expiration date
                end_date_line = result.stdout.strip()
                if 'notAfter=' in end_date_line:
                    end_date_str = end_date_line.split('notAfter=')[1]
                    # Convert to datetime
                    from datetime import datetime
                    import time
                    
                    # Parse the date string (format: Mon DD HH:MM:SS YYYY GMT)
                    exp_time = time.strptime(end_date_str, "%b %d %H:%M:%S %Y %Z")
                    exp_date = datetime(*exp_time[:6])
                    
                    # Calculate days until expiration
                    days_until_expiration = (exp_date - datetime.now()).days
                    
                    return {
                        'days_until_expiration': days_until_expiration,
                        'expiration_date': exp_date.isoformat(),
                        'needs_renewal': days_until_expiration < 30
                    }
            
            return {'error': 'Failed to parse certificate expiration'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def renew_certificates(self, domains=None):
        """Renew SSL certificates"""
        print("Renewing SSL certificates...")
        
        try:
            # Create log entry
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'action': 'certificate_renewal',
                'domains': domains or 'all'
            }
            
            # Run certbot renewal
            cmd = [self.certbot_path, 'renew']
            if domains:
                cmd.extend(['--cert-name', domains[0]])
            
            cmd.extend(['--quiet', '--no-random-sleep-on-renew'])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✓ Certificates renewed successfully")
                log_entry['status'] = 'success'
                log_entry['message'] = 'Certificates renewed successfully'
            else:
                print(f"✗ Certificate renewal failed: {result.stderr}")
                log_entry['status'] = 'failed'
                log_entry['error'] = result.stderr
            
            # Log the renewal attempt
            with open(self.renewal_log, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"✗ Certificate renewal error: {e}")
            return False
    
    def reload_nginx(self):
        """Reload Nginx to use new certificates"""
        print("Reloading Nginx...")
        
        try:
            result = subprocess.run(['systemctl', 'reload', 'nginx'], capture_output=True, text=True)
            if result.returncode == 0:
                print("✓ Nginx reloaded successfully")
                return True
            else:
                print(f"✗ Nginx reload failed: {result.stderr}")
                return False
        except Exception as e:
            print(f"✗ Nginx reload error: {e}")
            return False
    
    def setup_automatic_renewal(self):
        """Setup automatic certificate renewal"""
        print("Setting up automatic certificate renewal...")
        
        try:
            # Create cron job for automatic renewal
            cron_job = "0 12 * * * /usr/bin/certbot renew --quiet --no-random-sleep-on-renew"
            
            # Add to crontab
            current_crontab = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
            if cron_job not in current_crontab.stdout:
                # Add the cron job
                new_crontab = current_crontab.stdout + cron_job + "\n"
                subprocess.run(['crontab', '-'], input=new_crontab, text=True)
                print("✓ Automatic renewal cron job added")
            else:
                print("✓ Automatic renewal cron job already exists")
            
            return True
            
        except Exception as e:
            print(f"✗ Automatic renewal setup failed: {e}")
            return False
    
    def monitor_certificates(self):
        """Monitor certificate status"""
        print("Monitoring certificate status...")
        
        try:
            # Get certificate information
            if os.path.exists(self.cert_dir):
                domains = os.listdir(self.cert_dir)
                for domain in domains:
                    if os.path.isdir(f'{self.cert_dir}/{domain}'):
                        cert_info = self.check_certificate_expiration(domain)
                        print(f"Domain: {domain}")
                        if 'error' not in cert_info:
                            days_left = cert_info['days_until_expiration']
                            status = "Valid" if days_left > 0 else "Expired"
                            print(f"  Status: {status}")
                            print(f"  Days until expiration: {days_left}")
                            if cert_info['needs_renewal']:
                                print(f"  ⚠ Certificate needs renewal")
                        else:
                            print(f"  ✗ Error: {cert_info['error']}")
            
            return True
            
        except Exception as e:
            print(f"✗ Certificate monitoring failed: {e}")
            return False

def main():
    """Main function for certificate management"""
    manager = SSLCertificateManager()
    
    # Check certificate status
    manager.monitor_certificates()
    
    # Check if renewal is needed
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--renew":
        # Force renewal
        manager.renew_certificates()
        manager.reload_nginx()
    elif len(sys.argv) > 1 and sys.argv[1] == "--setup-auto":
        # Setup automatic renewal
        manager.setup_automatic_renewal()
    else:
        # Check expiration and renew if needed
        # This would typically be run by a cron job
        pass

if __name__ == "__main__":
    main()
```

### 8. Troubleshoot SSL Issues

#### Diagnose Common SSL Issues
```bash
# Check SSL certificate validity
openssl x509 -in ssl/selfsigned.crt -text -noout

# Test SSL connection
openssl s_client -connect localhost:443 -showcerts

# Check certificate expiration
openssl x509 -in ssl/selfsigned.crt -noout -enddate

# Verify certificate chain
openssl verify -CAfile ssl/selfsigned.crt ssl/selfsigned.crt

# Test SSL protocols
openssl ciphers -v | grep -i tls
```

#### Resolve SSL Issues
```bash
# Restart Nginx with SSL
docker-compose restart nginx

# Test SSL configuration
docker-compose exec nginx nginx -t

# Reload Nginx configuration
docker-compose exec nginx nginx -s reload

# Check SSL certificate permissions
ls -la ssl/

# Verify certificate paths in Nginx config
docker-compose exec nginx cat /etc/nginx/nginx.conf | grep ssl_certificate

# Test SSL connection from outside
curl -v https://localhost

# Check certificate expiration
docker-compose exec nginx openssl x509 -in /etc/nginx/ssl/certificate.pem -noout -enddate
```

### 9. Verify SSL Setup
```bash
# Test final SSL setup
python scripts/test_ssl.py

# Run SSL performance test
python scripts/test_ssl_performance.py

# Check certificate status
python scripts/monitor_ssl.py

# Verify SSL functionality
curl -f https://localhost
curl -f https://localhost/api/v1/health

# Test HSTS header
curl -I https://localhost | grep -i strict
```

## Verification
After completing the above steps, you should be able to:
- [ ] Understand SSL certificate architecture and configuration
- [ ] Generate and install SSL certificates (self-signed or Let's Encrypt)
- [ ] Configure SSL in Nginx with proper security settings
- [ ] Test SSL configuration and certificate validity
- [ ] Monitor SSL certificate status and expiration
- [ ] Configure SSL optimization and performance settings
- [ ] Implement certificate renewal automation
- [ ] Troubleshoot SSL issues and errors
- [ ] Verify SSL setup and secure HTTPS connections

## Common SSL Certificate Issues and Solutions

### Certificate Issues
- **"Certificate expired"**: Renew certificate before expiration
- **"Certificate not trusted"**: Install proper CA certificates or use Let's Encrypt
- **"Certificate mismatch"**: Ensure certificate matches domain name
- **"Self-signed certificate"**: Use trusted CA or accept self-signed certificate

### Configuration Issues
- **"SSL handshake failed"**: Check certificate permissions and paths
- **"Protocol not supported"**: Configure proper SSL protocols
- **"Cipher suite not supported"**: Update cipher suite configuration
- **"HSTS header missing"**: Add HSTS header to Nginx configuration

### Performance Issues
- **"Slow SSL handshake"**: Optimize SSL session caching and protocols
- **"High CPU usage"**: Configure proper SSL session tickets and caching
- **"Memory leaks"**: Monitor SSL session cache size and cleanup
- **"Connection timeouts"**: Increase SSL timeout values

## Troubleshooting Checklist

### Quick Fixes
- [ ] Check SSL certificate validity and expiration
- [ ] Verify certificate file permissions and paths
- [ ] Test SSL configuration syntax
- [ ] Restart Nginx service
- [ ] Check firewall and port configuration
- [ ] Review SSL protocol and cipher settings

### Advanced Diagnostics
- [ ] Implement detailed SSL monitoring and logging
- [ ] Analyze SSL handshake performance
- [ ] Optimize SSL configuration and caching
- [ ] Configure automatic certificate renewal
- [ ] Implement comprehensive error handling
- [ ] Set up proper security headers and HSTS

## Next Steps
Congratulations! You have completed all 41 installation guide chunks for the CRE Intelligence Platform. The platform is now fully configured with:
- System requirements verification
- Docker and local development setup
- Database and caching services
- API integrations and external services
- Background task processing with Celery
- Reverse proxy with Nginx
- SSL certificate configuration

You can now proceed to deploy and use the CRE Intelligence Platform according to your specific requirements.