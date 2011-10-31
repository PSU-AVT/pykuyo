import serial
import struct

class Urg_04lx(object):
	def open(self, path):
		s = serial.Serial(path, 19200, 8)

		self.device = s
		resp = self.cmd_version_info()

		if 'PROT:SCIP 2.0' not in resp:
			print 'Invalid protocol devined in version info. got:'
			print resp
			del s
			return

		self.device = s

	def run_cmd(self, cmd):
		self.device.write(cmd)
		self.device.write('\n')

		resp = ''
		while '\n\n' not in resp and '\r\r' not in resp:
			resp += self.device.read()

		return resp

	def cmd_version_info(self):
		return self.run_cmd('VV')

	def cmd_laser_on(self):
		print self.run_cmd('BM')

	def cmd_reset(self):
		print self.run_cmd('RS')

	def encode_chars(self, data):
		return ''.join([chr(ord(ch) + 0x30) for ch in data])

	def decode_chars(self, data):
		return ''.join([chr(ord(ch) - 0x30) for ch in data])

	def encode_val(self, val, out_size):
		ret = str(val)
		while len(ret) < out_size:
			ret = '0' + ret
		return ret

	def cmd_scan(self, start, end, cluster, scan_interval, scan_cnt):
		cmd = 'MD' + self.encode_val(start, 4) + self.encode_val(end, 4) + self.encode_val(cluster, 2) + self.encode_val(scan_interval, 1) + self.encode_val(scan_cnt, 2)
		status = self.run_cmd(cmd)
		resp = ''
		if '00P' in status:
			while '\n\n' not in resp:
				resp += self.device.read()
		else:
			print 'Invalid status during scan. got: '
			print status
		return resp

if __name__=='__main__':
	import matplotlib.pyplot as plt
	import math
	import time

	s = Urg_04lx()
	s.open('/dev/ttyACM0')
	plt.ion()
	while True:
		data = s.cmd_scan(10, 768, 2, 0, 1)
		data = data.split('\n')[3:]
		data = ''.join([x[:-1] for x in data])
		data = s.decode_chars(data)
		vals = []
		while len(data) > 0:
			vals.append(struct.unpack('<H', data[:2])[0])
			data = data[3:]

		c = (3.41*2) / 1024.0
		c *= 2

		x = []
		y = []
		for val in vals:
			i = len(x)
			theta = i * c
			y.append(math.sin(theta) * val)
			x.append(math.cos(theta) * val)
		
		plt.clf()
		plt.plot(x, y)
		plt.axis([-16000, 16000, -16000, 16000])
		plt.draw()
		time.sleep(.1)

