import tornado.ioloop
import tornado.web
import os
import sys
from helpers import logger_settings
import uuid

sys.path.append('../')
from COMMONS.JobIdEndpoint import HpcapiJobIdEndPoint
from COMMONS.Variables import VariablesShared
# 
from COMMONS.REST_tornado import WebsocketConnectionMangerEndPoint
from COMMONS.REST_tornado import AuthentificationEndPoint

'''
A mock up for a real endpoint
it returns 2 strings + ip
Pass an instance of an obj (tornado.web.RequestHandler) to the contructor
and then websocket_ has acces to all the associated methods
'''


def notificationsserver():
    settings = {
        'static_path': os.path.join(os.path.dirname(__file__), 'static'),
        'cookie_secret': str(uuid.uuid4()),
        'xsrf_cookies': True
    }
    logger_settings.logger.info('Starting server on {0} and listening on port:{1}'.format(VariablesShared.host,
                                                                                          VariablesShared.app_port))
    return tornado.web.Application([
        # favicon is the icon that will be displayed by default in browser when accesing "/push"
        (r'/(favicon.png)', tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
        (r'/', AuthentificationEndPoint),
        (r'/register', WebsocketConnectionMangerEndPoint),
        # TODO: put all the tornado stuff in a class, call directly the UAT_endpoints 
        # and remove the file HpcapiJobIdEndPoint
        (r'/push', HpcapiJobIdEndPoint),
        # Ex. userid=dan&token=bla.host.com&jobid=289
    ], **settings)


if __name__ == '__main__':
    try:
        '''
        # Creates an instance of tornado
        # 1. Websocket <- to register the client (webbrowser)
        # 2. Rest api call: GET <- ask for job status
        # 3. Rest api call: GET <- return a string used for authentication (known as "cookie")
        '''
        # Starts the tornado object in a specific port after previous initialization 
        (notificationsserver()).listen(VariablesShared.app_port, VariablesShared.host)
        # Starts the listener for incoming requests from clients (webbrowser)
        tornado.ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logger_settings.logger.info('I get it, wait ,closing...')
