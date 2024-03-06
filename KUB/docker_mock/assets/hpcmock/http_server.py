import sys
import threading
import urlparse
import BaseHTTPServer
import optparse
from helpers import logger_settings
from helpers.config_parser import config_params
import json


class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        '''
        :return:
        '''
        url = urlparse.urlparse(self.path)
        assert isinstance(url.query, object)
        query = urlparse.parse_qs(url.query)

        if url.path.startswith('/api/v2/job'):
            jobid = url.path.split('/', 4)[4]

            if not jobid:
                self.send_error(400)
                return

            logger_settings.logger.info('{0} Request job {1} status with  '
                                        'ticket {2}'.format(self.server.name(), jobid, query))

            my_corect_dict = {
                "success": True,
                "message": None,
                "data": {
                    "scratchFolder": "/SFS/hpcapi/dev/2ee2d01d-fe61-4edb-bc0b-36b9eff18d4f/aPsLvhgoRL.sh",
                    "status": "DONE",
                    "runtimeInfo": "-w n -shell yes -r n -l mem_reserve=128M -P normal -A appname=appdefault__isid=bordeanu__ipAddress=54_62_240_115",
                    "outLogPath": "/SFS/hpcapi/dev/2ee2d01d-fe61-4edb-bc0b-36b9eff18d4f/4c60f7aa-4c22-4cd1-8c45-1efd635d530a.out",
                    "errLogPath": "/SFS/hpcapi/dev/2ee2d01d-fe61-4edb-bc0b-36b9eff18d4f/4c60f7aa-4c22-4cd1-8c45-1efd635d530a.err",
                    "createDate": 1530780351000,
                    "pluginName": None,
                    "project": "normal",
                    "appName": "appdefault",
                    "ipAddress": "54_62_240_115",
                    "jobId": "289",
                    "local": False
                }
            }
            response = json.dumps(my_corect_dict)


            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(response)
            return

        else:
            logger_settings.logger.info('{0}: invalid GET:{1}'.format(self.server.name(), url.path))
            self.send_error(501)
            return


class HTTPServer(BaseHTTPServer.HTTPServer, threading.Thread):
    def __init__(self, name, port):
        '''

        :param name:
        :param port:
        '''
        BaseHTTPServer.HTTPServer.__init__(self, (config_params('portserver')['host'], port), RequestHandler)

        threading.Thread.__init__(self)
        assert isinstance(name, object)
        self.service_name = name
        assert isinstance(port, object)
        self.service_port = port

    def name(self):
        return self.service_name

    def run(self):
        logger_settings.logger.info('{0}: listening on port: {1}'.format(self.service_name, self.service_port))
        self.serve_forever()
        logger_settings.logger.info('{0}: stopped'.format(self.service_name))

    def stop(self):
        self.shutdown()


if __name__ == '__main__':

    parser = optparse.OptionParser()
    parser.add_option('--http-port', dest='http_port', type='int', default=config_params('portserver')['port'],
                      help='HPC-API JOBID MOCK HTTP server listen port')
    (opts, args) = parser.parse_args()
    if args:
        logger_settings.logger.info('no args')
        parser.error('no arguments allowed')
        sys.exit()
    try:
        httpd = HTTPServer('http', opts.http_port)
        httpd.start()
    except KeyboardInterrupt:
        httpd.stop()
        httpd.join()

    logger_settings.logger.info('Starting HPC-API JOBID MOCK Server')
    sys.exit()
