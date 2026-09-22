# Purpose

This is just a quick Python script I wrote up to refresh some programming skills I had forgotten as well as to try and incorporate some new coding practices. This script uses the FortiManager API to pull a list of FortiGate devices and export the data into a CSV file.

## Installation

After cloning the github repository, move to the directory in a terminal and run: `pipenv install`

If you don't have *pipenv* installed, from your terminal run: `pip install pipenv`

## FortiManager

Check out [Fortinet's Document Library](https://docs.fortinet.com/document/fortimanager/8.0.1/administration-guide/797124/creating-administrators-for-the-fortimanager-api) if you need help creating an API Administrator, Access Profile, Token, and so on.

## Script Usage

After cloning the project, create a __.env__ file within the directory. Define two string variables called 'fmg_ip' and 'api_token' that contain those bits of information relevant to your instances.

From the project directory, install the dependencies by running `pipenv install` and then run the script with your virtual environment by running `pipenv run python list_assets.py`

After the script completes, you should now have a *devices.csv* file in your directory that contains the pulled information on each device.

## Disclaimer

__*Use at your own risk*__

These example configurations were a learning tool for me to figure out what works for what I was trying to do, what didn't work, and maybe even a little bit as to why. I make no claims that this is the best way, or even the correct way, to configure devices utilizing this technology. What worked for me in a certain situation may not work for you, etc. I encourage you to take the time to learn and try these things out yourself and make your own judgments.
