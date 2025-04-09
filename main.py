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
    if not "SUDO_UID" in os.environ.keys():
        print(f"{red}[!] Please run the tool with sudo privileges.{reset}")
        exit()

def backup_csv():
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
            print(f"{purple}[{index + 1}]{reset} {cyan}{item}{reset}")
        while True:
            try:
                choice = int(input(f"\n{yellow}[>]{reset} Please select the interface you want to use for the attack: ").strip())
                if 1 <= choice <= len(net_int):
                    print(f"{green}[+] {net_int[choice - 1]} connected.{reset}\n")
                    break
                else:
                    print(f"{red}[!]{reset} Please enter a number that corresponds with the choises available.")
            except ValueError as e:
                print(f"{red}[!] VallueError: {e}{reset}")
        return net_int[choice - 1]
        
def set_monitor_mode(inf):
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

#### Continue from here
def set_band_to_monitor(choice, intf):
    """Select 2.4GHz, 5GHz, or both) for monitoring."""
    while True:
        wifi__bands = ["bg (2.4Ghz)", "a (5Ghz)", "abg (Will be slower)"]
        try:
            choice = input(f"{yellow}[>]{reset} Please select the bands you want to scan from the list above: ")
            if choice == "0":
                subprocess.Popen(["airodump-ng", "--band", "bg", "-w", "file", "--write-interval", "1", "--output-format", "csv", intf], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif choice == "1":
                subprocess.Popen(["airodump-ng", "--band", "a", "-w", "file", "--write-interval", "1", "--output-format", "csv", intf], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)        
            elif choice == "2":
                subprocess.Popen(["airodump-ng", "--band", "abg", "-w", "file", "--write-interval", "1", "--output-format", "csv", intf], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                raise ValueError("Invalid input.")
        except (ValueError, Exception) as e:
            print(f"{red}[!] Error frequency selection: {reset}")

def scan_networks(inf):
    """Run airodump-ng to discover networks."""
    pass

def select_target(networks):
    """Display network menu and return user's choice."""
    pass

def get_clients(target_bssid, channel, interface):
    """Capture clients on target network."""
    pass

def filter_clients(clients, whitelist):
    """Exclude whitelisted MACs from attack."""
    pass

def deauth_attack(target_bssid, clients, interface):
    """Run deauth attack on selected clients."""
    pass

def restore_managed_mode(inf):
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
    #check_sudo()
    inter = get_wifi_int()

if __name__ == "__main__":
    main()