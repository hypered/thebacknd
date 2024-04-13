import thebacknd

def list_droplets():
    xs = thebacknd.do_client.droplets.list(tag_name="thebacknd")
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

def main(args):
    xs = list_droplets()
    return xs
