import threading
import time

class threadSend(threading.Thread):
    def __init__(self,ws, sock):
        threading.Thread.__init__(self)
        self.ws = ws
        self.sock = sock

    def run(self):
        while True:
            try:
                dockerStreamStdout = self.sock.recv(2048)
                print(dockerStreamStdout.decode('utf-8'))
                if dockerStreamStdout is not None:
                    self.ws.send_text(dockerStreamStdout.decode('utf-8'))
                else:
                    print("docker daemon socket is close")
                    self.ws.close()
            except Exception as e:
                print("docker daemon socket err: %s" % e)
                self.ws.close()
                break