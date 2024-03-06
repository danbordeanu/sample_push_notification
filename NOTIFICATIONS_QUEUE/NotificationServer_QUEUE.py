from concurrent.futures import ThreadPoolExecutor
import time
import os
import tornado.ioloop
import tornado.web
import tornado
import ast
import sys
from multiprocessing import Process
import uuid

from pymemcache.client import base
from memcached_stats import MemcachedStats

sys.path.append('../')
from COMMONS.Variables import VariablesShared
# Endpoints
from COMMONS.REST_tornado import UserSubscribeJobId
from COMMONS.REST_tornado import WebsocketConnectionMangerEndPoint
from COMMONS.REST_tornado import AuthentificationEndPoint
from COMMONS.Uat_Endpoint import get_job_info
from COMMONS.helpers import logger_settings


class hpcapi_jobId_monitor(tornado.web.RequestHandler):
    def __init__(self, name=None):
        self.ticket = ''
        self.name = name
        self.futures = []

    def future_jobId_watcher(self, jobid, ticket, userid):
        self.pool = ThreadPoolExecutor(1)
        self.futures.append(self.pool.submit(self.handler_jobId, jobid, ticket, userid))

    def handler_jobId(self, jobid, ticket, userid):
        logger_settings.logger.info(
            'hpcapi_jobId_monitor -  Starting job status for user:{0} and job:{1}'.format(userid, jobid))
        while True:
            try:
                logger_settings.logger.debug(
                    'hpcapi_jobId_monitor - :  jobid:{0} ticket:{1} userid:{2}'.format(jobid, ticket, userid))
                job_status_result = (get_job_info(VariablesShared.url_hpc, ticket, jobid))['data']['status']
            except Exception:
                logger_settings.logger.info(
                    'hpcapi_jobId_monitor/handler_jobId - Exception on getting the status of job {0}'.format(jobid))
                break

            if 'DONE' not in str(job_status_result):
                logger_settings.logger.info(
                    'hpcapi_jobId_monitor/handler_jobId - Waiting for jobid:{0} status'.format(jobid))
                time.sleep(int(VariablesShared.pooling))
            else:
                logger_settings.logger.info(
                    'hpcapi_jobId_monitor/handler_jobId - Job {0} has status {1}'.format(jobid, job_status_result))

                try:

                    clients_ready = base.Client((VariablesShared.mem_cache_host, int(VariablesShared.mem_cache_port)))
                    mem = MemcachedStats(VariablesShared.mem_cache_host, VariablesShared.mem_cache_port)

                    # Writing to memcached ---------------------------------------------
                    # dict with job status and job id to be written in memcache
                    making_the_data = {'STATUS': job_status_result, 'JOB_NUMBER': jobid}
                    # if there is no userid we need to set it _first
                    if clients_ready.get(userid) is None:
                        clients_ready.set(userid, making_the_data)
                    else:
                        #THIS WILL GENERATE A STR containing all the jobs with status DONE
                        # if userid created/set already, we need to append data, this will generate a str
                        clients_ready.append(userid, making_the_data)
                    logger_settings.logger.debug(
                        'hpcapi_jobId_monitor/handler_jobId - to memcached  {0} and mem {1}'.format(making_the_data,
                                                                                                    mem.keys()))


                except Exception:
                    logger_settings.logger.debug('hpcapi_jobId_monitor/handler_jobId -  problem writing on the socket')
                # to break from the loop
                break


def QueueDispatcher(channel, method, properties, body):
    # Fetch from the queue (actually tornado automagically pushes here since QueueDispatcher is the official consumer of the queue)
    '''
    :param channel:
    :param method:
    :param properties:
    :param body:
    '''
    x = ast.literal_eval(body)
    monitor = hpcapi_jobId_monitor()
    try:
        logger_settings.logger.debug('Do the ACK for first queue')
        VariablesShared.channel_global.basic_ack(
            delivery_tag=method.delivery_tag)  # To ack with the Queue to remove the message after processed
    except Exception:
        logger_settings.logger.error('Issues for ACK the stored event in the rabbitmq')

    monitor.future_jobId_watcher(x['jobid'], x['ticket'], x['userid'])
    logger_settings.logger.info('HPCMonitorServer/QueueDispatcher - Reaching end of QueueDispatcher!')


