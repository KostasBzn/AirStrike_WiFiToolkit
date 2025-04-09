## 🔥 WiFi Deauth Tool (Python)

This is a simple Wi-Fi deauthentication tool, written in Python, designed for education and practice in pentesting.

---

 > ⚠️ **This tool is for educational and authorized testing purposes only!**

---

### 🧰 Features

- Colored CLI interface
- Automatic CSV `backup` from previous runs
- Band selection (2.4GHz / 5GHz / all)
- Real-time AP and client discovery
- Whitelist filtering MAC addresses you don't want to deauth
- Clean exit and monitor mode restore

---

### ✅ Requirements

- Python 3.8+
- Linux only (tested on Kali)
- Tools: `aircrack-ng`, `iw`, `ip`, `shutil`, etc. (preinstalled on Kali Linux)

### 🚀 How to Use

1. sudo python3 main.py
2. Select your wireless interface.
3. Switch to monitor mode.
4. Scan and select a network.
5. View connected clients.
6. Exclude MACs you don't want to target.
7. Launch the deauthentication.

### ⚠️ Legal Disclaimer

- This script is strictly for educational and authorized penetration testing use only. Do not use this tool on networks you don’t own or have explicit permission to test. Misuse is illegal and unethical.

