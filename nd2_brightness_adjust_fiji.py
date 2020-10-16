__author__ = "Melissa A. Klocke"
__email__ = "klocke@ucr.edu"
__version__ = "1.0"


import os
from ij import IJ
from ij.io import DirectoryChooser 
from loci.plugins import BF 

os.system("mkdir _figs")

def getDir():
	dc = DirectoryChooser("Choose a folder")  
	sourcePath = dc.getDirectory()  
	if sourcePath is None:  
		print "User canceled the dialog!"  
	else:  
		print "Selected folder:", sourcePath
	targetPath = sourcePath + '_figs/' #figure out how to mkdir in script
	return sourcePath, targetPath

def openBFImp(sourcePath, fn):
	imp = BF.openImagePlus(sourcePath + fn)
	imp[0].show()

def to8bit():
	imp = IJ.getImage() 
	IJ.run(imp, "8-bit", "") 
	imp.updateAndDraw()

def kotaMiuraBrightness(targetPath, fn):
	'''Taken and updated from script by Kota Miura (2015) found at:
	http://wiki.cmci.info/documents/120206pyip_cooking/python_imagej_cookbook#automatic_brightnesscontrast_button'''
	autoThreshold = 0
	AUTO_THRESHOLD = 5000
	 
	imp = IJ.getImage()
	cal = imp.getCalibration()
	imp.setCalibration(None)
	stats = imp.getStatistics() # get uncalibrated stats
	imp.setCalibration(cal)
	limit = int(stats.pixelCount/10)
	histogram = stats.histogram() #int[] I just added the () after the histogram...?
	#histogram = imp.getHistogram(256) # trying to make it bin itself in a smooth way like the java version of the code
	if autoThreshold<10:
		autoThreshold = AUTO_THRESHOLD
	else:
		autoThreshold /= 2
	threshold = int(stats.pixelCount/autoThreshold)	#int
	i = -1
	found = False
	count = 0 # int
	while True:
	   i += 1
	   count = histogram[i]
	   if count>limit:
	      count = 0
	   found = count> threshold
	   if found or i>=255:
	#   if 0 not in (!found, i<255) :
	      break
	hmin = i #int
	i = 256
	while True:
	   i -= 1
	   count = histogram[i]
	   if count>limit:
	      count = 0
	   found = count> threshold
	   if found or i<1:
	#   if 0 not in (!found, i<255) :
	      break
	hmax = i #int
	IJ.setMinAndMax(imp, hmin, hmax)
	#IJ.run(imp, "8-bit", "")
	IJ.run(imp, "Apply LUT", "") # this step makes histogram odd
	imp.updateAndDraw()
	return threshold, limit, hmin, hmax

def saveToTiff(targetPath, fn):
	'''Grab the currently open image and save it to the targetDir as 
	long as the path exists and saving does not overwrite a file. '''
	imp = IJ.getImage()  

	if os.path.exists(targetPath) and os.path.isdir(targetPath):  
		print "folder exists:", targetPath  
		filepath = targetPath + fn + '.tif'
		#filepath = os.path.join(targetPath, fn, ".tif") 
		# Operating System-specific  
		if os.path.exists(filepath):  
			print "File exists! Not saving the image, would overwrite a file!"  
		elif IJ.saveAs(imp, "TIFF", filepath):  
			print "File saved successfully at ", filepath 
	else:  
		print "Folder does not exist or it's not a folder!" 
	imp.close()

sourceDir, targetDir = getDir()
for file in os.listdir(sourceDir):  
	if file.endswith('.nd2'): 
		basedir, basename = os.path.split(file) #these two lines
		fname, fext = os.path.splitext(basename) # for saving files
		openBFImp(sourceDir, file)
		to8bit()
		thresh, lim, tmin, tmax = kotaMiuraBrightness(targetDir, fname)
		print 'min:', tmin
		print 'max:', tmax
		#line about saving the above values to csv
		saveToTiff(targetDir, fname)