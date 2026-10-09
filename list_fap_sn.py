"""
File: list_fap_sn.py
Created by: Ben Cook
Last Updated: 6 Oct 2026

This python script uses an API call to FortiManager v7.4.x to iterate through each ADOM for 
locating FortiAP devices attached to managed FortiGate devices.

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
from collections import defaultdict

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

import urllib3

# Disabling the insecure warning because internal FMG certificate is likely to be self-signed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()
fmg_ip = os.getenv("fmg_ip")
api_token = os.getenv("api_token")

url = "https://" + fmg_ip + "/jsonrpc"

headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + api_token
}

# Pull list of ADOMs

adom_payload = json.dumps({
  "method": "get",
  "params": [
    {
      "fields": [
        "name",
        "os_ver"
      ],
      #"filter": [
      #  "conn_status",
      #  "--",
      #  "up"
      #],
      "sortings": [
        {
          "name": 1
        }
      ],
      "loadsub": 1,
      "url": "/dvmdb/adom"
    }
  ],
  "verbose": 1,
  "id": 1
})

# Requests will ignore the FortiManager certificate and set a timeout limit

try:
  adom_response = requests.request("POST", url, headers=headers, data=adom_payload, verify=False,timeout=(3.05, 27))
except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as errc:
  raise SystemExit(errc)

adom_data = (adom_response.json())
# print(json.dumps(adom_data, indent=4, sort_keys=True))

default_adoms = [
    "FortiAnalyzer", 
    "FortiAuthenticator", 
    "FortiCache", 
    "FortiCarrier", 
    "FortiClient", 
    "FortiDDoS", 
    "FortiDeceptor", 
    "FortiFirewall", 
    "FortiFirewallCarrier",
    "FortiMail", 
    "FortiManager", 
    "FortiProxy", 
    "FortiSandbox", 
    "FortiWeb", 
    "Syslog", 
    "Unmanaged_Devices", 
    "others", 
    "rootp"
]

all_adoms = []

for item in adom_data['result'][0]['data']:
  all_adoms.append(item['name'])

unique_adoms = (list(set(all_adoms) - set(default_adoms)))
# print(unique_adoms)

# Iterate through the list of ADOMs to find FortiGate device names to be used in ADOM FAP SN search

adom_devices = defaultdict(list)

def adom_fgt_query(adom):
  adom_fgt_payload = json.dumps({
    "method": "get",
    "params": [
      {
        "fields": [
          "hostname",
          "desc",
          "sn",
          "conn_status",
          "fap_cnt",
          "name",
        ],
        #"filter": [
        #  "conn_status",
        #  "--",
        #  "up"
        #],
        "sortings": [
          {
            "name": 1
          }
        ],
        "loadsub": 0,
        "url": "/dvmdb/adom/" + adom + "/device"
      }
    ],
    "verbose": 1,
    "id": 2
  })

  # Requests will ignore the FortiManager certificate and set a timeout limit

  try:
    adom_fgt_response = requests.request("POST", url, headers=headers, data=adom_fgt_payload, verify=False,timeout=(3.05, 27))
  except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as errc:
    raise SystemExit(errc)
  
  adom_fgt_data = (adom_fgt_response.json())
  #print(json.dumps(adom_fgt_data, indent=4, sort_keys=True))

  for item in adom_fgt_data['result'][0]['data']:
    adom_devices[adom].append(item['name'])


for item in unique_adoms:
   adom_fgt_query(item)

# Iterate through the list of ADOMs to find FortiAP serial numbers

fap_sn = []

def adom_fap_query(adom,name):
  adom_fap_payload = json.dumps({
    "method": "get",
    "params": [
      {
        "fields": [
          "apcfg-profile",
          "comment",
          "coordinate-latitude",
          "coordinate-longitude",
          "location",
          "name",
          "region",
          "wtp-id",
          "uuid"
        ],
        #"filter": [
        #  "conn_status",
        #  "==",
        #  "up"
        #],
        "sortings": [
          {
            "wtp-id": 1
          }
        ],
        "scope member": [
        {
          "name": name,
          "vdom": "root"
        }
        ],
        "loadsub": 0,
        "url": "/pm/config/adom/" + adom + "/obj/wireless-controller/wtp"
      }
    ],
    "verbose": 1,
    "id": 3
  })
  
  # Requests will ignore the FortiManager certificate and set a timeout limit
  
  try:
    adom_fap_response = requests.request("POST", url, headers=headers, data=adom_fap_payload, verify=False,timeout=(3.05, 27))
  except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as errc:
    raise SystemExit(errc)
  
  adom_fap_data = (adom_fap_response.json())
  #print(json.dumps(adom_fap_data, indent=4, sort_keys=True))
  
  for item in adom_fap_data['result'][0]['data']:
    #print(item['wtp-id'])
    fap_sn.append(item['wtp-id'])

# For each ADOM, loop through the devices to add FortiAP serial number to 'fap_sn' list

for key, list_value in adom_devices.items():
   for device in list_value:
      adom_fap_query(key,device)

#print(fap_sn)

# CSV export section

with open('fap-sn.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["FortiAP Serial Number"])
    writer.writerow(fap_sn)

print("Script ran successfully. Please open 'fap-sn.csv' to verify the output.")
sys.exit(0)