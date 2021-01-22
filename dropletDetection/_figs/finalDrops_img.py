#!/usr/bin/env python  

__author__ = "Melissa A. Klocke"
__email__ = "klocke@ucr.edu"
__version__ = "1.1"

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

import sys
import os
import imageio

from matplotlib import rcParams
from skimage import data, color
from skimage.draw import circle_perimeter
from skimage.measure import label
from skimage.color import label2rgb
from itertools import zip_longest
from re import sub

'''This script is run by calling "python finalDrops_img.py $brightness-adjusted tiff filename$". This script
draws the finaldetected droplets on an image after the user has filtered out the artifacts of detection
and generated the "_final_data.csv" file. Both the brightness-adjusted tiff file and the final_data file 
must be in the same directory as this script.'''

def main():

	if len(sys.argv)==1:
		print("Need to specify file to process as a parameter.")
		print("   Exiting")
		exit()

	rcParams['font.family'] = 'sans-serif'
	rcParams['font.sans-serif'] = ['Arial']

	fn = sys.argv[1] 
	img, fname, df_vals = read_file(fn)

	comparison_image(img, df_vals, fname)


def read_file(fn):
	'''Reads in the brightness adjust .tif file for detection of circles. 
	Returns the image as numpy.array and the time point for further result filenames.'''
	basdir, basename = os.path.split(fn)
	fname, fext = os.path.splitext(basename)

	img = imageio.imread(fn)
	img = np.array(img)

	datafile = fname + '_final_data.csv'
	df = pd.read_csv(datafile, index_col=0)
	return img, fname, df


def draw_circles(comp_img, cx, cy, radii):
	'''Draw detected circles onto the brightness adjusted .tif image for visual inspection and removal or artifacts. 
	Removes x,y coordinates which are outside the image.'''
	img = color.gray2rgb(comp_img)
	for center_y, center_x, radius in zip(cy, cx, radii):
		radius = int(radius)
		circy, circx = circle_perimeter(center_y, center_x, radius)
		if np.max(circy) < len(img[:,0,0]) and  np.max(circx) < len(img[0,:,0]):
			img[circy, circx] = (220, 20, 20)
		else:
			continue
	return img


def comparison_image(comp_img, df, fn):
	'''Prepare a figure of the brightness-adjusted image with detected circles drawn in red and their IDs
	written near the upper-right side of the circle in colors corresponding to groups of 100. The different
	colors only aid in distnguishing circle IDs on busy comparison images, to aid removal of artificacts by ID.'''
	cx = df['X (pixels)']
	cy = df['Y (pixels)']
	radii = df['Radius (pixels)']
	idNum = df['droplet number']

	img_circles = draw_circles(comp_img, cx, cy, radii)

	fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 10))
	# ax[0].imshow(comp_img, cmap='gray')
	# ax[0].set_title('Original image of droplets')
	ax.imshow(img_circles)
	n = 0
	for i in idNum:
		if i<101:
			ax.text(cx[n],cy[n],str(i),fontsize=15, color='lightcoral') #round(accums[i],2)
		elif i<201:
			ax.text(cx[n],cy[n],str(i),fontsize=15, color='palegoldenrod') #round(accums[i],2)
		elif i<301:
			ax.text(cx[n],cy[n],str(i),fontsize=15, color='gray') #round(accums[i],2)
		elif i<401:
			ax.text(cx[n],cy[n],str(i),fontsize=15, color='mediumaquamarine') #round(accums[i],2)
		else:
			ax.text(cx[n],cy[n],str(i),fontsize=15, color='lightskyblue') #round(accums[i],2)
		n+=1
	ax.set_title('Detected circles (red) on droplet image')
	fig.tight_layout()
	fig.savefig('%s_finalimg.%s' % (fn.replace("/","__"), 'png'), dpi=700)
	plt.close()





if __name__ == '__main__':
	main()