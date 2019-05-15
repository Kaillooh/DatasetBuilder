#! /usr/bin/python3
# -*- coding: utf-8 -*-
__author__    = "Pierre Etheve"
__email__  = "pierre.etheve.lfdv@gmail.com"

import urllib.request as rq
import sys
import os
import subprocess
import dataset_shuffler
import argparse

parser = argparse.ArgumentParser(description="Custom dataset builder for Pix2Pix")
parser.add_argument('-source', type=str, required=True, help='folder where raw files are located')
parser.add_argument('-destination', type=str, required=True, help='output folder where generated image dataset is saved')
parser.add_argument('-resize', type=int, default=400, help='size of the generated images')
parser.add_argument('-mode', type=str, default="alphabetic", choices=["alphabetic", "self_pairing", "bifolder", "manual"], help='mode of pairing (default : alphabetic)')
opt = parser.parse_args()
print(opt)


source = opt.source
destination = opt.destination
mode = opt.mode
resize = opt.resize

def formatPath(path) :
	if path[-1] != '/' :
		path = path+'/'
	return path

def getDirs(path) :
	dirs = []
	for name in os.listdir(path) :
		if os.path.isdir(path+name) :
			dirs.append(name)
	return dirs

def generateFile(entry) :

	cmd1 = "convert -resize %dx%d %s out1.png"%(resize, resize, entry['A'])
	cmd2 = "convert -resize %dx%d %s out2.png"%(resize, resize, entry['B'])
	cmd3 = "convert +append out1.png out2.png %s"%(entry['out'])

	print(cmd1)
	print(cmd2)
	print(cmd3)

	p1 = subprocess.Popen(cmd1.split(), stdout=subprocess.PIPE)
	p1.wait()
	p2 = subprocess.Popen(cmd2.split(), stdout=subprocess.PIPE)
	p2.wait()
	p3 = subprocess.Popen(cmd3.split(), stdout=subprocess.PIPE)
	p3.wait

def processIndex(index) :
	for entry in index :
		generateFile(entry)


def buildIndexAlphamode() :
	global source, destination
	index = []
	folder_list = getDirs(source)
	

	for folder in folder_list :
		i=0
		path = source+folder+"/"

		files = os.listdir(path)
		original = ""
		puppets = []
		for f in files :
			if original == "" and f[0] == '0' :
				original = f
			else :
				puppets.append(f)

		for puppet in puppets : 
			entry = {}
			entry['A'] = path+original
			entry['B'] = path+puppet
			entry['out'] = "%s%s%03d.jpg"%(destination, folder, i)
			index.append(entry)
			i+=1

	return index

def buildIndexBifolder() :
	global source, destination
	index = []

	files = os.listdir(source+"A")
	files.sort()

	for f in files :
		entry = {}
		entry['A'] = "%sA/%s"%(source, f)
		entry['B'] = "%sB/%s"%(source, f)
		entry['out'] = "%s%s"%(destination, f)
		index.append(entry)

	return index

def buildIndexSelfPairing() :
	global source, destination
	index = []

	files = os.listdir(source)
	files.sort()

	i=0

	for f in files :
		entry = {}
		entry['A'] = "%s%s"%(source, f)
		entry['B'] = "%s%s"%(source, f)
		entry['out'] = "%s%03d.png"%(destination, i)
		i+=1
		index.append(entry)

	return index

def buildIndexManual() :
	global source, destination
	index = []

	files = os.listdir(source)
	files.sort()

	if "index.txt" not in files :
		print("'index.txt' was not found, try to add one or to select another mode")
		sys.exit()

	with open(source+'index.txt', 'r') as infile :
		for line in infile :
			line = line.replace('"', '')
			line = line.replace(' ', '')
			line = line.replace("\n", '')
			parts = line.split(',')
			print("A : '%s'   B : '%s'"%(parts[0], parts[1]))

			entry = {}
			entry["A"] = source+parts[0]
			entry["B"] = source+parts[1]
			entry['out'] = destination+parts[0]
			index.append(entry)

	return index


index = []
if opt.mode == "alphabetic" :
	index = buildIndexAlphamode()
elif opt.mode == "self_pairing" :
	index = buildIndexSelfPairing()
elif opt.mode == "bifolder" :
	index = buildIndexBifolder()
elif opt.mode == "manual" :
	index = buildIndexManual()
print(index)
processIndex(index)