"""
File: list_assets.py
Created by: Ben Cook
Last Updated: 24 Sep 2026

This python script uses API calls to FortiManager v7.2.x and the FortiCare Asset Protal
to query FortiGate device serial numbers and to compare where unique devices exist.
After pulling a subset of fields for each device, the script compares the two sources
and exports the data to a csv file.

You must create a '.env' file within the project directory and create several string variables:

  __fc_username__ - that contains your FortiCare username
  __fc_password__ - that contains your FortiCare password
  __fc_client_id__ - that contains your FortiCare client_id
  __fc_grant_type__ - that contains the type of grants for the FortiCare user
  __api_token__ that contains your private API token for FortiManager
  __fmg_ip__ that contains the ip address of your FortiManager

Full API documentation for FortiManager and other Fortinet products is available
on their Fortinet Developers Network website: 
https://fndn.fortinet.net/index.php
"""

import os
import sys
import urllib3

# Disabling the insecure warning because internal FMG certificate is likely to be self-signed
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
fc_username = os.getenv("fc_username")
fc_password = os.getenv("fc_password")
fc_client_id = os.getenv("fc_client_id")

fmg_url = "https://" + fmg_ip + "/jsonrpc"
ftnt_fac_url = "https://customerapiauth.fortinet.com/api/v1/oauth/token/"
ftnt_asset_url = "https://support.fortinet.com/ES/api/registration/v3/products/list"

fmg_headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer ' + api_token
}

ftnt_fac_headers = {
    "Content-Type": "application/json"
}

# FortiManager Section

fmg_payload = json.dumps({
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
        "build",
        "version"
      ],
      #"filter": [
      #  "conn_status",
      #  "--",
      #  "up"
      #],
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

# Requests will ignore the FortiManager certificate and set a connection timeout limit

try:
  response = requests.request("POST", fmg_url, headers=fmg_headers, data=fmg_payload, verify=False,timeout=(3.05, 27))
except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as errc:
  raise SystemExit(errc)

fmg_data = (response.json())
# print(json.dumps(fmg_data, indent=4, sort_keys=True))

fmg_devices = []

for item in fmg_data['result'][0]['data']:
  fmg_devices.append(item)

for item in fmg_devices:
  item['last_checked'] = datetime.fromtimestamp(item['last_checked']).strftime('%Y-%m-%d %H:%M:%S')  

fmg_device_sn = []

for item in fmg_devices:
  fmg_device_sn.append(item['sn'])

print("FortiManager Section Completed Successfully\n")

# FortiCare Asset Portal Section

ftnt_assets = []

def query_asset_portal(pattern):
  # Needs either serialNumber (exact or pattern) or expireBefore as required values

  ftnt_fac_payload = {
      "username": fc_username,
      "password": fc_password,
      "client_id": fc_client_id,
      "grant_type": "password"
  }

  ftnt_fac_response = requests.post(ftnt_fac_url, headers=ftnt_fac_headers,json=ftnt_fac_payload,allow_redirects=False)

  ftnt_fac_access_token = ftnt_fac_response.json()['access_token']
  ftnt_fac_refresh_token = ftnt_fac_response.json()['refresh_token']

  ftnt_asset_headers = {
      "Content-Type": "application/json",
      "Authorization": "Bearer " + ftnt_fac_access_token
  }

  ftnt_asset_payload = {
    # "accountId": 854651
    "serialNumber": pattern, # specific or pattern like FGT, FGVM, FGR, FR, S, SR, FP, etc.
    # "productModel": "FortiGate 90D***", 
    # "expireBefore": "2019-01-20T10:11:11-8:00",
    # "status": "Registered"
  }

  ftnt_asset_response = requests.post(ftnt_asset_url,headers=ftnt_asset_headers,json=ftnt_asset_payload,allow_redirects=False)

  # return a dictionary
  data = ftnt_asset_response.json()

  if data['message'] == 'No product found':
    print("No matching products found in the asset portal. Exiting.")
    sys.exit(1)

  # grabs just the assets section of the return
  data_dict = data['assets']

  # choose which fields specifically to use when filtering down the data_dict
  data_keys = ['status', 'serialNumber', 'registrationDate', 'productModel', 'isDecommissioned', 'description']

  for item in data_dict:
      new_data_dict = {k: item[k] for k in data_keys if k in item}
      ftnt_assets.append(new_data_dict)

  # print(json.dumps(assets,indent=4,sort_keys=True))
  return ftnt_assets

sn_pattern = ["FGT", "FGVM", "FR"]

for item in sn_pattern:
    query_asset_portal(item)

fc_device_sn = []

for item in ftnt_assets:
  fc_device_sn.append(item['serialNumber'])

print("FortiCare Asset Portal Section Completed Successfully\n")

# Devices in FortiManager and not in FortiCare Asset Portal

# print("Devices in FortiManager and not in FortiCare Asset Portal")
unique_fmg_sn= (list(set(fmg_device_sn) - set(fc_device_sn)))
# print(unique_fmg_sn)
# print("\n")

csv_unique_fmg_sn = []

for item in unique_fmg_sn:
   csv_unique_fmg_sn.insert(-1,[item])

# print(csv_unique_fmg_sn)

# Devices in FortiCare Asset Portal and not in FortiManager

# print("Devices in FortiManager and not in FortiCare Asset Portal")
unique_ftnt_sn = (list(set(fc_device_sn) - set(fmg_device_sn)))
# print(unique_ftnt_sn)
# print("\n")

csv_unique_ftnt_sn = []

for item in unique_ftnt_sn:
   csv_unique_ftnt_sn.insert(-1,[item])

# Generate CSV file to identify unique values in FortiManager and FortiCare Asset Portal

with open('compare-devices-sn.csv', 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Devices in FortiManager and not in FortiCare Asset Portal"])
    writer.writerows(csv_unique_fmg_sn)
    writer.writerow(["Devices in FortiManager and not in FortiCare Asset Portal"])
    writer.writerows(csv_unique_ftnt_sn)

print("script ran successfully")
sys.exit(0)