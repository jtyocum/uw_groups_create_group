"""
Tool to sync users from UW Groups to local system groups.
"""

import argparse
import sys
import os
import yaml
import requests
import json
import re


def group_id(id):
    if re.match("^uw?_[a-z0-9_-]*$", id):
        return id
    else:
        raise ValueError


def create_uw_group(
    gws_base_url: str,
    gws_ca_cert: str,
    gws_client_cert: str,
    gws_client_key: str,
    uw_group: str,
    uw_group_admins: str,
) -> int:
    """
    Create UW Group via Groups Web Service.
    """

    group_parameters = json.dumps(
        {"data": {"id": uw_group, "admins": [{"type": "group", "id": uw_group_admins}]}}
    )

    headers = {"Content-Type": "application/json"}

    r = requests.put(
        gws_base_url + "/group/" + uw_group,
        data=group_parameters,
        headers=headers,
        verify=gws_ca_cert,
        cert=(gws_client_cert, gws_client_key),
    )

    return r.status_code


def main():
    conf_path = (
        os.path.dirname(os.path.abspath(__file__)) + r"/conf/groups_create_group.yml"
    )
    config = yaml.load(open(conf_path, "r"), Loader=yaml.SafeLoader)

    # Group Web Service base URL
    # Use API v3, https://wiki.cac.washington.edu/display/infra/Groups+Service+API+v3
    gws_base_url = config["gws_base_url"]
    # GWS requires certificate based auth
    gws_ca_cert = config["gws_ca_cert"]
    gws_client_cert = config["gws_client_cert"]
    gws_client_key = config["gws_client_key"]

    parser = argparse.ArgumentParser()
    parser.add_argument("uw_group", type=group_id, help="UW Group Id")
    parser.add_argument(
        "uw_group_admins", type=group_id, help="UW Group to administer the group"
    )
    args = parser.parse_args()

    try:
        status_code = create_uw_group(
            gws_base_url,
            gws_ca_cert,
            gws_client_cert,
            gws_client_key,
            args.uw_group,
            args.uw_group_admins,
        )
        print("STATUS: {0}".format(status_code))
    except Exception:
        print("FATAL: Error creating group?", sys.exc_info())
        sys.exit(1)

    return


if __name__ == "__main__":
    main()
