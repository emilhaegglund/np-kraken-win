import os
import shutil
import h5py
import sys
import time
import subprocess
import re

class Fast5(object):
	def __init__(self, path, used):
		self.path = path
		self.used = False

def parse_kraken_out(out):
	result_line = re.split(r'\t', out)
	if len(result_line) > 2:
		txid = result_line[2]
		return(txid)
	else:
		print("Could not match this read")
		return(None)

used_file = []
mypath = sys.argv[1]
output = sys.argv[2]
kraken_db = sys.argv[3]


if not os.path.isdir(mypath):
	print(mypath + ' is not a directory')
	sys.exit()

if not os.path.isdir(output):
	print(outout + ' is not a directory')
	sys.exit()

if not os.path.isdir(kraken_db):
	print(kraken_db + ' is not a directory')
	sys.exit()

files = set([os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))])
species = {None:0}
number_of_reads = 0

#Read the taxonomy file and store it to dictionary
print('Loading taxonomy data...')
taxonomy_file = '/docker/minikraken_db/taxonomy/names.dmp'
num_lines = sum(1 for line in open(taxonomy_file))
with open(taxonomy_file, 'r') as taxonomy:
	taxonomy_data = [0] * num_lines
	for line in taxonomy:
		line = line.split('|')
		line = [item.strip() for item in line]
		if line[3] == 'scientific name':
			txid = int(line[0])
			taxonomy_data[txid] = line[1]
print('The taxonomy data has been loaded.')

print("Now, let's detect some species!")
while True:
	new_files = [os.path.join(mypath, f) for f in os.listdir(mypath) if os.path.isfile(os.path.join(mypath, f))]
	if len(new_files) > 0:
		for f in new_files:
			# Run kraken on new files
			dir_name, file_name = split(f)
			if splitext(file_name)[-1] == '.fast5':
				number_of_reads += 1
				print('Number of basecalled files: ' + str(number_of_reads))
				basecalled = h5py.File(f)
				print(str(basecalled['Raw/Reads'].keys()[0]))
				try:
					fastq_file = output + file_name + ".fastq"
					fastq = open(fastq_file, "w")
					fastq.write(basecalled['Analyses/Basecall_1D_001/BaseCalled_template/Fastq'][()])
				except:
				    print('No local basecalling was made on this file')

				basecalled.close()
				args = ['kraken', '--db', kraken_db, '--fastq-input', fastq_file]
				process = subprocess.Popen(args, stdout=subprocess.PIPE,
										   stderr=subprocess.PIPE)
				process.wait()
				out, err = process.communicate()
				shutil.move(f, output + file_name)
				txid = parse_kraken_out(out)
				if txid is not None:
					specie = taxonomy_data[int(txid)]
					if specie in species:
						species[specie] += 1
					else:
						species[specie] = 1
				else:
					species[None] += 1
				fastq.close()
				print(species)
	time.sleep(1)