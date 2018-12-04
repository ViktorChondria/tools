#!/usr/bin/env python3.6

"""
filetype signature: 76 69 6b 74 6f 72
format: signature (6 bytes), number of elements (4 bytes), [md5 hash of filename (16 bytes), offset from end of header (4 bytes)] 
"""

import glob, os, sys, struct, argparse, hashlib

def generate_archive(archive_name, files):
	signature = [0x76, 0x69, 0x6b, 0x74, 0x6f, 0x72]
	nulls = [00, 00, 00, 00, 00, 00, 00, 00, 00, 00]

	header = signature
	# number of files (and ToC chunks)
	header.extend(((32 - len(files).bit_length()) // 8) * [00] + [len(files)])

	current_offset = 10

	# generate header
	for file in files:
		m = hashlib.md5()
		m.update(os.path.basename(file.name).encode('utf-8'))
		h = m.digest()

		# filename hash
		header.extend(h)
		
		# file offset
		header.extend(((32 - current_offset.bit_length()) // 8) * [00] + [current_offset])
		current_offset += file.tell() + 10

	archive = open(archive_name, 'wb')
	# write header
	archive.write(bytearray(header))

	for file in files:
		# padding
		archive.write(bytearray(nulls))

		# file content
		chunk = file.read(1024)
		while(chunk):
			archive.write(chunk)
			chunk = file.read(1024)

		print(f'Archived file {file.name} checksum {m.hexdigest()} size {file.tell()}')

	return archive

def main():
	parser = argparse.ArgumentParser(description='vn archive generator')
	parser.add_argument('input_dir', action='store')
	parser.add_argument('-o', action='store', dest='out', default=None)

	args = parser.parse_args()
	if args.out == None:
		args.out = args.input_dir
	args.out += '.arc'
	print(f'Archiving {args.input_dir} into {args.out}')

	files = []
	os.chdir(args.input_dir)
	for file in glob.glob('*'):
		files.append(open(file, mode='rb'))

	os.chdir('../')
	generate_archive(args.out, files)

	print('Done!')

if __name__=='__main__':
	main()
