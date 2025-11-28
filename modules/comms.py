import serial
import serial.tools.list_ports
import threading
import time

class CommunicationManager:
    def __init__(self, log_callback=None):
        self.serial_port = None
        self.is_connected = False
        self.ultrasonic_distance = 0.0
        self.lock = threading.Lock()
        self.log_callback = log_callback

    def get_available_ports(self):
        return [port.device for port in serial.tools.list_ports.comports()]


    def disconnect(self):
        self.is_connected = False
        if self.serial_port:
            try:
                self.serial_port.close()
            except:
                pass
            self.serial_port = None

    def send_command(self, cmd):
        if self.is_connected and self.serial_port:
            try:
                self.serial_port.write(cmd.encode())
                if self.log_callback: self.log_callback(f"TX: {cmd.strip()}")
                return True
            except Exception as e:
                if self.log_callback: self.log_callback(f"TX Error: {e}")
                return False
        return False

    def connect(self, port, baudrate=9600):
        if self.is_connected:
            self.disconnect()
        
        try:
            self.serial_port = serial.Serial(port, baudrate, timeout=1)
            self.is_connected = True
            threading.Thread(target=self._read_serial, daemon=True).start()
            return True, f"Connected to {port}"
        except serial.SerialException as e:
            if "Access is denied" in str(e):
                return False, "Port Busy! Close Arduino IDE?"
            return False, f"Serial Error: {e}"
        except Exception as e:
            return False, f"Error: {e}"


    def _read_serial(self):
        while self.is_connected and self.serial_port:
            try:
                if self.serial_port.in_waiting > 0:
                    line = self.serial_port.readline().decode('utf-8').strip()
                    if line:
                        if self.log_callback: self.log_callback(f"RX: {line}")

                    with self.lock:
                        if "DIST" in line:
                            parts = line.split(':')
                            if len(parts) > 1:
                                self.ultrasonic_distance = float(parts[1].strip())
                        elif line.replace('.', '', 1).isdigit():
                            self.ultrasonic_distance = float(line)
            except Exception as e:
                if self.log_callback: self.log_callback(f"RX Error: {e}")
            time.sleep(0.05)

    def get_distance(self):
        with self.lock:
            return self.ultrasonic_distance
