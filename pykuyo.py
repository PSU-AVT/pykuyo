import serial

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

if __name__=='__main__':
	s = Urg_04lx()
	s.open('/dev/ttyACM0')
	s.cmd_reset()

