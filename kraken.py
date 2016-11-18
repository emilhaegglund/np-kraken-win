import os
import shutil
import h5py
import sys
import time
import subprocess
import re
import pandas as pd


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

def get_current_class(txid, tax):
    return tax[txid][1]

def get_class_name(txid, tax, names, class_number, class_name='species'):
    level = get_current_class(txid, tax)
    if txid == 131567:
        level = 'cellular organism'
    if class_number[level] > class_number[class_name]:
        return False
    elif class_number[level] == class_number[class_name]:
        return names[txid]

    while level != class_name:
        level = tax[txid][1]
        name = names[txid]
        txid = tax[txid][0]

    return name



""" Main Program """
used_file = []
mypath = sys.argv[1]
output = sys.argv[2]
kraken_db = sys.argv[3]
time_file = sys.argv[4]


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

class_number = {'no rank':0,
                'subspecies':1,
                'species':2,
                'genus':3,
                'family':4,
                'order':5,
                'class':6,
                'phylum':7,
                'superkingdom':8,
                'cellular organism':9}

#Read the taxonomy file and store it to dictionary
print('Loading taxonomy data...')
taxonomy_path = '/docker/minikraken_db/taxonomy/nodes.dmp'
tax = {}
with open(taxonomy_path, 'r') as taxonomy_file:
    for line in taxonomy_file:
        line = line.split("|")
        txid = int(line[0])
        parent = int(line[1].strip("\t"))
        level = line[2].strip("\t")
        tax[txid] = [parent, level]

names_path = '/docker/minikraken_db/taxonomy/names.dmp'
names = {}
with open(names_path, 'r') as name_file:
    for line in name_file:
        line = line.split("|")
        line = [item.strip() for item in line]
        if line[3] == 'scientific name':
            txid = int(line[0])
            names[txid] = line[1]
print('The taxonomy data has been loaded.')

print("Now, let's detect some species!")
times = pd.read_csv(time_file, sep='\t')
times = times.sort(["unix_timestamp"])
path = list(times['filename'])
prev_time = 0
outfile = file('/docker/outfile.txt', 'w')
while True:
	if True:
		for i, next_time in enumerate(list(times['unix_timestamp'])):
			# Run kraken on new files
			file_name = path[i]
			file_name = file_name[2:]
			move_time = next_time - prev_time
			print(move_time)
			time.sleep(move_time)
			#dir_name, file_name = os.path.split(f)
			if os.path.splitext(file_name)[-1] == '.fast5':
				number_of_reads += 1
				print('Number of basecalled files: ' + str(number_of_reads))
				basecalled = h5py.File(file_name)
				# print('\007')
				#print(str(basecalled['Raw/Reads'].keys()[0]))
				read_nr = list(basecalled['Raw/Reads'].keys())[0]
				start_time = basecalled['Raw']['Reads'][read_nr].attrs['start_time']
				sampling_rate = basecalled['UniqueGlobalKey']['channel_id'].attrs['sampling_rate']
				start_time = int(start_time/float(sampling_rate))
				try:
					fastq_seq=basecalled['Analyses/Basecall_1D_000/BaseCalled_template/Fastq'][()]
					fastq_file = file_name + ".fastq"
					fastq = open(fastq_file, "w")
					fastq.write(fastq_seq)
					print(basecalled['Analyses/Basecall_1D_000/BaseCalled_template/Fastq'][()])
					outfile.write('Read;' + str(start_time) + ';basecalled\r\n')
					outfile.flush()
					fastq_exist = True
					fastq.close()
				except:
				    print('No local basecalling was made on:' + str(f))
				    fastq_exist = False
				    txid = None
				
				basecalled.close()

				if fastq_exist == False:
					print('Read;' + str(start_time) + ';not basecalled')
					outfile.write('Read;' + str(start_time) + ';not basecalled\r\n')
					outfile.flush()

				if fastq_exist:
					args = ['kraken', '--db', kraken_db, '--fastq-input', fastq_file]
					process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
					process.wait()
					out, err = process.communicate()
						
					txid = int(parse_kraken_out(out))
				
				if txid == 0 or txid == 1:
					txid = None

				if txid is not None:
					print(txid)
					family = get_class_name(txid, tax, names, class_number, 'species')
					print(family)
					if family:
						if family in species:
							species[family] += 1
						else:
							species[family] = 1
						if family != 0:
							outfile.write(str(family) + ';' + str(species[family]) + ';' + str(start_time) + '\r\n')
							outfile.flush()
						else:
							print('Not classified')
							outfile.write('Not classified;' + str(species[family]) + ';' + str(start_time) + '\r\n')
							outfile.flush()
				# else:
				# 	species[None] += 1
				# 	outfile.write('Not basecalled:' + str(species[None]) + '\r\n')
				# 	outfile.flush()
				#shutil.move(file_name, output + file_name)
				prev_time = next_time
				
	time.sleep(1)