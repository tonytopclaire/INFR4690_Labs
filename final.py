print( "                                                    __----~~~~~~~~~~~------___")
print( "                                   .  .   ~~//====......          __--~ ~~    ")
print( "                   -.            \_|//     |||\\  ~~~~~~::::... /~            ")
print( "                ___-==_       _-~o~  \/    |||  \\            _/~~-           ")
print( "        __---~~~.==~||\=_    -_--~/_-~|-   |\\   \\        _/~                ")
print( "    _-~~     .=~    |  \\-_    '-~7  /-   /  ||    \      /                   ")
print( "  .~       .~       |   \\ -_    /  /-   /   ||      \   /                    ")
print( " /  ____  /         |     \\ ~-_/  /|- _/   .||       \ /                     ")
print( " |~~    ~~|--~~~~--_ \     ~==-/   | \~--===~~        .\                      ")
print( "          '         ~-|      /|    |-~\~~       __--~~                        ")
print( "                      |-~~-_/ |    |   ~\_   _-~            /\                ")
print( "                           /  \     \__   \/~                \__              ")
print( "                       _--~ _/ | .-~~____--~-/                  ~~==.         ")
print( "                      ((->/~   '.|||' -_|    ~~-/ ,              . _||        ")
print( "                                 -_     ~\      ~~---l__i__i__i--~~_/         ")
print( "                                 _-~-__   ~)  \--______________--~~           ")
print( "                               //.-~~~-~_--~- |-------~~~~~~~~                ")
print( "                                      //.-~~~--\                              ")
print( "-------------------INFR 4690U FINAL PROJECT --TONY WANG --100474399-----------")

# 03/06/2020:	  Anti-forensic tool ----- File(s) in a usb drive or sd card. 
# 03/06/2020:	  detect the drive and provide several options. (1) deep format drive (2) delete a file (3) apply self-destrcution file 
# 03/06/2020:	  Stage 1: fat system. Stage 2: NTFS system. Stage 3: other systems
# 03/06/2020:	  Goals: The target file(s) cannot be recovered by any method.
# 03/06/2020:	   Write 00 to offsets related to the search file or hard drive.
# 03/06/2020:	  Remove any evidence related to the search file had exsit before.
# 03/07/2020:	  MBR ONLY, so maximum partitions = 4.
import sys
import os
import hashlib
import binascii
import partitionID
from ctypes import *
from sys import platform

flag_win = "win32"
flag_linux = "linux"
flag_fbsd = "freebsd"
DriveCounter = 0
noOfDriveSize = 13
possible_drives = [
	r"\\.\PhysicalDrive0", # Windows
	r"\\.\PhysicalDrive1", 
	r"\\.\PhysicalDrive2",
	r"\\.\PhysicalDrive3",
	"/dev/mmcblk0", # Linux - MMC
	"/dev/mmcblk1",
	"/dev/mmcblk2",
	"/dev/sda", # Linux - Disk
	"/dev/sdb",
	"/dev/sdc",
	"/dev/disk1", #MacOSX
	"/dev/disk2",
	"/dev/disk3",
]

# The function to read and get the total number of physical drives of the pc 
def extractMBR(diskpath = "",no = 0, flag = ""):
	if (diskpath != ""):
		try:
			with open(diskpath, 'rb') as fp:
				hex_list = ["{:02x}".format(c) for c in fp.read(512)]
			fp.close();
			return hex_list
		except:
			print ("Input file/device not found")
			print ("Request terminated")
	else:
		for drive in possible_drives:
			try:
				with open(possible_drives[no], 'rb') as fp:
					hex_list = ["{:02x}".format(c) for c in fp.read(512)]
				if (flag == "load"):
					global DriveCounter
					DriveCounter = DriveCounter + 1
					print ("")
					print ("-------------------" + possible_drives[no] +" with the following partition(s) is found")
				fp.close();
				return hex_list
			except:
				pass

# The function to load the page
def platform():
	maxPhysicalDrives = DriveCounter

	if sys.platform.startswith(flag_fbsd):
		os = "freeBSD"
	elif sys.platform.startswith(flag_linux):
		os = "Linux"
	elif sys.platform.startswith(flag_win):
		os = "Windows"

	print ("")
	print ("-------------------Your current operating system is -------- " + os)

	for x in range(noOfDriveSize):
		try:
			extractMBR("",x,"load")
			parseInfo(extractMBR("",x,""),x)	
		except:
			pass

# the function to extract the partition info from the target pysical hard drive
def saveData(FATS,FATE,no):
	try:
		with open(possible_drives[no], 'rb') as fp:
			fp.seek(FATS)
			hex_list = ["{:02x}".format(c) for c in fp.read(FATE)]
		fp.close()
		return hex_list
	except:
		pass

