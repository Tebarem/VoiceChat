import socket 
import time
import threading
import sys

import argparse

import msgpack
import msgpack_numpy as m

import sounddevice as sd
import numpy  # Make sure NumPy is loaded before it is used in the callback
import wave

from cryptography.fernet import Fernet


class client(threading.Thread):
	version = "0.1"
 
	def __init__(self):
		threading.Thread.__init__(self)
		#encryption stuff not used yet
		self.publickey = b'4vF083_jOpvEdqbXqem8GP96wmawb0KKZLz3o43o-KU='
		self.pucryp = Fernet(self.publickey)
		#This is for menus and all that good stuff.
		self.login = False
		self.outdated = False
		self.faillogin = False

		#UDP socket
		self.udpsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		#self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.isConnected = False

  
		#sounddevice stuff but i dont use this i think
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
		

		#public ip here to send data to (replace 0.0.0.0 with the ip of the server)
		#self.server_ip = "0.0.0.0"
		#self.server_port = 5555

		#host locally for now
		self.server_ip = "127.0.0.1"
		self.server_port = 5555
  
		self.make_connection()

	def make_connection(self):
		''' Sending connection request to the server node '''

		#init the out stream and start it
		self.output_stream =sd.OutputStream(device=sd.default.device[1],
							samplerate=44100, blocksize=8192,
							dtype="int16", latency=0,
							channels=1)
		self.output_stream.start()
		server = (self.server_ip, self.server_port)
		while not self.isConnected:
			try:
				#self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
				#self.client_socket.connect(server)
				#print('Connection succesful made to the server')
				
				#Was using this for TCP but i think this is unneccessary in UDP
				Receiving_cio = threading.Thread(target=self.receive_sms)
				Receiving_cio.daemon = True
				Receiving_cio.start()
				self.isConnected = True
				break
			except Exception as ex:
				#[WinError 10054] wifi problem
				#[WinError 10061] server offline
				self.login = False
				print(ex)
				print("Trying to reconnect in 5 seconds...")
				time.sleep(5)

	def receive_sms(self):
		#unpacker = msgpack.Unpacker()
		#Initial pack so that we are able to start recieving data from the server
		self.udpsocket.sendto("connection".encode(), (self.server_ip,self.server_port))
		data,a = self.udpsocket.recvfrom(4096)
		if data.decode() != "connection":
			pass
		while True:
			#try:
			data, a = self.udpsocket.recvfrom(4096)
			#data = self.pucryp.decrypt(data).decode().split(" ")
			if not data:
				print("No data")
			else:
				try:
				#unpacker.feed(data)
					data = msgpack.unpackb(data, object_hook=m.decode)
					#print(numpy.prod(data.shape))
					#for d in unpacker:
					#	d = msgpack.unpackb(d, object_hook=m.decode)
					self.output_stream.write(data)
				except Exception as e:
					print(e)
	
			#except Exception as ex:
			#	print(ex)
			#	self.login = False
			#	print("Reconnecting to server. . .")
			#	break
	
	def int_or_str(self, text):
		"""Helper function for argument parsing."""
		try:
			return int(text)
		except ValueError:
			return text
	
	def sendcmd(self, command):
		#Send the audio in encoded numpy package
		message = command
		#print(sys.getsizeof(message))
		message = msgpack.packb(message, default=m.encode)
		#self.client_socket.send(message)
		self.udpsocket.sendto(message, (self.server_ip,self.server_port))