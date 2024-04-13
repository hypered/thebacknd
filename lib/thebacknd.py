# This is code that can be used by multiple "functions" within packages/.
# It is copied at build-time by the build.sh scripts of each "function".

import os
import pydo

# Environment variables are set in project.yml. In project.yml, they can be
# templated from a .env file. Don't write secrets directly in project.yml.
do_client = pydo.Client(token=os.getenv("DIGITALOCEAN_ACCESS_TOKEN"))

# Fingerprint or ID of an SSH key to embed in a created virtual machine. Must
# already be known from DigitalOcean.
ssh_key = os.getenv("EMBED_SSH_KEY")

def list_droplets():
    xs = do_client.droplets.list(tag_name="thebacknd")
    r = {}
    for x in xs["droplets"]:
        # Normally, we already filter against this tag above,
        # but better safe than sorry.
        if "thebacknd" in x["tags"]:
            r[x["id"]] = {
                "name": x["name"],
                "image-name": x["image"]["name"],
                "image-description": x["image"]["description"],
                "created_at": x["created_at"]
            }
            public_ips = [
                network["ip_address"] for network in x["networks"]["v4"]
                if network["type"] == "public"
            ]
            r[x["id"]]["public_ips"] = public_ips
            if False:
                r[x["id"]]["debug"] = x
    return r
