# scripts/health_check.sh
#!/bin/bash
"""
Health check script for all CRE Intelligence services
"""

echo "========================================="
echo "CRE Intelligence Platform Health Check"
echo "========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to check service
check_service() {
    local name=$1
    local url=$2
    local expected=$3
    
    echo -n "Checking $name... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" $url)
    
    if [ "$response" = "$expected" ]; then
        echo -e "${GREEN}✓ OK${NC}"
        return 0
    else
        echo -e "${RED}✗ FAILED (HTTP $response)${NC}"
        return 1
    fi
}

# Check all services
check_service "FastAPI MCP" "http://localhost:8000/" "200"
check_service "Prometheus" "http://localhost:9090/-/healthy" "200"
check_service "Grafana" "http://localhost:3000/api/health" "200"
check_service "Redis" "http://localhost:6379" "000" # Redis doesn't have HTTP

# Check PostgreSQL
echo -n "Checking PostgreSQL... "
if pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo -e "${GREEN}✓ OK${NC}"
else
    echo -e "${RED}✗ FAILED${NC}"
fi

# Check disk space
echo -n "Checking disk space... "
disk_usage=$(df /app/data 2>/dev/null | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$disk_usage" -lt 80 ]; then
    echo -e "${GREEN}✓ OK ($disk_usage% used)${NC}"
else
    echo -e "${RED}✗ WARNING ($disk_usage% used)${NC}"
fi

echo "========================================="

# ============================================================================
# scripts/data_manager.py
"""Data management utilities for CRE Intelligence Platform"""

import os
import shutil
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
import click

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataManager:
    """Manage data lifecycle for CRE Intelligence"""
    
    def __init__(self, base_path: str = "./data"):
        self.base_path = Path(base_path)
        self.raw_path = self.base_path / "raw"
        self.processed_path = self.base_path / "processed"
        self.archive_path = self.base_path / "archive"
        self.cache_path = self.base_path / "cache"
        
        # Ensure directories exist
        for path in [self.raw_path, self.processed_path, self.archive_path, self.cache_path]:
            path.mkdir(parents=True, exist_ok=True)
    
    def get_storage_stats(self) -> Dict:
        """Get storage statistics"""
        stats = {}
        
        for name, path in [
            ("raw", self.raw_path),
            ("processed", self.processed_path),
            ("archive", self.archive_path),
            ("cache", self.cache_path)
        ]:
            if path.exists():
                size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                count = len(list(path.rglob('*')))
                stats[name] = {
                    "size_mb": size / (1024 * 1024),
                    "file_count": count
                }
            else:
                stats[name] = {"size_mb": 0, "file_count": 0}
        
        stats["total_size_mb"] = sum(s["size_mb"] for s in stats.values())
        return stats
    
    def archive_old_data(self, days: int = 30) -> int:
        """Archive data older than specified days"""
        archived_count = 0
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for file_path in self.processed_path.glob("*.jsonl"):
            # Check file modification time
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
            
            if mtime < cutoff_date:
                # Create archive subdirectory by month
                archive_subdir = self.archive_path / mtime.strftime("%Y-%m")
                archive_subdir.mkdir(exist_ok=True)
                
                # Move file to archive
                archive_path = archive_subdir / file_path.name
                shutil.move(str(file_path), str(archive_path))
                logger.info(f"Archived {file_path.name} to {archive_subdir}")
                archived_count += 1
        
        return archived_count
    
    def clean_cache(self, max_age_hours: int = 24) -> int:
        """Clean cache files older than specified hours"""
        cleaned_count = 0
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        
        for file_path in self.cache_path.rglob("*"):
            if file_path.is_file():
                mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                
                if mtime < cutoff_time:
                    file_path.unlink()
                    logger.info(f"Deleted cache file: {file_path.name}")
                    cleaned_count += 1
        
        return cleaned_count
    
    def merge_filtered_data(self, output_file: str = "merged_filtered.jsonl") -> Path:
        """Merge all filtered data files"""
        merged_data = []
        
        for file_path in self.processed_path.glob("filtered_*.jsonl"):
            df = pd.read_json(file_path, lines=True)
            merged_data.append(df)
        
        if merged_data:
            combined = pd.concat(merged_data, ignore_index=True)
            # Remove duplicates
            combined = combined.drop_duplicates(subset=['id'], keep='first')
            
            output_path = self.processed_path / output_file
            combined.to_json(output_path, orient='records', lines=True)
            logger.info(f"Merged {len(merged_data)} files into {output_path}")
            return output_path
        
        return None
    
    def export_for_analysis(self, format: str = "parquet") -> Path:
        """Export processed data for analysis"""
        # Collect all processed data
        all_data = []
        
        for file_path in self.processed_path.glob("filtered_*.jsonl"):
            df = pd.read_json(file_path, lines=True)
            all_data.append(df)
        
        if all_data:
            combined = pd.concat(all_data, ignore_index=True)
            
            # Export based on format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if format == "parquet":
                output_path = self.base_path / f"export_{timestamp}.parquet"
                combined.to_parquet(output_path)
            elif format == "csv":
                output_path = self.base_path / f"export_{timestamp}.csv"
                combined.to_csv(output_path, index=False)
            elif format == "excel":
                output_path = self.base_path / f"export_{timestamp}.xlsx"
                combined.to_excel(output_path, index=False)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Exported {len(combined)} records to {output_path}")
            return output_path
        
        return None

@click.group()
def cli():
    """Data management CLI for CRE Intelligence"""
    pass

@cli.command()
def stats():
    """Show storage statistics"""
    manager = DataManager()
    stats = manager.get_storage_stats()
    
    print("\nStorage Statistics:")
    print("-" * 40)
    for name, data in stats.items():
        if name != "total_size_mb":
            print(f"{name.capitalize():12} {data['size_mb']:.2f} MB ({data['file_count']} files)")
    print("-" * 40)
    print(f"{'Total':12} {stats['total_size_mb']:.2f} MB")

@cli.command()
@click.option('--days', default=30, help='Archive data older than N days')
def archive(days):
    """Archive old data"""
    manager = DataManager()
    count = manager.archive_old_data(days)
    print(f"Archived {count} files older than {days} days")

@cli.command()
@click.option('--hours', default=24, help='Clean cache older than N hours')
def clean(hours):
    """Clean cache files"""
    manager = DataManager()
    count = manager.clean_cache(hours)
    print(f"Cleaned {count} cache files older than {hours} hours")

@cli.command()
@click.option('--output', default='merged_filtered.jsonl', help='Output filename')
def merge(output):
    """Merge filtered data files"""
    manager = DataManager()
    result = manager.merge_filtered_data(output)
    if result:
        print(f"Merged data saved to: {result}")
    else:
        print("No data files to merge")

@cli.command()
@click.option('--format', type=click.Choice(['parquet', 'csv', 'excel']), default='parquet')
def export(format):
    """Export data for analysis"""
    manager = DataManager()
    result = manager.export_for_analysis(format)
    if result:
        print(f"Data exported to: {result}")
    else:
        print("No data to export")

if __name__ == "__main__":
    cli()

# ============================================================================
# scripts/performance_monitor.py
"""Performance monitoring for CRE Intelligence Platform"""

import time
import psutil
import asyncio
from datetime import datetime
from typing import Dict, List
import json
from pathlib import Path

class PerformanceMonitor:
    """Monitor system performance metrics"""
    
    def __init__(self, output_dir: str = "./monitoring/metrics"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.metrics_history = []
    
    def get_system_metrics(self) -> Dict:
        """Get current system metrics"""
        return {
            "timestamp": datetime.now().isoformat(),
            "cpu": {
                "percent": psutil.cpu_percent(interval=1),
                "count": psutil.cpu_count(),
                "freq": psutil.cpu_freq().current if psutil.cpu_freq() else None
            },
            "memory": {
                "total_gb": psutil.virtual_memory().total / (1024**3),
                "used_gb": psutil.virtual_memory().used / (1024**3),
                "percent": psutil.virtual_memory().percent
            },
            "disk": {
                "total_gb": psutil.disk_usage('/').total / (1024**3),
                "used_gb": psutil.disk_usage('/').used / (1024**3),
                "percent": psutil.disk_usage('/').percent
            },
            "network": {
                "bytes_sent": psutil.net_io_counters().bytes_sent,
                "bytes_recv": psutil.net_io_counters().bytes_recv
            }
        }
    
    def get_process_metrics(self, process_name: str = "python") -> List[Dict]:
        """Get metrics for specific processes"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info']):
            try:
                if process_name.lower() in proc.info['name'].lower():
                    processes.append({
                        "pid": proc.info['pid'],
                        "name": proc.info['name'],
                        "cpu_percent": proc.cpu_percent(interval=1),
                        "memory_mb": proc.info['memory_info'].rss / (1024**2)
                    })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        
        return processes
    
    async def monitor_endpoint_performance(self, url: str, method: str = "GET", payload: Dict = None):
        """Monitor API endpoint performance"""
        import httpx
        
        metrics = {
            "endpoint": url,
            "method": method,
            "timestamp": datetime.now().isoformat()
        }
        
        start_time = time.time()
        
        try:
            async with httpx.AsyncClient() as client:
                if method == "GET":
                    response = await client.get(url)
                elif method == "POST":
                    response = await client.post(url, json=payload)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                metrics["response_time_ms"] = (time.time() - start_time) * 1000
                metrics["status_code"] = response.status_code
                metrics["success"] = response.status_code == 200
                
        except Exception as e:
            metrics["response_time_ms"] = (time.time() - start_time) * 1000
            metrics["error"] = str(e)
            metrics["success"] = False
        
        return metrics
    
    def save_metrics(self, metrics: Dict, filename: str = None):
        """Save metrics to file"""
        if filename is None:
            filename = f"metrics_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2)
        
        return filepath
    
    async def continuous_monitoring(self, duration: int = 60, interval: int = 5):
        """Run continuous monitoring for specified duration"""
        start_time = time.time()
        metrics_collection = []
        
        while time.time() - start_time < duration:
            metrics = {
                "system": self.get_system_metrics(),
                "processes": self.get_process_metrics(),
                "timestamp": datetime.now().isoformat()
            }
            
            # Test API endpoints
            endpoints = [
                ("http://localhost:8000/", "GET", None),
                ("http://localhost:8000/mine_phrases", "POST", {"corpus_source": "test", "top_k": 10})
            ]
            
            api_metrics = []
            for url, method, payload in endpoints:
                api_metric = await self.monitor_endpoint_performance(url, method, payload)
                api_metrics.append(api_metric)
            
            metrics["api_performance"] = api_metrics
            metrics_collection.append(metrics)
            
            # Print summary
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"CPU: {metrics['system']['cpu']['percent']}% | "
                  f"Memory: {metrics['system']['memory']['percent']}% | "
                  f"Disk: {metrics['system']['disk']['percent']}%")
            
            await asyncio.sleep(interval)
        
        # Save all metrics
        self.save_metrics(metrics_collection, "monitoring_session.json")
        
        # Generate summary
        self.generate_summary(metrics_collection)
    
    def generate_summary(self, metrics: List[Dict]):
        """Generate performance summary"""
        if not metrics:
            return
        
        # Calculate averages
        cpu_avg = sum(m['system']['cpu']['percent'] for m in metrics) / len(metrics)
        mem_avg = sum(m['system']['memory']['percent'] for m in metrics) / len(metrics)
        
        # API performance
        api_times = []
        for m in metrics:
            if 'api_performance' in m:
                for api in m['api_performance']:
                    if 'response_time_ms' in api:
                        api_times.append(api['response_time_ms'])
        
        api_avg = sum(api_times) / len(api_times) if api_times else 0
        
        summary = {
            "monitoring_duration": len(metrics) * 5,  # Assuming 5 second intervals
            "average_cpu_percent": cpu_avg,
            "average_memory_percent": mem_avg,
            "average_api_response_ms": api_avg,
            "max_cpu_percent": max(m['system']['cpu']['percent'] for m in metrics),
            "max_memory_percent": max(m['system']['memory']['percent'] for m in metrics),
            "timestamp": datetime.now().isoformat()
        }
        
        print("\n" + "="*50)
        print("Performance Summary")
        print("="*50)
        print(f"Average CPU Usage: {summary['average_cpu_percent']:.2f}%")
        print(f"Average Memory Usage: {summary['average_memory_percent']:.2f}%")
        print(f"Average API Response: {summary['average_api_response_ms']:.2f}ms")
        print(f"Max CPU Usage: {summary['max_cpu_percent']:.2f}%")
        print(f"Max Memory Usage: {summary['max_memory_percent']:.2f}%")
        
        self.save_metrics(summary, "performance_summary.json")

async def main():
    """Main monitoring function"""
    monitor = PerformanceMonitor()
    
    # Run continuous monitoring for 5 minutes
    await monitor.continuous_monitoring(duration=300, interval=10)

if __name__ == "__main__":
    asyncio.run(main())

# ============================================================================
# scripts/backup.py
"""Backup and restore utilities for CRE Intelligence Platform"""

import os
import shutil
import tarfile
import json
from datetime import datetime
from pathlib import Path
import subprocess
import click

class BackupManager:
    """Manage backups for CRE Intelligence Platform"""
    
    def __init__(self, backup_dir: str = "./backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def backup_data(self, include_raw: bool = False) -> Path:
        """Create data backup"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"cre_data_backup_{timestamp}.tar.gz"
        backup_path = self.backup_dir / backup_name
        
        with tarfile.open(backup_path, "w:gz") as tar:
            # Always backup processed and lexicon data
            tar.add("data/processed", arcname="processed")
            tar.add("data/lexicon", arcname="lexicon")
            
            # Optionally include raw data
            if include_raw:
                tar.add("data/raw", arcname="raw")
            
            # Backup configurations
            tar.add("config", arcname="config")
            
            print(f"Created backup: {backup_path}")
        
        return backup_path
    
    def backup_database(self, connection_string: str) -> Path:
        """Backup PostgreSQL database"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"cre_db_backup_{timestamp}.sql"
        backup_path = self.backup_dir / backup_name
        
        # Parse connection string
        # postgresql://user:password@host:port/database
        import re
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', connection_string)
        
        if match:
            user, password, host, port, database = match.groups()
            
            # Use pg_dump to create backup
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            cmd = [
                'pg_dump',
                '-h', host,
                '-p', port,
                '-U', user,
                '-d', database,
                '-f', str(backup_path)
            ]
            
            subprocess.run(cmd, env=env, check=True)
            print(f"Created database backup: {backup_path}")
        else:
            raise ValueError("Invalid connection string format")
        
        return backup_path
    
    def restore_data(self, backup_file: str):
        """Restore data from backup"""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Extract backup
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall("data/")
        
        print(f"Restored data from: {backup_file}")
    
    def restore_database(self, backup_file: str, connection_string: str):
        """Restore PostgreSQL database from backup"""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_file}")
        
        # Parse connection string
        import re
        match = re.match(r'postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)', connection_string)
        
        if match:
            user, password, host, port, database = match.groups()
            
            # Use psql to restore backup
            env = os.environ.copy()
            env['PGPASSWORD'] = password
            
            cmd = [
                'psql',
                '-h', host,
                '-p', port,
                '-U', user,
                '-d', database,
                '-f', str(backup_path)
            ]
            
            subprocess.run(cmd, env=env, check=True)
            print(f"Restored database from: {backup_file}")
        else:
            raise ValueError("Invalid connection string format")
    
    def list_backups(self):
        """List available backups"""
        backups = list(self.backup_dir.glob("*.tar.gz")) + list(self.backup_dir.glob("*.sql"))
        
        if backups:
            print("\nAvailable backups:")
            print("-" * 50)
            for backup in sorted(backups):
                size_mb = backup.stat().st_size / (1024 * 1024)
                print(f"{backup.name:40} {size_mb:>8.2f} MB")
        else:
            print("No backups found")
    
    def cleanup_old_backups(self, keep_days: int = 30):
        """Remove backups older than specified days"""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=keep_days)
        removed_count = 0
        
        for backup in self.backup_dir.glob("*"):
            if backup.is_file():
                mtime = datetime.fromtimestamp(backup.stat().st_mtime)
                if mtime < cutoff:
                    backup.unlink()
                    print(f"Removed old backup: {backup.name}")
                    removed_count += 1
        
        print(f"Removed {removed_count} old backups")

@click.group()
def cli():
    """Backup management CLI"""
    pass

@cli.command()
@click.option('--include-raw', is_flag=True, help='Include raw data in backup')
def backup_data(include_raw):
    """Create data backup"""
    manager = BackupManager()
    manager.backup_data(include_raw)

@cli.command()
@click.option('--connection', envvar='DATABASE_URL', help='Database connection string')
def backup_db(connection):
    """Backup database"""
    manager = BackupManager()
    manager.backup_database(connection)

@cli.command()
@click.argument('backup_file')
def restore_data(backup_file):
    """Restore data from backup"""
    manager = BackupManager()
    manager.restore_data(backup_file)

@cli.command()
@click.argument('backup_file')
@click.option('--connection', envvar='DATABASE_URL', help='Database connection string')
def restore_db(backup_file, connection):
    """Restore database from backup"""
    manager = BackupManager()
    manager.restore_database(backup_file, connection)

@cli.command()
def list():
    """List available backups"""
    manager = BackupManager()
    manager.list_backups()

@cli.command()
@click.option('--days', default=30, help='Keep backups newer than N days')
def cleanup(days):
    """Remove old backups"""
    manager = BackupManager()
    manager.cleanup_old_backups(days)

if __name__ == "__main__":
    cli()

# ============================================================================
# setup.py
"""Setup configuration for CRE Intelligence Platform"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="cre-intelligence",
    version="1.0.0",
    author="Your Team",
    author_email="team@cre-intelligence.com",
    description="Commercial Real Estate Intelligence Platform",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/cre-intelligence",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.11.0",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
            "pre-commit>=3.5.0",
        ],
        "docs": [
            "mkdocs>=1.5.3",
            "mkdocs-material>=9.4.14",
        ],
    },
    entry_points={
        "console_scripts": [
            "cre-filter=scripts.run_filter_via_mcp:main",
            "cre-mine=scripts.refresh_tfidf_via_mcp:main",
            "cre-expand=scripts.expand_cities_via_mcp:main",
            "cre-pipeline=scripts.run_full_pipeline:main",
            "cre-schedule=scripts.schedule_jobs:main",
            "cre-data=scripts.data_manager:cli",
            "cre-backup=scripts.backup:cli",
            "cre-monitor=scripts.performance_monitor:main",
        ],
    },
    package_data={
        "mcp": ["*.yml", "*.yaml", "*.json"],
        "config": ["*.yml", "*.yaml"],
        "bmad": ["**/*.yml", "**/*.yaml"],
    },
    include_package_data=True,
)

print("CRE Intelligence Platform setup complete!")
print("Run 'pip install -e .' to install in development mode")