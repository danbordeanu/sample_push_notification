import requests

from COMMONS.helpers import logger_settings
from COMMONS.helpers.Error import UATError, ExceptionType
from Variables import VariablesShared


def get_job_info(url, ticket, jobid):
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

