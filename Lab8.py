# INFR 4690U Lab 8 
# Student Name:   TONY WANG
# Date:           02/27/2019
# Student Number: 100474399
# Description:    All questions are based on Python 3 to get the bonus mark.	

import sys
import hashlib
import binascii
# Using a partition types table as a reference from https://github.com/shubham0d/MBR-extractor
import partitionID

# inherit and optimized functions from lab 5
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------

currentFileName = "thumbimage_ntfs.dd"

flag_ptt = "partition"
flag_FAT = "FileAllocationTable"
flag_FAT_FD ="fileDirectory"

# the function to read the file
def extractMBR(path=""):
	try:
		with open(path, "rb") as fp:
			hex_list = ["{:02x}".format(c) for c in fp.read(512)]
	finally:
		fp.close()
	return hex_list

# the function to extract data of one partition from the source file and write it in a new file
def saveData(FATS,FATE,flag="",noOfPartition=""):
	try:
		f = open(currentFileName + "." + flag + noOfPartition, "wb")
		if (flag == flag_ptt):
			fp = open(currentFileName, "rb")
			print("Partition " + noOfPartition + " data is saved as: " + currentFileName + "." + flag + noOfPartition)
		elif (flag == flag_FAT_FD):
			fp = open(currentFileName + "." + flag_ptt + noOfPartition, "rb")
			print("File directory data of FAT partiton " + noOfPartition + " is saved as: " + currentFileName + "." + flag + noOfPartition)
		elif (flag == flag_FAT):
			fp = open(currentFileName + "." + flag_ptt + noOfPartition, "rb")
			print("File allocation table data of " + noOfPartition + " is saved as: " + currentFileName + "." + flag + noOfPartition)		
		fp.seek(FATS)
		mbr = fp.read(FATE)
		f.write(mbr)
	finally:
		f.close()
		fp.close()
	return mbr

# the function to hash the partition 1 using SHA-256
def hashPartition(noOfPartition=""):
	filename = currentFileName + "." + flag_ptt + noOfPartition
	with open(filename,"rb") as f:
		bytes = f.read() # read entire file as bytes
		readable_hash = hashlib.sha256(bytes).hexdigest();
		print("The SHA-256 hash of the partition " + noOfPartition + " is: " + readable_hash)
		print ("")

# The function to extract mbr from the source file
def parseInfo(rawData):	
	# 1MB = 1024 * 1024 B
	CalFormula = 1048576
	maxPartition = 4	
	#	         0   1   2   3   4   5   6   7   8	 9   10  11  12  13  14  15
	partion = [[446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461],
			   [462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477],
			   [478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493],
			   [494,495,496,497,498,499,500,501,502,503,504,505,506,507,508,509],]
	for x in range(maxPartition):
		if ((rawData[partion[x][0]] == "00" or rawData[partion[x][0]] == "80") and (rawData[partion[x][1]] != "00" 
			or rawData[partion[x][2]] != "00" or rawData[partion[x][3]] !="00") and rawData[partion[x][4]] != "00"):
			print ("---------------------------" + str(x + 1) + "st Partition found---------------------------")
			# The reference from https://github.com/shubham0d/MBR-extractor
			partitionTypes = partitionID.partitionIdList(rawData[partion[x][4]])
			partitionStartSector = int(rawData[partion[x][11]] + rawData[partion[x][10]] + rawData[partion[x][9]] + rawData[partion[x][8]], 16)
			partitionEndSector = int(rawData[partion[x][15]] + rawData[partion[x][14]] + rawData[partion[x][13]] + rawData[partion[x][12]], 16)
			# call the function to save the current partition data to a new file
			saveData((partitionStartSector*512),(partitionEndSector*512),flag_ptt,str(x+1))
			# call the function to hash the current partition
			hashPartition(str(x+1))			
			print ("Partition type:       "+ partitionTypes)
			noOfSectors = int(rawData[partion[x][15]] + rawData[partion[x][14]] + rawData[partion[x][13]] + rawData[partion[x][12]], 16)
			totalSizeInByte = ((partitionStartSector+noOfSectors) * 512)-(partitionStartSector * 512)
			print ("Total partition size: "+ str(totalSizeInByte/CalFormula) + " MB")
			# call the function if the current partition type is FAT32
			if (rawData[partion[x][4]] == "0b"):
				FAT32Ana(extractMBR(currentFileName + "." + flag_ptt + str(x+1)),str(x+1))
			print ("")
		else:
			print("-----------------------No Partition found on disk-----------------------")

# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------
# ---------------------------------------------------------------------------------------------------------

# New function to extract partition boot sector from the FAT32 partition
def FAT32Ana(rawData,no): 
	global sectorSize
	global clusterSector
	global clusterSize
	global fileDirectoryStartSector
	global firstClusterOfRootDirectory
	sectorSize = int(rawData[12] + rawData[11], 16)	
	reservedArea = int(rawData[15] + rawData[14], 16)
	clusterSector = int(rawData[13], 16)
	clusterSize = clusterSector * sectorSize
	noOfFAT = int(rawData[16], 16)
	FATSize = int(rawData[39] + rawData[38] + rawData[37] + rawData[36], 16)
	firstClusterOfRootDirectory = int(rawData[47] + rawData[46] + rawData[45] + rawData[44], 16)
	minNoCluster = pow(2,1) 
	print ("Each sector size:              " + str(sectorSize))
	print ("Cluster per sector:            " + str(clusterSector))
	print ("Reserved area:                 " + str(reservedArea))
	print ("Total file allocation number:  " + str(noOfFAT))
	for x in range(noOfFAT):
		print ("FAT " + str(x) + " Start sector: " + str(reservedArea + (x * FATSize)) + " End sector: " + str(reservedArea + ((x+1) * FATSize)-1))
	print ("Cluster size in bytes of the FAT file system is:     " + str(clusterSize))
	print ("The smallest cluster number of a FAT file system is: " + str(minNoCluster))
	if (noOfFAT == 2):
		fileDirectoryStartSector = (reservedArea + (FATSize * 2))
		fileDirectoryStartSectorinBytes = (reservedArea + (FATSize * 2)) * 512
	else:
		print("Number of FAT is incorrect.")
	# save the file directory data as a new file
	saveData(fileDirectoryStartSectorinBytes,512,flag_FAT_FD,no)
	# save the file allocation table data as a new file
	saveData((reservedArea*512),(FATSize*512),flag_FAT,no)
	extractDirectory(extractMBR(currentFileName + "." + flag_FAT_FD + no),flag_FAT_FD)	
	extractDirectory(extractMBR(currentFileName + "." + flag_FAT + no),flag_FAT)	

# New function to extract data from the directory
def extractDirectory(rawData,flag):
	global fileSize
	global startingCluster
	if (flag == flag_FAT_FD):
		fileName = bytes.fromhex(rawData[0] + rawData[1] + rawData[2] + rawData[3] + rawData[4] + rawData[5] + rawData[6] + rawData[7]).decode('utf-8')
		fileExtension = bytes.fromhex(rawData[8] + rawData[9] + rawData[10]).decode('utf-8')
		fileSize = int(rawData[31] + rawData[30] + rawData[29] + rawData[28], 16)
		startingCluster = int(rawData[21] + rawData[20] + rawData[27] + rawData[26], 16)
		print ("File Name:                                   " + fileName + "." + fileExtension)
		print ("File Size (bytes):                           " + str(fileSize))
		print ("Starting Cluster Number (decimal):           " + str(startingCluster))
	if (flag == flag_FAT):
		# calculate the nunmber of allocated clusters 
		noOfClusters = 0
		Smybol = "0fffffff"
		if (rawData[11] + rawData[10] + rawData[9] + rawData[8] == Smybol):
			x = 11
			while ((rawData[x+4] + rawData[x+3] + rawData[x+2] + rawData[x+1]) != Smybol):
				noOfClusters += 1
				x += 4
		noOfClusters += 1
		# calculation end
		# calculate the sectors of the root directory 
		noOfRootDirectorySector = int(((startingCluster - firstClusterOfRootDirectory) * clusterSize) / sectorSize)
		fileDirectoryStartingSector = fileDirectoryStartSector + noOfRootDirectorySector
		# calculation end
		print ("Starting Sector Address (decimal):           " + str(fileDirectoryStartingSector))
		print ("Number of Clusters allocated to readme file: " + str(noOfClusters))
		print ("Number of Sectors allocated to readme file:  " + str((noOfClusters * clusterSector)))
		print ("Size of Slack Space (bytes):                 " + str((noOfClusters * clusterSize) - fileSize))

parseInfo(extractMBR(currentFileName))

