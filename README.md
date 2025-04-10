## WiFi Security Tool (Python)

This is a simple dual-purpose tool written in Python, for WiFi penetration testing penetration testing and deauthentication attack detection.

---

 > ⚠️ **This tool is for educational and authorized testing purposes only!**

---

### 1. Attacker Module (`dos_wifi.py`)

- Colored CLI interface
- Automatic CSV `backup` from previous runs
- Band selection (2.4GHz / 5GHz / both)
- Real-time AP and client discovery
- Whitelist filtering MAC addresses you don't want to deauth
- Clean exit and monitor mode restore

### 2. Defender Module (`dos_def.py`)
- Detects deauthentication attacks in real-time
- Identifies attacking devices
- Provides attack statistics
- Threat alerts.

---

### Requirements

- Python 3.8+
- Linux only (tested on Kali)
- Tools: `aircrack-ng`, `tshark`, `iw`, `ip`, `shutil`, etc. (all preinstalled on Kali Linux)
- Requires WiFi adaptor that supports `monitor` mode.

### Quick Start

1. sudo python3 dos_wifi.py (to lainch deauthentication)
2. sudo python3 dos_def.py (to capture and defend deauthentication)

### ⚠️ Ethical Disclaimer

- This script is strictly for educational and authorized penetration testing use only. Unauthorized use against networks you don't own is illegal.

