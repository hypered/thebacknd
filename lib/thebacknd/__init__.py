# This is code that can be used by multiple "functions" within packages/.
# It is copied at build-time by the .include files of each "function".

import datetime
import hmac
import hashlib
import os
import pydo
from types import SimpleNamespace
import uuid

# Environment variables are set in project.yml. In project.yml, they can be
# templated from a .env file. Don't write secrets directly in project.yml.
do_client = pydo.Client(token=os.getenv("DIGITALOCEAN_ACCESS_TOKEN"))

# Fingerprint or ID of an SSH key to embed in a created virtual machine. Must
# already be known from DigitalOcean.
ssh_key = os.getenv("EMBED_SSH_KEY")

# A secret known from thebacknd, from which to derive per-vm secrets, used by
# the VMs to request to be destroyed.
secret = os.getenv("THEBACKND_SECRET")

# Things should be configurable. I guess we'll need to update the build.sh
# scripts to copy some user-defined Python code or JSON file, or whatever
# later.
conf = SimpleNamespace()

# After how many minutes a virtual machine must be destroyed.
conf.old_minutes = 60

# Values passed to do_client.droplets.create().
conf.vm_region = "ams3"
conf.vm_size = "s-1vcpu-1gb"
conf.vm_image = os.getenv("VM_IMAGE", "debian-12-x64")
conf.nix_cache = os.getenv("NIX_CACHE")
conf.nix_trusted_key = os.getenv("NIX_TRUSTED_KEY")
conf.nix_cache_key_id = os.getenv("NIX_CACHE_KEY_ID")
conf.nix_cache_key_secret = os.getenv("NIX_CACHE_KEY_SECRET")


# Generate VM ID. (DigitalOcean will also create one, but we'll know it only
# after spawning a VM. We need one for the per-vm secret before VM creation.)
def create_vm_id():
    return "thebacknd-{0}".format(uuid.uuid4())


# Per-VM secret derived from the main secret above, associated to a given VM ID.
def create_killcode(vm_id):
    secret_bytes = secret.encode()
    identifier_bytes = vm_id.encode()
    hmac_obj = hmac.new(secret_bytes, identifier_bytes, hashlib.sha256)
    per_vm_secret = hmac_obj.hexdigest()
    return per_vm_secret


def verify_killcode(vm_id, killcode):
    expected_hmac = create_killcode(vm_id)
    return hmac.compare_digest(killcode, expected_hmac)


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
                "created_at": x["created_at"],
            }

            public_ips = [
                network["ip_address"]
                for network in x["networks"]["v4"]
                if network["type"] == "public"
            ]
            r[x["id"]] |= {
                "public_ips": public_ips,
            }

            created_at = datetime.datetime.strptime(
                x["created_at"], "%Y-%m-%dT%H:%M:%SZ"
            ).replace(tzinfo=datetime.timezone.utc)
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

def destroy_all_droplets():
    d = do_client.droplets.destroy_by_tag(tag_name="thebacknd")
    return {
        "destroy": d,
    }

def cli():
    """
    Drive the above functions from the command-line (i.e. locally instead of
    remotely.

    For instance the "list" code can be run with both these commands:

        $ poetry run thebacknd list
        $ doctl serverless functions invoke thebacknd/list
    """
    import argparse
    import pprint

    def run_list():
        xs = list_droplets()
        pprint.pp(xs)

    def run_destroy_all():
        r = destroy_all_droplets()
        pprint.pp(r)

    parser = argparse.ArgumentParser(description="Ephemeral virtual machines in one command.")
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    parser_list = subparsers.add_parser('list', help='List virtual machines')
    parser_list.set_defaults(func=lambda args: run_list())

    parser_destroy_all = subparsers.add_parser('destroy-all', help='Destroy all virtual machines')
    parser_destroy_all.set_defaults(func=lambda args: run_destroy_all())

    args = parser.parse_args()
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()
