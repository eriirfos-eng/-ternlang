#!/usr/bin/env python3
"""
ntp_monitor_agent.py — Quirit Edition
Monitors global clock synchronization and time drift.
Emits ternary packets from socket_custom.TernarySocket for each measurement.
"""

import asyncio
import json
import logging
import socket
import struct
import time
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import re
import os
import sys

# Desktop boot banner
print("[Desktop] NTP Monitor Agent booting — {}".format(datetime.now(timezone.utc).isoformat()))

# Import quirit lattice socket from same folder
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
try:
    from socket_custom import TernarySocket
except Exception as e:
    print("[Error] Could not import socket_custom.py from Desktop:", e)
    sys.exit(1)

# Safe default log location (no root needed)
DEFAULT_LOG = str(Path.home() / "ntp_monitor.log")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - NTP-AGENT - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(DEFAULT_LOG), logging.StreamHandler()],
)
logger = logging.getLogger("NTP-AGENT")


class NTPMonitor:
    def __init__(self, config_file="/etc/ntp_monitor.json"):
        self.config_path = self._resolve_config_path(config_file)
        self.config = self.load_config(self.config_path)
        self.stats = {
            "queries_sent": 0,
            "responses_received": 0,
            "timeouts": 0,
            "drift_measurements": 0,
            "start_time": time.time(),
        }
        self.sock = TernarySocket("ntp-monitor")
        self.backoff_until = 0.0

    def _resolve_config_path(self, preferred: str) -> str:
        """Try preferred path; if not writable, fall back to user home."""
        try:
            p = Path(preferred)
            p.parent.mkdir(parents=True, exist_ok=True)
            # touch will raise if not permitted
            if not p.exists():
                p.write_text("")  # create empty; we may overwrite later
            return preferred
        except Exception:
            fallback = Path.home() / ".config" / "ntp_monitor.json"
            fallback.parent.mkdir(parents=True, exist_ok=True)
            return str(fallback)

    def load_config(self, config_file: str) -> dict:
        default_config = {
            "monitor_interval": 60,
            "ntp_servers": [
                "pool.ntp.org",
                "time.google.com",
                "time.cloudflare.com",
                "time.apple.com",
                "0.pool.ntp.org",
                "1.pool.ntp.org",
            ],
            "timeout": 5,
            "alert_thresholds": {
                "drift_ms": 100.0,
                "stratum_max": 15,
                "server_unreachable_count": 3,
            },
            "output_file": str(Path.home() / "ntp_data.jsonl"),
            "webhook_url": None,
            "local_chrony": True,
            "local_ntpd": False,
        }
        try:
            text = Path(config_file).read_text()
            if text.strip():
                cfg = json.loads(text)
            else:
                cfg = {}
        except FileNotFoundError:
            logger.info("No config found, creating default at %s", config_file)
            cfg = {}
        except Exception as e:
            logger.warning("Config read error (%s). Using defaults.", e)
            cfg = {}

        # merge defaults
        for k, v in default_config.items():
            if k not in cfg:
                cfg[k] = v

        # write back merged config
        try:
            Path(config_file).write_text(json.dumps(cfg, indent=2))
        except Exception as e:
            logger.warning("Could not write config to %s (%s)", config_file, e)

        # ensure output dir exists
        try:
            Path(cfg["output_file"]).parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        return cfg

    @staticmethod
    def _ntp_packet() -> bytes:
        # 48-byte NTP packet, LI=0, VN=4, Mode=3 (client)
        pkt = bytearray(48)
        pkt[0] = 0x23
        return bytes(pkt)

    @staticmethod
    def _ntp_to_unix(ntp_seconds_float: float) -> float:
        # NTP epoch starts 1900-01-01; UNIX epoch 1970-01-01
        return ntp_seconds_float - 2208988800.0

    @staticmethod
    def _fixed_32_to_float(u32: int) -> float:
        # 16.16 fixed-point
        return float(u32) / 65536.0

    def _derive_quirit_state(self, offset_ms: float) -> int:
        # Map offset to ternary: near 0 => 0 (tend), >0 => +1 (affirm), <0 => -1 (shadow)
        threshold = 5.0  # ms deadband
        if offset_ms > threshold:
            return 1
        if offset_ms < -threshold:
            return -1
        return 0

    async def query_ntp_server(self, server: str, port: int = 123) -> dict:
        """Send one UDP NTP request and parse response."""
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.settimeout(float(self.config["timeout"]))

            send_time = time.time()
            s.sendto(self._ntp_packet(), (server, port))
            self.stats["queries_sent"] += 1

            data, addr = s.recvfrom(512)
            recv_time = time.time()
            self.stats["responses_received"] += 1
            return self._parse_ntp_response(data, send_time, recv_time, server)
        except socket.timeout:
            self.stats["timeouts"] += 1
            # encode timeout as shadow state
            self.sock.switch(-1)
            pkt = self.sock.emit()
            return {
                "agent": "ntp-monitor",
                "server": server,
                "status": "timeout",
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **pkt,
            }
        except Exception as e:
            # encode error as shadow state
            self.sock.switch(-1)
            pkt = self.sock.emit()
            return {
                "agent": "ntp-monitor",
                "server": server,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat(),
                **pkt,
            }
        finally:
            if s is not None:
                try:
                    s.close()
                except Exception:
                    pass

    def _parse_ntp_response(self, data: bytes, send_time: float, recv_time: float, server: str) -> dict:
        if len(data) < 48:
            self.sock.switch(-1)
            pkt = self.sock.emit()
            return {"agent": "ntp-monitor", "server": server, "status": "invalid_response", **pkt}

        # Header fields
        li_vn_mode = data[0]
        leap_indicator = (li_vn_mode >> 6) & 0x3
        version = (li_vn_mode >> 3) & 0x7
        mode = li_vn_mode & 0x7
        stratum = data[1]
        poll = data[2]
        precision_signed = struct.unpack("!b", data[3:4])[0]

        root_delay_u32 = struct.unpack("!I", data[4:8])[0]
        root_disp_u32 = struct.unpack("!I", data[8:12])[0]
        root_delay = self._fixed_32_to_float(root_delay_u32)
        root_dispersion = self._fixed_32_to_float(root_disp_u32)
        ref_id = data[12:16].hex()

        # Timestamps are 64-bit: seconds (32) + fraction (32)
        def u64_to_float(u64: int) -> float:
            secs = (u64 >> 32) & 0xFFFFFFFF
            frac = u64 & 0xFFFFFFFF
            return float(secs) + float(frac) / 4294967296.0

        reference_u64 = struct.unpack("!Q", data[16:24])[0]
        originate_u64 = struct.unpack("!Q", data[24:32])[0]
        receive_u64 = struct.unpack("!Q", data[32:40])[0]
        transmit_u64 = struct.unpack("!Q", data[40:48])[0]

        reference_ntp = u64_to_float(reference_u64)
        originate_ntp = u64_to_float(originate_u64)
        receive_ntp = u64_to_float(receive_u64)
        transmit_ntp = u64_to_float(transmit_u64)

        # Convert to UNIX seconds
        T1 = send_time
        T2 = self._ntp_to_unix(receive_ntp)
        T3 = self._ntp_to_unix(transmit_ntp)
        T4 = recv_time

        # Standard NTP formulas
        offset = ((T2 - T1) + (T3 - T4)) / 2.0
        delay = (T4 - T1) - (T3 - T2)

        self.stats["drift_measurements"] += 1

        offset_ms = offset * 1000.0
        delay_ms = delay * 1000.0

        # choose ternary state based on offset sign and deadband
        self.sock.switch(self._derive_quirit_state(offset_ms))
        pkt = self.sock.emit()

        return {
            "agent": "ntp-monitor",
            "server": server,
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "leap_indicator": leap_indicator,
            "version": version,
            "mode": mode,
            "stratum": int(stratum),
            "poll_interval": int(poll),
            "precision": int(precision_signed),
            "root_delay_ms": root_delay * 1000.0,
            "root_dispersion_ms": root_dispersion * 1000.0,
            "reference_id": ref_id,
            "offset_ms": offset_ms,
            "delay_ms": delay_ms,
            "reference_time_unix": self._ntp_to_unix(reference_ntp),
            "originate_time_unix": self._ntp_to_unix(originate_ntp),
            "receive_time_unix": T2,
            "transmit_time_unix": T3,
            **pkt,
        }

    async def get_local_chrony_status(self) -> dict | None:
        if not self.config.get("local_chrony", True):
            return None
        try:
            proc = await asyncio.create_subprocess_exec(
                "chronyc", "tracking",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()
            if proc.returncode != 0:
                logger.debug("chronyc tracking failed: %s", stderr.decode(errors="ignore"))
                return None
            return self._parse_chrony_tracking(stdout.decode(errors="ignore"))
        except FileNotFoundError:
            logger.debug("chronyc not found")
            return None
        except Exception as e:
            logger.debug("chronyc error: %s", e)
            return None

    def _parse_chrony_tracking(self, text: str) -> dict:
        data = {"source": "chrony", "timestamp": datetime.now(timezone.utc).isoformat()}
        # System time     : 0.000003456 seconds fast of NTP time
        m = re.search(r"System time\s*:\s*([+-]?\d+\.\d+)\s*seconds", text)
        if m:
            data["system_offset_ms"] = float(m.group(1)) * 1000.0
        # Frequency       : 12.345 ppm fast
        m = re.search(r"Frequency\s*:\s*([+-]?\d+\.\d+)\s*ppm", text)
        if m:
            data["frequency_ppm"] = float(m.group(1))
        # Stratum         : 3
        m = re.search(r"Stratum\s*:\s*(\d+)", text)
        if m:
            data["stratum"] = int(m.group(1))
        return data

    async def save_data(self, record: dict) -> None:
        path = Path(self.config["output_file"])
        try:
            with path.open("a") as f:
                json.dump(record, f)
                f.write("\n")
        except Exception as e:
            logger.error("Failed to save data to %s (%s)", str(path), e)

    async def send_alert(self, message: str, data: dict | None = None) -> None:
        url = self.config.get("webhook_url")
        if not url:
            return
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                payload = {
                    "agent": "NTP-Monitor",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "message": message,
                    "data": data,
                    "stats": self.stats,
                }
                await session.post(url, json=payload)
        except Exception as e:
            logger.debug("Alert send failed: %s", e)

    async def check_alerts(self, results: list[dict]) -> None:
        alerts = []
        drift_thr = float(self.config["alert_thresholds"]["drift_ms"])
        stratum_max = int(self.config["alert_thresholds"]["stratum_max"])
        unreachable_thr = int(self.config["alert_thresholds"]["server_unreachable_count"])

        ok = [r for r in results if r.get("status") == "success"]
        timeouts = [r for r in results if r.get("status") == "timeout"]

        for r in ok:
            off = abs(float(r.get("offset_ms", 0.0)))
            if off > drift_thr:
                alerts.append(f"High time drift {off:.2f} ms from {r.get('server')}")

            s = int(r.get("stratum", 0))
            if s > stratum_max:
                alerts.append(f"High stratum {s} from {r.get('server')}")

        if len(timeouts) >= unreachable_thr:
            alerts.append(f"Multiple NTP servers unreachable: {len(timeouts)}")

        for a in alerts:
            logger.warning("NTP ALERT: %s", a)
            await self.send_alert(a)

        # Simple backoff on heavy failure to be gentle to servers
        if len(ok) == 0 and len(results) > 0:
            self.backoff_until = time.time() + 120.0  # 2 minutes

    async def monitor_loop(self) -> None:
        logger.info("NTP Monitor starting (Quirit Edition)")
        while True:
            if time.time() < self.backoff_until:
                await asyncio.sleep(5.0)
                continue

            try:
                tasks = [self.query_ntp_server(s) for s in self.config["ntp_servers"]]
                results = await asyncio.gather(*tasks)

                # local chrony status
                local_status = await self.get_local_chrony_status()

                # persist results
                for r in results:
                    if isinstance(r, dict):
                        await self.save_data(r)
                if local_status:
                    await self.save_data({"agent": "ntp-monitor", **local_status})

                # summary
                ok = [r for r in results if r.get("status") == "success"]
                avg_offset = sum(r.get("offset_ms", 0.0) for r in ok) / len(ok) if ok else 0.0
                summary = {
                    "agent": "ntp-monitor",
                    "type": "ntp_summary",
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "servers_queried": len(self.config["ntp_servers"]),
                    "successful_responses": len(ok),
                    "average_offset_ms": avg_offset,
                    "stats": self.stats,
                    "local_chrony": local_status,
                }
                await self.save_data(summary)

                # alerts
                await self.check_alerts(results)

                logger.info("NTP Monitor: %d/%d OK, avg offset %.2f ms",
                            len(ok), len(self.config["ntp_servers"]), avg_offset)

            except Exception as e:
                logger.error("Error in monitor loop: %s", e)

            await asyncio.sleep(int(self.config["monitor_interval"]))


async def main():
    agent = NTPMonitor()
    try:
        await agent.monitor_loop()
    except KeyboardInterrupt:
        logger.info("NTP Monitor shutting down...")


if __name__ == "__main__":
    asyncio.run(main())

