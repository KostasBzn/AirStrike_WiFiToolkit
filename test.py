import os
import csv
def clients():
    active_clients = set()
    os.system("clear")
    for file_name in os.listdir():
        fieldnames = ["Station MAC", "First time seen", "Last time seen", "Power", "packets", "BSSID", "Probed ESSIDs"]
        if ".csv" in file_name and file_name.startswith("clients"):
            with open(file_name) as csv_h:
                csv_h.seek(0)
                csv_reader = csv.DictReader(csv_h, fieldnames=fieldnames)
                for index, row in enumerate(csv_reader):
                    print(f"{index} : {row["Station MAC"]}")
                    if index < 3:
                        pass
                    else:
                        active_clients.add(row["Station MAC"])
    print(active_clients)
   
    

clients()