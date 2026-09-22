"""
File: list_assets.py
Created by: Ben Cook
Last Updated: 22 Sep 2026

This python script uses an API call to FortiManager v7.4.x to query the device database.
After pulling a subset of fields for each device, the script exports the data to a csv file.

You must create a '.env' file within the project directory and create two string variables:

  'api_token' that contains your private API token for FortiManager.
  'fmg_ip' that contains the ip address of your FortiManager.

Full API documentation for FortiManager and other Fortinet products is available
on their Fortinet Developers Network website: 
https://fndn.fortinet.net/index.php?/fortiapi/5-fortimanager/
"""

import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    print(
      "Dotenv dependency not met.\n" +
      "Please install with pip install dotenv" 
    )
    sys.exit(1)

try:
    import requests
except ImportError:
    print(
        "Requests dependency not met.\n" +
        "Please install with pip install requests"
    )
    sys.exit(1)

try:
    import json
except ImportError:
    print(
        "JSON dependency not met.\n" +
        "Please install with pip install json"
    )
    sys.exit(1)

try:
    import csv
except ImportError:
    print(
        "Requests dependency not met.\n" +
        "Please install with pip install csv")
    sys.exit(1)

from datetime import datetime, timezone

load_dotenv()
fmg_ip = os.getenv("fmg_ip")
api_token = os.getenv("api_token")

url = "https://" + fmg_ip + "/jsonrpc"

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + api_token
}

# These fields can be changed to suit your own use case; sourced from FNDN

payload = json.dumps({
  "method": "get",
  "params": [
    {
      "fields": [
        "hostname",
        "desc",
        "sn",
        "conn_status",
        "conn_mode",
        "fap_cnt",
        "fsw_cnt",
        "hw_generation",
        "hw_rev_major",
        "hw_rev_minor",
        "ip",
        "last_checked",
        "last_resync",
        "latitude",
        "longitude",
        "location_from",
        "name",
        "os_ver",
        "patch",
        "version"
      ],
      "sortings": [
        {
          "sn": 1
        }
      ],
      "loadsub": 0,
      "url": "/dvmdb/device"
    }
  ],
  "verbose": 1,
  "id": 1
})

# This call with requests will ignore the FortiManager certificate

response = requests.request("POST", url, headers=headers, data=payload, verify=False)

data = (response.json())
# print(json.dumps(data, indent=4, sort_keys=True))

devices = []

for item in data['result'][0]['data']:
  devices.append(item)

for item in devices:
  item['last_checked'] = datetime.fromtimestamp(item['last_checked']).strftime('%Y-%m-%d %H:%M:%S')  

csv_fields = []

for key in devices[0]:
  csv_fields.append(key)

with open('devices.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile,fieldnames=csv_fields)
    writer.writeheader()
    writer.writerows(devices)
