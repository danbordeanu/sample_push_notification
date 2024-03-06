import threading
from multiprocessing import Process
from pymemcache.client import base
from memcached_stats import MemcachedStats
import tornado.web
from helpers import logger_settings
import time
import json
from tornado import websocket
import uuid
from Variables import VariablesShared
import ast


# QUEUE stuff ==============================================================

# Fetch from the queue  and write to memcache
def QueueDispatcher(channel, method, properties, body):
        # Reading memcached ------------------------------------------------
    try:
        # VariablesShared.channel_global2.basic_ack(delivery_tag=method.delivery_tag)  # To ack with the Queue to remove the message after processed
        clients_ready = base.Client((VariablesShared.mem_cache_host, int(VariablesShared.mem_cache_port)))
        mem = MemcachedStats(VariablesShared.mem_cache_host, VariablesShared.mem_cache_port)

        # Getting the message from the queue -------------------------------
        x = ast.literal_eval(body)
        VariablesShared.channel_global2.basic_ack(delivery_tag=method.delivery_tag)  # To ack with the Queue to remove the message after processed
        logger_settings.logger.debug('REST_tornado/QueueDispatcher queue_second [userid:jobid:job status] - [{0}:{1}:{2}'.format(x['userid'],x['jobid'],x['job_status']))

        # Writing to memcached ---------------------------------------------
        # dict with job stus and job id to be written in memcache
        making_the_data = {'STATUS': x['job_status'], 'JOB_NUMBER': x['jobid']}
        clients_ready.set(x['userid'], making_the_data)
        logger_settings.logger.debug('wirint  {0} and mem {1}'.format(making_the_data, mem.keys()))

        print 'REST_tornado/QueueDispatcher - memcache {0}'.format(clients_ready.get(x['userid']))

        # mem = MemcachedStats(VariablesShared.mem_cache_host, VariablesShared.mem_cache_port)
        logger_settings.logger.debug('Memcache keys: {0}'.format(mem.keys()))

        logger_settings.logger.info('REST_tornado/QueueDispatcher Reaching end of QueueDispatcher!')

    except Exception:
        # TODO proper error handling
        logger_settings.logger.error('REST_tornado/QueueDispatcher - Issues writing to the memcache or reading from Queue')

class Queue_second(threading.Thread):

    def __init__(self):

        super(Queue_second, self).__init__()
        # super(SetUpNoticationsServer, self).__init__()
        # self.process=''
        logger_settings.logger.info('Starting second queue')
        self.workers = []

        self.queue_second_init()
        # self.process = Process(target=self.queue_second_init)
        # self.process.start()


    def queue_second_init(self):

        VariablesShared.channel_global2.queue_declare(queue=VariablesShared.queue_second)
        VariablesShared.channel_global2.basic_qos(prefetch_size=0, prefetch_count=1, all_channels=True)


        for i in range(VariablesShared.MAX_WORKERS):

            time.sleep(1)
            logger_settings.logger.error('worker .........................................')
            print i
            logger_settings.logger.error('worker .........................................')
            # Each process has an "ad-hoc" copy of the "sockets"
            p = Process(target=self.worker)
            self.workers.append(p)
            p.start()



    # #
    def worker(self):
        try:
            VariablesShared.channel_global2.basic_consume(QueueDispatcher, queue=VariablesShared.queue_second)
            VariablesShared.channel_global2.start_consuming()
        except Exception as e:
            print ''
            print ''
            print ''
            logger_settings.logger.error('REST_tornado/worker- issue perhaps consuming queue_second')
            print ''
            print ''
            print ''
            exit


