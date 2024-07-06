# This is code that can be used by multiple "functions" within packages/.
# It is copied at build-time by the .include files of each "function".

import boto3
import datetime
import hmac
import hashlib
import json
import os
import pydo
import secrets
from types import SimpleNamespace
import uuid

# Environment variables are set in project.yml. In project.yml, they can be
# templated from a .env file. Don't write secrets directly in project.yml.
do_client = pydo.Client(token=os.getenv("DIGITALOCEAN_ACCESS_TOKEN"))

s3_client = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("THEBACKND_ONCE_KEY_ID"),
    aws_secret_access_key=os.getenv("THEBACKND_ONCE_KEY_SECRET"),
    endpoint_url="https://ams3.digitaloceanspaces.com",
)

# Fingerprint or ID of an SSH key to embed in a created virtual machine. Must
# already be known from DigitalOcean.
ssh_key = os.getenv("EMBED_SSH_KEY")

# A secret known from thebacknd, from which to derive per-vm secrets, used by
# the VMs to request to be destroyed.
main_secret = os.getenv("THEBACKND_SECRET")

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

# Bucket name to store the one-time-urls content.
conf.once_bucket_name = "thebacknd"


# Generate VM ID. (DigitalOcean will also create one, but we'll know it only
# after spawning a VM. We need one for the per-vm secret before VM creation.)
def create_vm_id():
    return "thebacknd-{0}".format(uuid.uuid4())


# Per-VM secret derived from the main secret above, associated to a given VM ID.
def create_killcode(vm_id):
    secret_bytes = main_secret.encode()
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


# Find the smallest number (starting from 1) that is not in a given list.
def smallest_missing_number(numbers):
    current = 1
    while True:
        if current not in numbers:
            return current
        current += 1


def existing_droplet_numbers():
    xs = do_client.droplets.list(tag_name="thebacknd")
    # The names looks like "thebacknd-123".
    ns = [int(x["name"].split("-")[-1]) for x in xs["droplets"]]
    return ns


def create_droplet(nix_toplevel, nix_binary):
    numbers = existing_droplet_numbers()
    n = smallest_missing_number(numbers)
    vm_id = create_vm_id()

    system_input = {}
    per_vm_secret = create_killcode(vm_id)
    system_input["vm_id"] = vm_id
    system_input["vm_killcode"] = per_vm_secret

    if nix_toplevel:
        system_input["nix_toplevel"] = nix_toplevel
    if nix_binary:
        system_input["nix_binary"] = nix_binary

    key = put_once_content(system_input)

    user_data_content = {}
    user_data_content["system_input_key"] = key
    user_data_content[
        "once_url"
    ] = "https://faas-ams3-2a2df116.doserverless.co/api/v1/web/fn-85df16d9-63e4-4388-875f-28a44e683171/thebacknd/once"
    user_data_json = json.dumps(user_data_content, indent=2)

    print(f"Creating droplet with image {conf.vm_image}...")
    droplet_req = {
        "name": "thebacknd-{0}".format(n),
        "region": conf.vm_region,
        "size": conf.vm_size,
        "image": conf.vm_image,
        "ssh_keys": [ssh_key],
        # We pass the file content with user_data instead of
        # user_data_file because I don't know how to get content
        # back within the VM. With user_data, we can simple query
        # the metadata service at
        # http://169.254.169.254/metadata/v1/user-data.
        "user_data": user_data_json,
        "tags": ["thebacknd", vm_id],
    }
    c = do_client.droplets.create(body=droplet_req)
    return {
        "create": c,
    }


