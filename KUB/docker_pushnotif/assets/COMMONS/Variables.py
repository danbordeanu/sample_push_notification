from helpers.config_parser import config_params
import pika
import os


class VariablesShared(object):
    # if there is no env var for HPC_APIURL, use the one from config.ini
    url_hpc = os.environ.get('HPC_APIURL', config_params('urlhpc')['url'])
    # push notification app settins
    app_port = config_params('portserver')['port']
    host = config_params('portserver')['host']
    cookie = config_params('cookie')['name']
    pooling = config_params('portserver')['pooling']

    # memcache settins
    #take memcached host value from env(value is set by docker compose). If not preent, fallback to config:localhost
    mem_cache_host = os.environ.get('MEMCACHED_HOST', config_params('memcache')['host'])
    mem_cache_port = config_params('memcache')['port']

    # queue name
    queue_first = config_params('rabbitmq')['queue_first']
    queue_second = config_params('rabbitmq')['queue_second']

    # Queue port,heartbeat, password

    # WHEN RUNNING ON LOCALHOST, GUEST/GUEST IS USED TO CONNECT TO RABBIT MQ
    # WHEN RUNNING IN DOCKER, WE NEED ADMIN/ADMIN ACCOUNT (RELAX, IS CREATED INSIDE OF DOCKER AUTOMAGICAL)

    # PLEASE RUN THIS ON YOUR LOCALMACHINE ___IF___ YOU NEED A DIFFERENT ACCOUNT
    # rabbitmqctl add_user admin admin
    # rabbitmqctl set_user_tags admin administrator
    # rabbitmqctl set_permissions -p / admin ".*" ".*" ".*"

    # take rabbit user and password from env var(values are set by the docker compose). If not present, fallback to config: guest/guest
    pika_username = os.environ.get('RABBITMQ_DEFAULT_USER', config_params('rabbitmq')['user'])
    pika_password = os.environ.get('RABBITMQ_DEFAULT_PASS', config_params('rabbitmq')['password'])
    # take rabbit host from env var(value is set by docker compose). If not present, fallback to config localhos
    pika_host = os.environ.get('RABBITMQ_HOST', config_params('rabbitmq')['host'])
    pika_credentials = pika.PlainCredentials(pika_username, pika_password)
    connection_settings = pika.ConnectionParameters(host=pika_host, port=int(config_params('rabbitmq')['port']), heartbeat=0, credentials=pika_credentials)

    # Queue workers
    MAX_WORKERS = config_params('workers')['numbers']
                                                    

    # To connect to a broker on the host/port
    rabbit = pika.BlockingConnection(connection_settings)
    channel_global = rabbit.channel()

    rabbit2 = pika.BlockingConnection(connection_settings)
    channel_global2 = rabbit2.channel()

    if 'blockingconnection' not in str(rabbit).lower() and 'mock' not in str(rabbit).lower():
        raise Exception('Heartbeat runner requires a connection to rabbitmq-firstqueue as connection, '
                        'actually has {0}, a {1}'.format(str(rabbit), type(rabbit)))

    if rabbit.is_open is False:
        raise Exception('Heart runner\'s connection to rabbitmq-firstqueue should be open, is actually closed')

    if 'blockingconnection' not in str(rabbit2).lower() and 'mock' not in str(rabbit2).lower():
        raise Exception('Heartbeat runner requires a connection to rabbitmq-secongqueue as connection, '
                        'actually has {0}, a {1}'.format(str(rabbit), type(rabbit)))

    if rabbit2.is_open is False:
        raise Exception('Heart runner\'s connection to rabbitmq-secondqueue should be open, is actually closed')
