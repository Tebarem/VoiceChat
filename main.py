from client import client

import argparse

import sounddevice as sd
import numpy  # Make sure NumPy is loaded before it is used in the callback
import threading

class App:
    def __init__(self):
        self.client = client()
        self.client.daemon = True
        self.client.start()

        self.parser = argparse.ArgumentParser(add_help=False)
        self.parser.add_argument(
            '-l', '--list-devices', action='store_true',
            help='show list of audio devices and exit')
        self.args, self.remaining = self.parser.parse_known_args()
        if self.args.list_devices:
            print(sd.query_devices())
            self.parser.exit(0)
        self.parser = argparse.ArgumentParser(
            description=__doc__,
            formatter_class=argparse.RawDescriptionHelpFormatter,
            parents=[self.parser])
        self.parser.add_argument(
            '-i', '--input-device', type=self.int_or_str,
            help='input device (numeric ID or substring)')
        self.parser.add_argument(
            '-o', '--output-device', type=self.int_or_str,
            help='output device (numeric ID or substring)')
        self.parser.add_argument(
            '-c', '--channels', type=int, default=2,
            help='number of channels')
        self.parser.add_argument('--dtype', help='audio data type')
        self.parser.add_argument('--samplerate', type=float, help='sampling rate')
        self.parser.add_argument('--blocksize', type=int, help='block size')
        self.parser.add_argument('--latency', type=float, help='latency in seconds')
        self.args = self.parser.parse_args(self.remaining)
    
        self.run()
    
    def run(self):
        self.listTH = threading.Thread(target=self.listener)
        self.listTH.daemon = True
        self.listTH.start()
        input_stream =sd.InputStream(device=sd.default.device[0],
                            samplerate=44100, blocksize=512,
                            dtype="int16", latency=0,
                            channels=1)
        
        print(self.args.channels)
        print(self.args.input_device)
        input_stream.start()
        while True:
            try:
            
                frames = input_stream.read(1024)[0]
                #print(frames)
                self.client.sendcmd(frames)
            except KeyboardInterrupt:
                self.parser.exit('')
            except Exception as e:
                self.parser.exit(type(e).__name__ + ': ' + str(e))
            #self.client.sendcmd(f"{self.stream_in.read(1024)}")
    
    def callback(self, indata, outdata, frames, time, status):
        if status:
            print(status)
        outdata[:] = indata
     
    def listener(self):
        pass
    
    def int_or_str(self, text):
        """Helper function for argument parsing."""
        try:
            return int(text)
        except ValueError:
            return text

    
app = App()