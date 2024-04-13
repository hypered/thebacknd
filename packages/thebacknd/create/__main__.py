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
    droplet_req = {
        "name": "thebacknd-{0}".format(n),
        "region": "ams3",
        "size": "s-1vcpu-1gb",
        "image": "debian-12-x64",
        "ssh_keys": [thebacknd.ssh_key],
        "tags": ["thebacknd"],
    }
    r = thebacknd.do_client.droplets.create(body=droplet_req)
    return r

def main(args):
      c = create_droplet()
      return {
          "create": c,
      }
