#!/usr/bin/env python3

"""
Get information on IP address
"""

import json
import os
import sys

import ipinfo


###
# MAIN METHOD
###


def main():
    """Main method"""
    ip_address = check_args()

    # Get api key
    api_key = check_env("IPINFO_API_KEY")

    # Fetch details
    handler = ipinfo.getHandler(access_token=api_key)
    details = handler.getDetails(ip_address)

    # Display results
    print(json.dumps(details.all, indent=4))


def check_env(field):
    val = os.getenv(field)

    if not val:
        print(f"error: env var not found: %s" % field)
        sys.exit(1)

    return val


def check_args():
    if len(sys.argv) != 2:
        usage()

    return sys.argv[1]


def usage():
    script_name = sys.argv[0]
    print('usage: %s <ip_address>' % script_name)
    sys.exit()


####
# MAIN
####

# Invoke main method
if __name__ == "__main__":
    main()
