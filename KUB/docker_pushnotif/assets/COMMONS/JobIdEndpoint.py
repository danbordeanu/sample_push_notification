import tornado.web
import requests
from helpers import logger_settings
from helpers.Error import ExceptionType
from helpers.Error import UATError
import time
from concurrent.futures import ThreadPoolExecutor
import json
from Variables import VariablesShared




class HpcapiJobIdEndPoint(tornado.web.RequestHandler):
    # should be here from documentation of tornado
    def data_received(self, chunk):
        pass

    def get(self):
        VariablesShared.userid = str(self.get_argument('userid'))
        ticket = str(self.get_argument('ticket'))
        jobid = str(self.get_argument('jobid'))
        assert isinstance(VariablesShared.userid, str), 'Need user name in GET request'
        assert isinstance(ticket, str), 'Need user ticket in GET request'
        assert isinstance(jobid, str), 'Need jobid in GET request'
        data = json.dumps({'userid': VariablesShared.userid, 'ticket': ticket, 'jobid': jobid})
        x_real_ip = self.request.headers.get('X-Real-IP')
        remote_ip = x_real_ip or self.request.remote_ip
        logger_settings.logger.info('IP of the request is :{0}'.format(remote_ip))
        self.write(data)
        self.subscribe(VariablesShared.userid, jobid, ticket)

    # The QueueWatcher after pull from the queue creates a future
    # that is checking the API jobId till gets "done"
    def subscribe(self, userid, jobid, ticket):
        # type: (object, object, object) -> object
        logger_settings.logger.info('New subscriber created for user:{0} and jobid:{1}'.format(VariablesShared.userid, jobid))
        pool = ThreadPoolExecutor(1)
        futures = []
        futures.append(pool.submit(self.checkhpc, userid, jobid, ticket))

    def checkhpc(self, userid, jobid, ticket):
        logger_settings.logger.info('Check the HPC job status for user:{0} and job:{1}'.format(userid, jobid))
        for theuser in VariablesShared.clients:
            if theuser['userid'] == VariablesShared.userid:
                logger_settings.logger.info('Seems you are the user for which the request was received')
                while True:
                    job_status_result = self.get_job_status(ticket, jobid)
                    # TODO check errors of execution to prevent hangout
                    if 'DONE' not in job_status_result:
                        logger_settings.logger.info(
                            'We will wait another while to get the jobid:{0} status'.format(jobid))
                        time.sleep(2)
                    else:
                        result_returned = json.dumps({'jobid': jobid, 'jobstatus': job_status_result})
                        logger_settings.logger.info('Job {0} has status {1}'.format(jobid, job_status_result))
                        try:
                            # WRite to socket
                            theuser['wsobj'].write_message(result_returned)
                        except Exception:
                            logger_settings.logger.error('Hmmm, we had a problem writing on the socket')
                        break


    def get_job_info(self, url, ticket, jobid):
        # type: (object, object, object) -> object
        """
        :type url: object
        :param url:
        :param ticket:
        :param jobid:
        """
        try:
            url = url + '/' + 'job' + '/' + jobid + '/' + 'info' + '?ticket=' + ticket
            r = requests.get(url)
            r.raise_for_status()
            data = r.json()
            if str(data['success']) is 'False':
                print 'Json: {0}'.format(str(data))
                raise (UATError(ExceptionType.HPCAPI_RET_FALSE, ' unsuccessful'))
            r.raise_for_status()
            return data

        except requests.exceptions.Timeout as e:
            raise (UATError(ExceptionType.HPCAPI_TIMEOUT, ' at get_job_info [ {0} ]'.format(e)))

        except requests.exceptions.HTTPError as e:
            raise (UATError(ExceptionType.HPCAPI_FORDBIDDEN, ' at get_job_info [ {0} ]'.format(e)))

        except requests.exceptions.TooManyRedirects as e:
            raise (UATError(ExceptionType.HPCAPI_TOOMANYREDIRECTS, ' at get_job_info [ {0} ]'.format(e)))

        except requests.exceptions.RequestException as e:
            raise (UATError(ExceptionType.HPCAPI_OTHER, ' at get_job_info [ {0} ]'.format(e)))

        except Exception:
            logger_settings.logger.debug('No idea')
            raise (UATError(ExceptionType.HPCAPI, ' at get_job_info'))

    def get_job_status(self, ticket, jobid):
        try:
            get_job_status = self.get_job_info(VariablesShared.url_hpc, ticket, jobid)
            status = get_job_status['data']['status']
            return status
        except Exception:
            logger_settings.logger.info('exception on getting the status of job')
