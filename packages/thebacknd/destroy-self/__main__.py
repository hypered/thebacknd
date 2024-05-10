import thebacknd


def main(event):
    # TODO test for .vm_id and .killcode attrs.
    vm_id = event["vm_id"]
    vm_killcode = event["vm_killcode"]
    r = thebacknd.destroy_self(vm_id, vm_killcode)
    return r
