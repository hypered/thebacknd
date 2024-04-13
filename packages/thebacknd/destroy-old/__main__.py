import thebacknd

def main(args):
    xs = thebacknd.list_droplets()
    r = {}
    for k, v in xs.items():
        if v["should_be_destroyed"] is True:
            r[k] = thebacknd.do_client.droplets.destroy(k)
    return r
