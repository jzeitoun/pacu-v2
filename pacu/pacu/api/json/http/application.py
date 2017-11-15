from pacu.profile import manager

web = manager.instance('web')

def get_info(req):
    return dict(port=web.port)
