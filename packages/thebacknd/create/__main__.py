import thebacknd


def main(event):
    r = thebacknd.create_droplet(
        nix_toplevel=event.get("nix_toplevel", None),
        nix_binary=event.get("nix_binary", None),
    )
    return r