# Retrieved the dict saved to S3 in create_droplet, augmented with credentials.
def get_system_input(key):
    system_input = get_once_content(key)
    if system_input is None:
        return None

    # doctl serverless functions get thebacknd/destroy-self --url
    # TODO Must be automatically discovered.
    system_input[
        "destroy_url"
    ] = "https://faas-ams3-2a2df116.doserverless.co/api/v1/web/fn-85df16d9-63e4-4388-875f-28a44e683171/thebacknd/destroy-self"
    system_input["nix_cache"] = conf.nix_cache
    system_input["nix_trusted_key"] = conf.nix_trusted_key
    system_input["nix_cache_key_id"] = conf.nix_cache_key_id
    system_input["nix_cache_key_secret"] = conf.nix_cache_key_secret
    return system_input


def destroy_all_droplets():
    d = do_client.droplets.destroy_by_tag(tag_name="thebacknd")
    return {
        "destroy": d,
    }


def destroy_old_droplets():
    xs = list_droplets()
    r = {}
    for k, v in xs.items():
        if v["should_be_destroyed"] is True:
            r[k] = do_client.droplets.destroy(k)
    return r


def destroy_self(vm_id, vm_killcode):
    has_killcode = verify_killcode(vm_id, vm_killcode)
    if has_killcode:
        do_client.droplets.destroy_by_tag(tag_name=vm_id)
        return {"destroyed": vm_id}
    else:
        return {}


# Store a dict to S3, returning a hard-to-guess key.
def put_once_content(value):
    date_str = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")
    key = f"once/{date_str}/{secrets.token_hex()}"
    value_json = json.dumps(value, indent=2)
    s3_client.put_object(Bucket=conf.once_bucket_name, Key=key, Body=value_json)
    return key


# Retrieve a dict from S3 using its key, and delete it from S3.
def get_once_content(key):
    try:
        response = s3_client.get_object(Bucket=conf.once_bucket_name, Key=key)
        value = response["Body"].read().decode("utf-8")
        s3_client.delete_object(Bucket=conf.once_bucket_name, Key=key)
        return json.loads(value)
    except s3_client.exceptions.NoSuchKey:
        return None


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

    def run_create(nix_toplevel, nix_binary):
        r = create_droplet(
            nix_toplevel=nix_toplevel,
            nix_binary=nix_binary,
        )
        pprint.pp(r)

    def run_destroy_all():
        r = destroy_all_droplets()
        pprint.pp(r)

    def run_destroy_old():
        r = destroy_old_droplets()
        pprint.pp(r)

    def run_destroy_self(vm_id, vm_killcode):
        r = destroy_self(vm_id, vm_killcode)
        pprint.pp(r)

    parser = argparse.ArgumentParser(
        description="Ephemeral virtual machines in one command."
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    parser_list = subparsers.add_parser("list", help="List virtual machines")
    parser_list.set_defaults(func=lambda args: run_list())

    parser_create = subparsers.add_parser("create", help="Create a virtual machine")
    parser_create.add_argument(
        "--toplevel", type=str, default=None, help="Specify a toplevel to deploy."
    )
    parser_create.add_argument(
        "--binary", type=str, default=None, help="Specify a binary to run."
    )
    parser_create.set_defaults(
        func=lambda args: run_create(nix_toplevel=args.toplevel, nix_binary=args.binary)
    )

    parser_destroy_all = subparsers.add_parser(
        "destroy-all", help="Destroy all virtual machines"
    )
    parser_destroy_all.set_defaults(func=lambda args: run_destroy_all())

    parser_destroy_old = subparsers.add_parser(
        "destroy-old", help="Destroy old virtual machines"
    )
    parser_destroy_old.set_defaults(func=lambda args: run_destroy_old())

    parser_destroy_self = subparsers.add_parser(
        "destroy-self", help="Destroy a virtual machine given a killcode"
    )
    parser_destroy_self.add_argument(
        "--vm-id", type=str, help="Specify a virtual machine ID."
    )
    parser_destroy_self.add_argument("--killcode", type=str, help="Specify a killcode.")
    parser_destroy_self.set_defaults(
        func=lambda args: run_destroy_self(args.vm_id, args.killcode)
    )

    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
