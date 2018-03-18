import os
import sys
from hashlib import md5
from subprocess import *
import json

try:
	from pysqlcipher3 import dbapi2 as sqlite3
except ModuleNotFoundError:
	print("pysqlcipher3 Not Installed!")
	exit(1)


class util:
	bin = "/data/data/com.termux/files/home/"
	encoding = sys.getdefaultencoding()

	def md5sum(text):
			return md5(text.encode(util.encoding))


class param:

	def imei():
		print("Retrieving Device ID...")

		imei = Popen(["termux-telephony-deviceinfo"], stdout=PIPE)
		imei = json.loads(imei.communicate()[0])
		imei = imei["device_id"]

		print("Done! Device ID is " + imei)
		return imei

	def uin():
		print("Retrieving UIN...")

		try:
			uin = open("/sdcard/tencent/uin", "r").read()[:-1]
		except OSError:
			print("UIN Not Found!")
			exit(1)

		if util.md5sum("mm" + str(uin)).hexdigest() != util.dir:
			print("Wrong UIN!")
			exit(1)

		print("Done! UIN is " + uin)
		return uin


class decrypt:
		bak = "/dbback/EnMicroMsg.db.bak"
		prefix = "/sdcard/tencent/MicroMsg/"
		sm = "/dbback/EnMicroMsg.db.sm"

		def repair():
			arglist = [util.bin + "dbrepair"]
			arglist.extend(["--in-key", util.ff])
			arglist.extend(["--output", decrypt.output])
			arglist.extend(["--page-size", "1024"])
			arglist.extend(["--load-master", decrypt.prefix + util.dir + decrypt.sm])
			arglist.extend(["--version", "1"])
			arglist.extend(["--master-key", util.ff])
			arglist.extend([decrypt.prefix + util.dir + decrypt.bak])

			print("Repairing DB...")

			s = Popen(arglist, stdout = PIPE, stderr = PIPE)
			stdout, stderr = s.communicate()
			print(stdout.decode(util.encoding))
			print(stderr.decode(util.encoding))

		def backup():
			arglist = [util.bin + "dbbackup"]
			arglist.extend(["recover"])
			arglist.extend(["--verbose"])
			arglist.extend(["--key", util.ff])
			arglist.extend(["--output", decrypt.prefix + util.dir + decrypt.bak])
			arglist.extend(["--page-size", "1024"])
			arglist.extend([decrypt.output])

			print("Generating DB...")

			b = Popen(arglist, stdout = PIPE, stderr = PIPE)
			stdout, stderr = b.communicate()
			print(stdout.decode(util.encoding))
			print(stderr.decode(util.encoding))


def main(argv):
	if len(argv) == 1:
		decrypt.output = "MicroMsg.db"
	else:
		decrypt.output = argv[1]

	if os.path.isfile(decrypt.output):
		print("Delete old one? (Y/N)")
		ans = input()
		if ans == 'Y':
			os.remove(decrypt.output)
		else:
			print("Done!")
			exit(0)

	for dir in os.listdir(decrypt.prefix[:-1]):
		if len(dir) == 32:
			util.dir = dir
			break

	imei = param.imei()
	uin = param.uin()

	util.hex = util.md5sum(imei + uin).hexdigest()[:7]
	util.ff = util.md5sum(imei + uin).digest()

	try:
		decrypt.repair()
	except Error as e:
		print(e)
		print("Repair of DB Failed!")
		exit(-1)

	try:
		decrypt.backup()
	except Error as e:
		print(e)
		print("Decryption of DB Failed!")
		exit(-1)

	print("HEX: ")
	print(util.hex)

	print("CHAR: ")
	print(util.ff)


if __name__ == "__main__":
	main(sys.argv)