# The function to extract mbr info from the hard drive
def parseInfo(rawData,noOfPartition):	
	# 1MB = 1024 * 1024 B
	CalFormula = 1048576
	# MBR
	maxPartitionMBR = 4
	#	         0   1   2   3   4   5   6   7   8	 9   10  11  12  13  14  15
	partion = [[446,447,448,449,450,451,452,453,454,455,456,457,458,459,460,461],
			   [462,463,464,465,466,467,468,469,470,471,472,473,474,475,476,477],
			   [478,479,480,481,482,483,484,485,486,487,488,489,490,491,492,493],
			   [494,495,496,497,498,499,500,501,502,503,504,505,506,507,508,509],]
	for x in range(maxPartitionMBR):
		try:
			if ((rawData[partion[x][0]] == "00" or rawData[partion[x][0]] == "80") and (rawData[partion[x][1]] != "00" 
				or rawData[partion[x][2]] != "00" or rawData[partion[x][3]] !="00") and rawData[partion[x][4]] != "00"):
				print ("")
				print ("---------------------------  " + str(x + 1) + "st Partition found   ---------------------------")
				# The reference from https://github.com/shubham0d/MBR-extractor
				partitionTypes = partitionID.partitionIdList(rawData[partion[x][4]])
				partitionStartSector = int(rawData[partion[x][11]] + rawData[partion[x][10]] + rawData[partion[x][9]] + rawData[partion[x][8]], 16)
				partitionEndSector = int(rawData[partion[x][15]] + rawData[partion[x][14]] + rawData[partion[x][13]] + rawData[partion[x][12]], 16)
				print ("Partition type:       "+ partitionTypes)
				print ("")
				noOfSectors = int(rawData[partion[x][15]] + rawData[partion[x][14]] + rawData[partion[x][13]] + rawData[partion[x][12]], 16)
				totalSizeInByte = ((partitionStartSector+noOfSectors) * 512)-(partitionStartSector * 512)
				print ("Total partition size:					     "+ str(totalSizeInByte/CalFormula) + " MB")
				## call the function if the current partition type is FAT32
				if (rawData[partion[x][4]] == "0b" or rawData[partion[x][4]] == "0c"):
					FAT32Ana(saveData((partitionStartSector*512),512,noOfPartition),x+1)
				if (rawData[partion[x][4]] == "07"):
					NTFSAna(saveData((partitionStartSector*512),512,noOfPartition),x+1)
		except:
			pass

# FAT function to extract partition boot sector from the FAT32 partition
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
	print ("Each sector size:                                            " + str(sectorSize))
	print ("Cluster per sector:                                          " + str(clusterSector))
	print ("Reserved area:                                               " + str(reservedArea))
	print ("Total file allocation number:                                " + str(noOfFAT))
	for x in range(noOfFAT):
		print ("FAT " + str(x) + " Start sector: " + str(reservedArea + (x * FATSize)) + " End sector: " + str(reservedArea + ((x+1) * FATSize)-1))
	print ("Cluster size in bytes of the current FAT partition is:       " + str(clusterSize))
	print ("The smallest cluster number of the current FAT partition is: " + str(minNoCluster))
	if (noOfFAT == 2):
		fileDirectoryStartSector = (reservedArea + (FATSize * 2))
		fileDirectoryStartSectorinBytes = (reservedArea + (FATSize * 2)) * 512
	else:
		print ("Number of FAT is incorrect.")

def NTFSAna(rawData,no): 
	global NTFS_MFT_LocationInt
	sectorSize = int(rawData[12] + rawData[11], 16)	
	clusterSector = int(rawData[13], 16)
	clusterSize = clusterSector * sectorSize
	MFT_Entry = 35
	MFTSize = 1024 # NTFS default 
	volumeSerialNo_1 = str.upper(rawData[75] + rawData[74])
	volumeSerialNo_2 = str.upper(rawData[73] + rawData[72])
	NTFS_MFT_LocationInt = ((int(rawData[55] + rawData[54] + rawData[53] + rawData[52] + rawData[51] + rawData[50] + rawData[49] + rawData[48],16)) * clusterSize)
	MFT_StartCluster = int(NTFS_MFT_LocationInt / clusterSize)
	MFT_Location = MFT_StartCluster * clusterSize
	print ("The volume serial number of partition " + str(no) + " is:                  " + volumeSerialNo_1 + " - " + volumeSerialNo_2)
	print ("Cluster size in bytes of the current NTFS partition:         " + str(clusterSize))
	print ("The first cluster of the MFT is:                             " + str(MFT_StartCluster))
	print ("The size of each Master File Table entry in bytes is:        " + str(MFTSize))

def myFmtCallback(command, modifier, arg):
    print(command)
    return 1    # TRUE

# Securely format the hard drive under Windows System
# Support FAT32, NTFS, FAT
def format_drive(Drive, Format, Title):
	if (sys.platform.startswith(flag_linux)):
		print ("")
	elif (sys.platform.startswith(flag_win)):
		fm = windll.LoadLibrary('fmifs.dll')
		FMT_CB_FUNC = WINFUNCTYPE(c_int, c_int, c_int, c_void_p)
		FMIFS_HARDDISK = 0x0B
		fm.FormatEx(c_wchar_p(Drive), FMIFS_HARDDISK, c_wchar_p(Format),
					c_wchar_p(Title), False, c_int(0), FMT_CB_FUNC(myFmtCallback))

format_drive('F:\\', 'NTFS', 'USBDrive')

platform()

