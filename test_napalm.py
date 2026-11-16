from napalm import get_network_driver
import yaml
import pandas as pd


with open("devices.yml","r") as f:
    inventory = yaml.safe_load(f)
    
audit_result =[]
    
for device in inventory["devices"] :
    print(f"auuditing {device['name']}")
    vendor_type = device["device_type"].split("_")[-1]
    driver = get_network_driver(vendor_type)

    dev = driver(
    hostname=device["host"], 
    username=device["username"], 
    password=device["password"])
    try :    
        dev.open()
    
        dev.load_merge_candidate(filename="condidate.txt")
        diff =dev.compare_config()
        print("Diffs found:")
        print(diff)

        dev.commit_config()

        facts = dev.get_facts()
        print(f"Device OS Version: {facts['os_version']}")
    
        audit_result.append({
            "Device_Name": device["name"],
            "IP_Address": device["host"],
            "Vendor": facts.get("vendor"),
            "Model": facts.get("model"),
            "OS_Version": facts.get("os_version"),
            "Serial_Number": facts.get("serial_number"),
            "Status": "Success"
        })
        dev.close()
    except Exception as e:
        print(f"Failed to audit {device['name']}: {e}")
        
        # 2. APPEND FAILURE DETAILS IF SOMETHING GOES WRONG
        audit_result.append({
            "Device_Name": device["name"],
            "IP_Address": device["host"],
            "Vendor": "N/A",
            "Model": "N/A",
            "OS_Version": "N/A",
            "Serial_Number": "N/A",
            "Status": f"Failed: {str(e)}"
        })


df = pd.DataFrame(audit_result)
output_file = "network_audit_report.csv"
df.to_csv(output_file, index=False)

print(f"\n[Success] Audit report successfully exported to {output_file}")