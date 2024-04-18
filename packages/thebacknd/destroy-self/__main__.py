import thebacknd


def main(event):
    # TODO test for .vm_id and .killcode attrs.
    vm_id = event["vm_id"]
    vm_killcode = event["vm_killcode"]
    has_killcode = thebacknd.verify_killcode(vm_id, vm_killcode)
    if has_killcode:
        thebacknd.do_client.droplets.destroy_by_tag(tag_name=vm_id)
        return {"destroyed": vm_id}
    else:
        return {}
