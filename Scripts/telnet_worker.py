import telnetlib

from PyQt5.QtCore import pyqtSignal, QThread

TIMEOUT = 2

class TelnetWorker(QThread):
    message_received = pyqtSignal(str)
    connection_closed = pyqtSignal()

    def __init__(self, host: str, port: int, lock):
        super().__init__()
        try:
            self.telnet_connection = telnetlib.Telnet(host, int(port), TIMEOUT)
            self.running = True
            self.lock = lock
            self.response = None
        except Exception as e:
            self.message_received.emit(f"Error: {str(EOFError)}")

    def run(self):
        while self.running:
            try:
                self.lock.lock()
                try:
                    self.response = self.telnet_connection.read_until(b"\r", timeout=TIMEOUT).decode('ascii').rstrip()
                    if not self.response.endswith("\r"):
                        self.response += self.telnet_connection.read_very_eager().decode('ascii').rstrip()
                except EOFError:
                    self.message_received.emit(f"Error: {str(EOFError)}")
                finally:
                    self.lock.unlock()

                if self.response.startswith("INFO"):
                    self.message_received.emit(self.response)
            except EOFError:
                self.message_received.emit(f"Error: {str(EOFError)}")
                self.connection_closed.emit()
                break

    def stop(self):
        self.running = False
        self.quit()
        self.wait()