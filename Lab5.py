
# INFR 4690U Lab 5 
# Student Name:   TONY WANG
# Date:           02/01/2019
# Student Number: 100474399
# Description:    All questions are based on Python 3 to get the bonus mark.

import sys
import hashlib
import binascii

# question 1
# ---------------------------------------------------------------------------------------------------------
# the function to extract the first 512 bytes from the image and write them in a .mbr file
def saveMBR():
	try:
		f = open("ext-part-test-2.dd.mbr", "wb")
		fp = open("ext-part-test-2.dd", "rb")
		mbr = fp.read(512)
		f.write(mbr)
	finally:
		f.close()
		fp.close()
	return mbr

# the function to hash the extracted MBR file using SHA-256
def hashMBR():
	filename = "ext-part-test-2.dd.mbr"
	with open(filename,"rb") as f:
		bytes = f.read() # read entire file as bytes
		readable_hash = hashlib.sha256(bytes).hexdigest();
		print("The SHA-256 hash of the mbr file is: " + readable_hash)

# Question 2
# ---------------------------------------------------------------------------------------------------------
# the function to read the mbr file in hexdecimal 
def extractMBR():
	try:
		with open("ext-part-test-2.dd", "rb") as fp:
			hex_list = ["{:02x}".format(c) for c in fp.read(512)]
	finally:
		fp.close()
	return hex_list

# The funciton is to gather the infomration of each partition, calculate the start & ending CHS, 
# starting LBA, total factors and size of each partition using a Python list to optamize the program 
# performance
def parseInfo(rawData):
	
	# 1MB = 1024 * 1024 B
	CalFormula = 1048576

	#	         0   1   2   3   4   5   6   7   8	 9   10  11  12  13  14  15
	partion = [[446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461],
			   [462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477],
			   [478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493],
			   [494,495,496,497,498,499,500,501,502,503,504,505,506,507,508,509],]
	for x in range(4):
		if ((rawData[partion[x][0]] == "00" or rawData[partion[x][0]] == "80") and (rawData[partion[x][1]] != "00" or rawData[partion[x][2]] != "00" or rawData[partion[x][3]] !="00") and rawData[partion[x][4]] != "00"):
			print ("---------------------------" + str(x + 1) + "st Partition found---------------------------")
			# size and sector calculator
			# 454 to 457 are starting lsb, 458 to 461 are sectors number
			lsbStringInHex = rawData[partion[x][11]]+rawData[partion[x][10]]+rawData[partion[x][9]]+rawData[partion[x][8]]
			# 447 to 449 are the Starting CHS values
			chsStartingInHex = rawData[partion[x][3]]+rawData[partion[x][2]]+rawData[partion[x][1]]
			# 447 to 449 are the ending CHS values
			chsEndingInHex = rawData[partion[x][7]]+rawData[partion[x][6]]+rawData[partion[x][5]]
			startingSector = int(lsbStringInHex, 16)			
			print("Starting CHS:                 "+ chsStartingInHex + "   (Big Endian)")
			print("Ending CHS:                   "+ chsEndingInHex + "   (Big Endian)")
			print("Starting LBA:                 "+ lsbStringInHex + " (Big Endian)")
			noOfSectorsinHex = rawData[partion[x][15]]+rawData[partion[x][14]]+rawData[partion[x][13]]+rawData[partion[x][12]]
			noOfSectors = int(noOfSectorsinHex, 16)
			print("Total sectors:                "+ noOfSectorsinHex + " (Big Endian)")	
			totalSizeInByte = ((startingSector+noOfSectors)*512)-(startingSector*512)
			print ("Total size:                   "+ str(totalSizeInByte/CalFormula)+" MB")
		else:
			print("-----------------------No Partition found on disk-----------------------")

# Question 3
# ---------------------------------------------------------------------------------------------------------
# the function to extract the partition 1 from the image and write it in a .partition file
def savePartition1():
	try:
		f = open("ext-part-test-2.dd.partition", "wb")
		fp = open("ext-part-test-2.dd", "rb")
		fp.seek(32256)
		mbr = fp.read(26804736)
		f.write(mbr)
	finally:
		f.close()
		fp.close()
	return mbr

# the function to hash the partition 1 using SHA-256
def hashPartition1():
	filename = "ext-part-test-2.dd.partition"
	with open(filename,"rb") as f:
		bytes = f.read() # read entire file as bytes
		readable_hash = hashlib.sha256(bytes).hexdigest();
		print("The SHA-256 hash of the partition 1 is: " + readable_hash)

# Call all the functions
# ---------------------------------------------------------------------------------------------------------
# declare the mbr file is saved locally
print("The mbr file is saved as:            ext-part-test-2.dd.mbr")
# call the save & hash mbr functions
saveMBR()
hashMBR()
# call the parse function
parseInfo(extractMBR())
# declare the partition 1 data is saved locally
print("Partition 1 data is saved as:        ext-part-test-2.dd.partition1")
# call the save & hash partition1 functions
savePartition1()
hashPartition1()