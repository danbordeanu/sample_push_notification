import websocket
import thread
import time
import sys


def on_message(ws, message):
    print message


def on_error(ws, error):
    print error


def on_close(ws):
    print "### closed ###"


def on_open(ws):
    def run(*args):
        while True:
            time.sleep(15)
            ws.send('Ping from client - writing to websocket')
        time.sleep(1)
        ws.close()

    thread.start_new_thread(run, ())


if __name__ == '__main__':
    port = sys.argv[1]
    user = sys.argv[2]
    assert isinstance(port, str), 'Need PORT where PUSH NOTIF is running'
    assert isinstance(user, str), 'Need user for the websocket'
    websocket.enableTrace(True)
    try:
        ws = websocket.WebSocketApp('ws://localhost:{0}/register?userid={1}'.format(port, user),
                                    on_message=on_message,
                                    on_error=on_error,
                                    on_close=on_close)
    except Exception:
        print 'issue creating the socket'

    ws.on_open = on_open
    ws.run_forever()
