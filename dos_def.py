#!/usr/bin/env python3
import os
import subprocess
import re
from datetime import datetime

# Colors for terminal output
red = "\033[1;31m"
green = "\033[1;32m"
yellow = "\033[1;33m"
blue = "\033[1;34m"
purple = "\033[1;35m"
cyan = "\033[1;36m"
reset = "\033[0m"

logo = blue + r"""
######################################################
  ___  _     ______      __               _           
 / _ \(_)    |  _  \    / _|             | |          
/ /_\ \_ _ __| | | |___| |_ ___ _ __   __| | ___ _ __ 
|  _  | | '__| | | / _ \  _/ _ \ '_ \ / _` |/ _ \ '__|
| | | | | |  | |/ /  __/ ||  __/ | | | (_| |  __/ |   
\_| |_/_|_|  |___/ \___|_| \___|_| |_|\__,_|\___|_|   
                                                      
                                                      
######################################################                        
""" + reset + "\n\n"


def check_sudo():
    """Verify sudo privileges."""
    if not "SUDO_UID" in os.environ.keys():
        print(f"{red}[!] Please run as a root.{reset}")
        exit()

def get_wifi_interface():
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
        

def monitor_deauth(interface, threshold=10):
    """Monitor for deauthentication attacks"""
    print(f"{green}[+] Monitoring {interface} for deauth attacks...{reset}")
    print(f"{yellow}[*] Threshold: {threshold} deauth frames/minute{reset}")
    
    try:
        # we start tshark in background to capture deauth frames
        cmd = [
            "tshark",
            "-i", interface,
            "-Y", "wlan.fc.type_subtype == 0x000c",  # we filter only deauth frames
            "-T", "fields",
            "-e", "wlan.sa",  
            "-e", "wlan.da",  
            "-a", "duration:60"  
        ]
        
        while True:
            print(f"\n{blue}[*] Starting new monitoring cycle{reset}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            lines_list = result.stdout.strip().split('\n') # we make the lines a list
            
            # threshold=10 means that if we catch more than 10 deauth per minute it is probably an attack.Normal wifi has 1-2 per minute
            if len(lines_list) > threshold: 
                attackers = {}
                for line in lines_list:
                    if line:

                        attacker_mac, destination = line.split('\t')
                        if attacker_mac in attackers:
                            attackers[attacker_mac] += 1 #we count the attacks from each mac
                        else:
                            attackers[attacker_mac] = 1 #if he is new we add it with one attack (the first)
                
                print(f"{red}[!] DEAUTH ATTACK DETECTED!{reset}")
                print(f"{red}[!] {len(lines_list)} deauth frames in last minute{reset}")
                print(f"{yellow}[*] Attackers list:{reset}")
                for attacker_mac, counter in attackers.items():
                    print(f"{attacker_mac}: {counter} frames")
                
                # More protection measurements can be added here
                # Like change channel, enable protection and so on
                
            else:
                print(f"{green}[+] No attack detected ({len(lines_list)} deauth frames){reset}")
                
    except KeyboardInterrupt:
        print(f"\n{yellow}[*] Stopping monitor...{reset}")
    except Exception as e:
        print(f"{red}[!] Error: {e}{reset}")

def main():
    os.system("clear")
    print(logo)
    check_sudo()
    interface = get_wifi_interface()
    monitor_deauth(interface)

if __name__ == "__main__":
    main()