class SetUpHPCMonitorServer(object):
    def __init__(self):
        super(SetUpHPCMonitorServer, self).__init__()
        logger_settings.logger.info('Setting up the queue')
        self.workers = []
        self.MAX_WORKERS = int(VariablesShared.MAX_WORKERS)
        self.init_queue()

    def init_queue(self):

        # durable = True -> When RabbitMQ quits or crashes it will NOT forget the queues and messages 
        # prefetech_count = 1 -> tells RabbitMQ not to give more than one message to a worker at a time
        # VariablesShared.channel_global.queue_declare(queue=VariablesShared.queue_first, durable=True)
        VariablesShared.channel_global.queue_declare(queue=VariablesShared.queue_first)
        VariablesShared.channel_global.basic_qos(prefetch_size=0, prefetch_count=1, all_channels=True)

        for i in range(self.MAX_WORKERS):
            p = Process(self.worker())
            self.workers.append(p)
            p.start()

    def worker(self):
        try:
            VariablesShared.channel_global.basic_consume(QueueDispatcher, queue=VariablesShared.queue_first)
            VariablesShared.channel_global.start_consuming()
        except Exception:
            logger_settings.logger.error('NotificationsServer/worker- issue creating the queue')

    def terminate(self):
        for i in range(self.MAX_WORKERS):
            self.workers(i).terminate()

    # TODO re-write
    # def alive(self):
    # return self.process.is_alive()
    # for i in range(self.MAX_WORKERS):
    # self.workers(i).terminate()


class SetUpNoticationsServer(object):
    def __init__(self):
        super(SetUpNoticationsServer, self).__init__()
        self.process = ''
        self.init_run_server()
        logger_settings.logger.info('Starting push notification service')

    def init_run_server(self):
        self.process = Process(target=self.worker)
        self.process.start()

    def worker(self):


        settings = {
            'static_path': os.path.join(os.path.dirname(__file__), 'static'),
            'cookie_secret': str(uuid.uuid4()),
            'xsrf_cookies': True,

        }

        self.http_server = tornado.web.Application([
            (r'/(favicon.png)', tornado.web.StaticFileHandler, dict(path=settings['static_path'])),
            (r'/', AuthentificationEndPoint),
            (r'/register', WebsocketConnectionMangerEndPoint),
            # Ex. var ws = new WebSocket("ws://localhost:8888/register?userid=bordeanu");
            (r'/push', UserSubscribeJobId),
        ], **settings)

        try:
            # Starts the tornado object in a specific port after previous initialization
            self.http_server.listen(VariablesShared.app_port, VariablesShared.host)
            # Starts the listener for incoming requests from clients (webbrowser)
            tornado.ioloop.IOLoop.instance().start()
        except Exception, e:
            logger_settings.logger.error('Issues starting tornado {0}'.format(e))

    def pause_resume(self):
        self.running_flag.value = not self.running_flag.value

    def terminate(self):
        logger_settings.logger.info('Terminate queue')
        self.process.terminate()

    # def alive(self):
    # TODO fix this
    # return self.process.is_alive()


if __name__ == '__main__':
    try:

        NotificationsServer = SetUpNoticationsServer()
        HPCMonitorServer = SetUpHPCMonitorServer()

        # while True:
        # time.sleep(2)

        # read_servers = open('servers.pkl', 'rb')
        # servers_status = pickle.load(read_servers)
        # # print servers_status# this is a dict object
        # nn = str(servers_status['notifications'])
        # qq = str(servers_status['queue'])
        # read_servers.close()

        # TODO ternary
        # i = 5 if a > 7 else 0
        # translates into

        # if a > 7:
        # i = 5
        # else:
        # i = 0

        # TODO fix isalive
        # if '1' in nn:
        # if NotificationsServer.alive():
        # # print "alive"
        # pass
        # else:
        # logger_settings.logger.info('Restarting Server')
        # NotificationsServer.init_run_server()
        # elif '0' in nn:
        # logger_settings.logger.info('Stopping server')
        # NotificationsServer.terminate()

        # if '1' in qq:
        # if HPCMonitorServer.alive():
        # pass
        # else:
        # logger_settings.logger.info('Restarting Server')
        # HPCMonitorServer.init_queue()
        # elif '0' in qq:
        # logger_settings.logger.info('Terminating HPCMonitorServer')
        # HPCMonitorServer.terminate()

    #except IOError:
    except KeyboardInterrupt:
        # logger_settings.logger.info('piclke file not there will do one for you')
        # thread_list_status = {'queue': '1', 'notifications': '1'}
        # pk_file = open('servers.pkl', 'wb')
        # pickle.dump(thread_list_status, pk_file)
        # pk_file.close()
        logger_settings.logger.info('Closing everything down')
        sys.exit(0)
