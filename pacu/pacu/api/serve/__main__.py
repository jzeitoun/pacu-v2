from ... import profile

from tornado.wsgi import WSGIContainer
from tornado.httpserver import HTTPServer
from pacu.core.io.scanbox.model import server

def main(**kwargs):
    profile.manager.currents.update(kwargs)
    profile.manager.print_status()
    log, web = profile.manager.instances('log', 'web')
    if NotImplemented in [web]:
        log.error('Unable to initialize profiles. Stop...')
    else:
        try:
            log.debug(web.format_status())
            app = server.create_endpoint()
            HTTPServer(WSGIContainer(app)).listen(web.port + 30000)
            return web.run()
        except Exception as e:
            log.error('Failed to run app. ({!s})'.format(e))
if __name__ == '__api_main__':
    main()
