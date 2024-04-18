import thebacknd


def destroy_all_droplets():
    r = thebacknd.do_client.droplets.destroy_by_tag(tag_name="thebacknd")
    return r


def main(args):
    d = destroy_all_droplets()
    return {
        "destroy": d,
    }
