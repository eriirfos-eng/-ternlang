#!/usr/bin/env python3
"""
Ping/Keepalife Monitoring Agent (Quirit Edition)
Monitors network connectivity and keepalife signals
Falls back to Desktop logging if /var/log is not writable
"""

import os
import time
import logging
from pathlib import Path

# === Logging setup with fallback ===
desktop_log = str(Path.home() / "Desktop" / "ping_monitor.log")
system_log = "/var/log/ping_monitor.log"

try:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - PING-KEEPALIFE - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(system_log), logging.StreamHandler()]
    )
    logger = logging.getLogger("PING-KEEPALIFE")
    logger.info(f"Logging to {system_log}")
except PermissionError:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - PING-KEEPALIFE - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler(desktop_log), logging.StreamHandler()]
    )
    logger = logging.getLogger("PING-KEEPALIFE")
    logger.warning(f"No permission for {system_log}, logging to {desktop_log} instead")

# === Core keepalife function ===
def keepalife_ping(target="8.8.8.8", interval=5):
    """Continuously ping a target host at regular intervals."""
    logger.info(f"Starting keepalife ping to {target} every {interval}s")
    while True:
        response = os.system(f"ping -c 1 {target} > /dev/null 2>&1")
        if response == 0:
            logger.info(f"Ping to {target} successful")
        else:
            logger.warning(f"Ping to {target} failed")
        time.sleep(interval)

# === Entry point ===
if __name__ == "__main__":
    keepalife_ping()


# === Logging setup with fallback ===
def setup_logging():
    log_paths = [
        Path("/var/log/ping_monitor.log"),
        Path.home() / "Desktop" / "ping_monitor.log"
    ]
    handlers = []
    for log_path in log_paths:
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            handlers = [
                logging.FileHandler(log_path),
                logging.StreamHandler()
            ]
            print(f"[Desktop] Logging to {log_path}")
            break
        except PermissionError:
            continue

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - PING-AGENT - %(levelname)s - %(message)s",
        handlers=handlers
    )
    return logging.getLogger("PING-AGENT")

logger = setup_logging()


class PingMonitor:
    def __init__(self, config_file=str(Path.home() / ".config/ping_monitor.json")):
        self.config = self.load_config(config_file)
        self.stats = {
            'pings_sent': 0,
            'pings_received': 0,
            'tcp_checks': 0,
            'udp_checks': 0,
            'keepalives_monitored': 0,
            'start_time': time.time()
        }
        self.host_states = {}
        
    def load_config(self, config_file):
        """Load configuration or create default"""
        default_config = {
            "monitor_interval": 30,
            "ping_targets": [
                "8.8.8.8",
                "1.1.1.1",
                "208.67.222.222",
                "9.9.9.9"
            ],
            "ping_timeout": 3,
            "ping_count": 4
        }
        
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
        except FileNotFoundError:
            logger.info(f"No config found, creating default at {config_file}")
            Path(config_file).parent.mkdir(parents=True, exist_ok=True)
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=2)
            return default_config

    async def ping_host_system(self, host):
        """Ping using system ping command"""
        try:
            cmd = [
                'ping', '-c', str(self.config['ping_count']), 
                '-W', str(self.config['ping_timeout']), host
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await proc.communicate()
            
            self.stats['pings_sent'] += self.config['ping_count']
            
            if proc.returncode == 0:
                return self.parse_ping_output(stdout.decode(), host)
            else:
                logger.warning(f"Ping failed for {host}: {stderr.decode().strip()}")
                return {'host': host, 'status': 'failed', 'timestamp': datetime.now().isoformat()}
                
        except Exception as e:
            logger.error(f"Ping error for {host}: {e}")
            return {'host': host, 'status': 'error', 'timestamp': datetime.now().isoformat()}

    def parse_ping_output(self, output, host):
        """Parse system ping output (Linux style)"""
        result = {
            'host': host,
            'status': 'success',
            'timestamp': datetime.now().isoformat()
        }
        for line in output.split("\n"):
            if "packet loss" in line:
                result['packet_loss_line'] = line.strip()
            if "min/avg/max" in line or "min/avg/max/stddev" in line:
                result['rtt_line'] = line.strip()
        return result


async def main():
    logger.info("[Desktop] Ping/Keepalive Agent booting — %s", datetime.utcnow().isoformat())
    monitor = PingMonitor()
    while True:
        for host in monitor.config['ping_targets']:
            result = await monitor.ping_host_system(host)
            logger.info(f"[PING] {result}")
        await asyncio.sleep(monitor.config['monitor_interval'])


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Ping/Keepalive Agent shutting down")

