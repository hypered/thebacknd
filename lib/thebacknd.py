# This is code that can be used by multiple "functions" within packages/.
# It is copied at build-time by the build.sh scripts of each "function".

import datetime
import os
import pydo
from types import SimpleNamespace

# Environment variables are set in project.yml. In project.yml, they can be
# templated from a .env file. Don't write secrets directly in project.yml.
do_client = pydo.Client(token=os.getenv("DIGITALOCEAN_ACCESS_TOKEN"))

# Fingerprint or ID of an SSH key to embed in a created virtual machine. Must
# already be known from DigitalOcean.
ssh_key = os.getenv("EMBED_SSH_KEY")

# Things should be configurable. I guess we'll need to update the build.sh
# scripts to copy some user-defined Python code or JSON file, or whatever
# later.
conf = SimpleNamespace()

# After how many minutes a virtual machine must be destroyed.
conf.old_minutes = 60

# Values passed to do_client.droplets.create().
conf.vm_region = "ams3"
conf.vm_size = "s-1vcpu-1gb"
conf.vm_image = "154099004" # ID of thebacknd-base custom image.

def list_droplets():
    xs = do_client.droplets.list(tag_name="thebacknd")
    r = {}
    for x in xs["droplets"]:
        # Normally, we already filter against this tag above,
        # but better safe than sorry.
        if "thebacknd" in x["tags"]:
            r[x["id"]] = {
                "name": x["name"],
                "image_name": x["image"]["name"],
                "image_description": x["image"]["description"],
                "created_at": x["created_at"]
            }

            public_ips = [
                network["ip_address"] for network in x["networks"]["v4"]
                if network["type"] == "public"
            ]
            r[x["id"]] |= {
                "public_ips": public_ips,
            }

            created_at = datetime.datetime.strptime(x["created_at"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=datetime.timezone.utc)
            old_age = datetime.timedelta(minutes=conf.old_minutes)
            old_datetime = created_at + old_age
            current_datetime = datetime.datetime.now(datetime.UTC)
            is_too_old = old_datetime < current_datetime
            r[x["id"]] |= {
                "should_be_destroyed_at": old_datetime.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "should_be_destroyed": is_too_old,
            }

            if False:
                r[x["id"]]["debug"] = x
    return r
