import json
import thebacknd

# Find the smallest number (starting from 1) that is not in a given list.
def smallest_missing_number(numbers):
    current = 1
    while True:
        if current not in numbers:
            return current
        current += 1

def existing_droplet_numbers():
    xs = thebacknd.do_client.droplets.list(tag_name="thebacknd")
    # The names looks like "thebacknd-123".
    ns = [int(x["name"].split('-')[-1]) for x in xs["droplets"]]
    return ns 

def create_droplet():
    numbers = existing_droplet_numbers()
    n = smallest_missing_number(numbers)
    vm_id = thebacknd.create_vm_id()

    user_data_content = {}
    per_vm_secret = thebacknd.create_killcode(vm_id)
    user_data_content["vm_id"] = vm_id
    user_data_content["vm_killcode"] = per_vm_secret
    # doctl serverless functions get thebacknd/destroy-self --url
    user_data_content["destroy_url"] = "https://faas-ams3-2a2df116.doserverless.co/api/v1/web/fn-85df16d9-63e4-4388-875f-28a44e683171/thebacknd/destroy-self"

    droplet_req = {
        "name": "thebacknd-{0}".format(n),
        "region": thebacknd.conf.vm_region,
        "size": thebacknd.conf.vm_size,
        "image": thebacknd.conf.vm_image,
        "ssh_keys": [thebacknd.ssh_key],
        # We pass the file content with user_data instead of
        # user_data_file because I don't know how to get content
        # back within the VM. With user_data, we can simple query
        # the metadata service at
        # http://169.254.169.254/metadata/v1/user-data.
        "user_data": json.dumps(user_data_content, indent=2),
        "tags": ["thebacknd", vm_id],
    }
    r = thebacknd.do_client.droplets.create(body=droplet_req)
    return r

def main(args):
      c = create_droplet()
      return {
          "create": c,
      }
