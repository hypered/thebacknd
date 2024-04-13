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
            }
    return r

def main(args):
    xs = list_droplets()
    return xs
