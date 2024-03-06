import requests
import random
import time


class Transaction(object):
    def __init__(self):
        pass

    def run(self):
	r = requests.get('http://localhost:8887/push?userid=dan&ticket=ST-2157-j6WQCu4OtqiX95vOlEqZ-bla-dev.bla.com&jobid=777')
	r.raw_read()
    
if __name__ == '__main__':
    trans = Transaction()
    trans.run()
    print trans.custom_timers
