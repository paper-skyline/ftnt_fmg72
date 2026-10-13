# Purpose

This is just a quick Python script I wrote up to refresh some programming skills I had forgotten as well as to try and incorporate some new coding practices. 

The __list_assets.py__ script uses the FortiManager API to pull a list of FortiGate devices from the FortiManager device database and export the data into a CSV file.

The __list_fap_sn.py__ script uses the FortiManager API to pull a list of managed FortiAP device serial numbers from each FortiGate in the root ADOM and each other non-standard ADOM.

The __compare_fmg_fc_sn.py__ script uses a combination of the FortiManager API and the FortiCare Asset Portal API to pull FortiGate device serial numbers from each and do a comparison between the two. Useful if you're looking to see what assets exist in FortiManager but don't exist in FortiCare and vice versa.

## Installation

After cloning the github repository, move into the directory in a terminal and install the python package dependencies with run: `pipenv install`

If you don't have *pipenv* installed, from your terminal run: `pip install pipenv`

## FortiManager

Check out [Fortinet's Document Library](https://docs.fortinet.com/document/fortimanager/8.0.1/administration-guide/797124/creating-administrators-for-the-fortimanager-api) if you need help creating an API Administrator, Access Profile, Token, and so on.

## Script Usage

After cloning the project, you must create a '.env' file within the project directory and create several string variables:

  __fc_username__ - that contains your FortiCare username
  __fc_password__ - that contains your FortiCare password
  __fc_client_id__ - that contains your FortiCare client_id
  __fc_grant_type__ - that contains the type of grants for the FortiCare user
  __api_token__ that contains your private API token for FortiManager
  __fmg_ip__ that contains the ip address of your FortiManager

From the project directory, either activate the virtual environment shell by running `pipenv shell` and then run the script you want. Alternatively, you can run the script directly without activating the environment by `pipenv run python <script>`.

After the script completes, you should now have a corresponding _csv_ file in your directory that contains the pulled information based on the script executed.

## Disclaimer

__*Use at your own risk*__

These example configurations were a learning tool for me to figure out what works for what I was trying to do, what didn't work, and maybe even a little bit as to why. I make no claims that this is the best way, or even the correct way, to configure devices utilizing this technology. What worked for me in a certain situation may not work for you, etc. I encourage you to take the time to learn and try these things out yourself and make your own judgments.
