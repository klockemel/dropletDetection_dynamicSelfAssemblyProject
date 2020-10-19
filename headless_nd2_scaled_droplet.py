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
from nd2reader import ND2Reader

from skimage import data, color
from skimage.transform import hough_circle, hough_circle_peaks
from skimage.feature import canny
from skimage.draw import circle_perimeter
from skimage.measure import label
from skimage.color import label2rgb
from itertools import zip_longest
from re import sub

#make file executable chmod u+x filename

'''This script runs without user input. Once runvalues for min and max rad, step size, and # of circles to limit
search to are determined, those values can be edited directly here and the code will run by just calling:
python headless_nd2_scaled_droplet.py $filename

To run this script, have both the raw .nd2 file as well as an auto brightness-adjusted .tif file scaled to 8-bit in 
Fiji in the same directory as this script. All output files will be saved to a "./_figs/" directory created by
running the script.'''

def main():
    '''Main function executes the script by calling on the functions in this file and using the parameters defined
    below on the file named in the command line.'''
    if len(sys.argv)==1:
        print("Need to specify file to process as a parameter.")
        print("   Exiting")
        exit()

    fn = sys.argv[1] 
    min_ac_relative = 0.45 
    os.system("mkdir _figs")

    print("\nOpening file: ", fn)
    comp_img, fname, timept = read_file(fn)
    full_img, pix_micron = nd2_read(fn)

    min_rad = np.int(12)                #### edit min rad here
    max_rad = np.int(60)                #### edit max rad here
    step = np.int(1)                    #### edit step size here

    '''Because the range of radii searched across in the image is generally very large, and computational time and resources
    grow greatly if searching across the whole range at once, circles are first detected using sequential_drop_detection
    in small radii groups defined in group_radii function. In these small groups, the weakest 45% of circles
    (determined by their accum value) are dropped, circles which are overlapping are compared and the strongest
    circle (by accum value) is kept. Finally the remaining circles in each small hr_group, which are sorted by their
    strength or accums value, are capped at the num_drops limiting value in sequential_drop_detection, for three reasons:
    1) the code can find many more circle than there actually are in the image, 2) if the code finds unlimited circles,
    it will continue to run for more than 30 minutes without producing useful results, and 3) if there are too many circles, 
    t is impossible to visually inspect the image with detected circles to remove any artifacts which may have been included 
    in results.'''

    hr = np.arange(min_rad, max_rad, step)
    hr_group = group_radii(hr)
    drops_df, num_drops = sequential_drop_detection(full_img, comp_img, hr_group, min_ac_relative, fname)

    '''After circles are detected and sorted in small radii groups above, all circles are pooled together to 
    remove the weakest 45% of circles (as determined by their accums value), remove overlapping circles, and save
    the results to .csv files.'''

    cx = np.array(drops_df['X (pixels)'])
    cy = np.array(drops_df['Y (pixels)'])
    radii = np.array(drops_df['Radius (pixels)'])
    accums = np.array(drops_df['Probability count'])
    cx, cy, radii, accums = remove_low_accum(accums, cx, cy, radii, min_ac_relative, fname)
    cx, cy, radii, accums = remove_overlap(cx, cy, radii, accums)
    write_drops_csv(cx, cy, radii, accums, fname, timept, pix_micron)
    write_run_info_csv(fn, fname, pix_micron, min_rad, max_rad, step, num_drops)

    '''The lines below are used to: 
    - extract pixel brightness values from within the detected circles and save the results to a .csv file
    - make a figure in which detected circles are drawn with ID numbers on a brightness-adjusted image for 
    visual inspection and confirmation
    - plot diagnostics plots: a histogram of radii and the results from the edge detection and hough_circle functions.'''

    print("Making figures")
    mask, ind_mask = circle_mask(comp_img, cx, cy, radii, fname)
    intensity_of_droplets(full_img, ind_mask, radii, fname)

    comparison_image(comp_img, cx, cy, radii, accums, fname)
    # radii_hist(radii, pix_micron, fname)
    # diagnostics_plot(edges, hough_res,fname)

    print('Done')

def read_file(fn):
    '''Reads in the brightness adjust .tif file for detection of circles. 
    Returns the image as numpy.array and the time point for further result filenames.'''
    basdir, basename = os.path.split(fn)
    fname, fext = os.path.splitext(basename)
    split_char = '_'
    timept = fname.split(split_char)
    timept = sub(r'\D', '', timept[-1])
    img = imageio.imread(fname + '.tif')
    img = np.array(img)
    return img, fname, timept

def nd2_read(fn):
    '''Reads raw .nd2 file with full bit depth for pixel intensity extraction.
    Reads the conversion for pixels to microns for the image from metadata.'''
    img = ND2Reader(fn)
    pix_micron = img.metadata['pixel_microns']
    img = np.array(img[0])
    return img, pix_micron

def grouper(iterable, chunksize):
    args = [iter(iterable)] * chunksize
    return zip_longest(*args, fillvalue=None)

def group_radii(hr):
    '''Groups the radii into small groups spanning chunksize steps. The final group of largest radii will span
    whatever remaining steps are left, which may be chunksize or less depending on the number of radii searched
    I left chunksize as 10 for all data processed for 2020 nanotubes in droplets paper.'''
    # removed the Nones in a clunky way. Try to for and can improve if necessary later
    chunksize = 10
    hr_group = list(grouper(hr, chunksize))
    hr_group_filtered = []
    for item in hr_group:
        item = list(item)
        item = list(filter(None, item))
        hr_group_filtered.append(item)
    return hr_group_filtered

def sequential_drop_detection(img, comp_img, hr_group, min_ac_relative, fn):
    '''Full description of this function above in main. The short version is this function breaks the very large and
    computationally heavy search of circles over a large range (ex. 10-50, step size 1) into smaller groups.
    Circles detected within these groups are compared and removed based on strength, overlapping, and a total
    cap on the number of circles allowed in each group (num_drops). The results from each small group are compiled
    into one large dataframe which contains accums, cx, cy, radius of each circle for further processing.'''

    df = pd.DataFrame()
    num_drops = np.int(400)
    # print("\nFinding circles and etracting intensities")

    for i in hr_group:
        accums, cx, cy, radii, edges, hough_res = find_droplets(comp_img, i)
        # diagnostics_plot(edges, hough_res, fn, i)		### Will plot the hough intensities for each HR group
        cx, cy, radii, accums_prob = remove_low_accum(accums, cx, cy, radii, min_ac_relative, fn)
        cx, cy, radii, accums = remove_overlap(cx, cy, radii, accums_prob)
        cx, cy, radii, accums = lim_num_drops(cx, cy, radii, accums, num_drops)
        accums = np.round(accums, decimals=5)
        dict_vals = {'X (pixels)': cx, 'Y (pixels)': cy, 'Radius (pixels)': radii, 'Probability count': accums}
        temp_df = pd.DataFrame(dict_vals)
        df = pd.concat([df, temp_df], sort=False)

    df = df.reset_index(drop=True)
    df = df.reset_index()
    df = df.rename(columns={'index': 'droplet number'})
    return df, num_drops

def write_drops_csv(cx, cy, radii, accums, fn, timept, pix_micron):
    '''Save all information about final detected circles to a .csv file.'''
    vol = []
    for i in range(cx.shape[0]):
        temp = volume(radii[i], pix_micron)
        temp = temp * (10**-3)
        temp = np.round(temp, decimals=5)
        vol.append(temp)
    accums = np.round(accums, decimals=5)
    dict_vals = {'X (pixels)': cx, 'Y (pixels)': cy, 'Radius (pixels)': radii, 'Probability count': accums, 'Time': timept, 'Volume (pL)': vol}
    df = pd.DataFrame(dict_vals)
    df = df.reset_index()
    df = df.rename(columns={'index': 'droplet number'})
    df.to_csv('_figs/%s_values.%s' % (fn.replace("/","__"), 'csv'))

def write_run_info_csv(fn, fname, pix_micron, min_rad, max_rad, step, num_drops):
    '''This function saves all input parameters given by the user for each run of the code including the filename, 
    the conversion factor from pixels to microns for the inout image, min and max radius searched through, 
    the step size used to determine which discrete radius values to search for between the min and max value, and the 
    limit on the number of circles found for each radii group (num_drops in sequential_drop_detection).'''
    dict_vals = {'Filename': fn, 'Pix to micron': pix_micron, 'Min radius (px)': min_rad, 'Max radius (px)': max_rad, 'Step size (px)': step, 'Number of droplets': num_drops}
    df = pd.DataFrame([dict_vals])
    # df = df.reset_index()
    df.to_csv('_figs/%s_runvalues.%s' % (fname.replace("/","__"), 'csv'))

def find_droplets(img, hr):
    '''First a Canny filter (canny) is used to detect edges in the image and returns a boolean image. 
    Then the Circular Hough Transform (hough_circle) transforms the boolean image to hough space for a range of radii. 
    Peaks where circles are likely to be located in the hough space array (hough_res) are found with the hough_circle_peaks 
    unction. For the range of radii given, the strengrh of different circle peaks is detemined through "votes", and the
    peak strength value (accums) is returned along with the center (x,y) corrdinates and radius for 
    each detected circle. See http://scikit-image.org/ for more information on each function.'''
    edges = canny(img, sigma=3, low_threshold=10, high_threshold=20)            #These are the values used for all data in 2020 paper
    hough_radii = hr
    hough_res = hough_circle(edges, hough_radii)
    accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii)
    return accums, cx, cy, radii, edges, hough_res

def volume(radius, pix_micron):
    '''Calculates the volume of the droplet in femtoliters using the radius of a given circle.'''
    radius = radius*pix_micron
    vol = 4./3.*(np.pi*(radius**3)) #femtoliters
    return vol

def distance(x0, y0, r0, x1, y1, r1):
    '''Used to determine whether two circular objects are overlapping. Objects are determined to be overlapping
    if they are closer than 3/4 the sum of each radius. This does leave more possibility for large overlapping 
    circles to remain, but those can be removed after visual inspection after the code has run.'''
    dist = np.sqrt((x1-x0)**2+(y1-y0)**2)
    ovr = dist < (3./4.)*(r1+r0)
    return ovr

def remove_low_accum(accums, cx, cy, radii, min_ac_relative,fname):
    '''Removes circles which have low accum counts and are likely to just be artifacts of the image processing.
    min_ac_relative is hardcoded at the beginning of the main script. For all data processed for the 2020 nanotube
    in circles paper, it was set to 0.45, so that the bottom 45% of detected objects were dropped.
    Optional code at the end of the function to plot a histogram of the accums values for all detected objects 
    with a vertical line at the cut-off value use_min.'''
    use_min=min_ac_relative*accums[0]

    good = accums > use_min
    cx_prob = cx[good]
    cy_prob = cy[good]
    radii_prob = radii[good]
    accums_prob = accums[good]

    # fig, ax = plt.subplots()
    # ax.hist(accums,weights=accums,bins=50,zorder=-1000)
    # ax.axvline(use_min,lw=1.5,zorder=-100,c="r",ls=":")
    # fig.tight_layout()
    # fig.savefig('_figs/%s_which_dropped.%s' % (fname.replace("/","__"), 'png'), dpi=700)

    return cx_prob, cy_prob, radii_prob, accums_prob

def remove_overlap(cx, cy, radii, accums_prob):
    '''Removes accums, cx, cy and radii for overlapping objects determined by the two circles radii using the 
    distance function above.'''
    good = []
    bad = []

    for i in range(np.array(cx.shape[0])):
        if i in bad:
            continue
        for j in range(i+1, np.array(cx.shape[0])):
            ovr = distance(cx[i], cy[i], radii[i], cx[j], cy[j], radii[j])
            if ovr == True:
                bad.append(j)
        good.append(i)

    cx_nodup = np.array([cx[i] for i in good])
    cy_nodup = np.array([cy[i] for i in good])
    radii_nodup = np.array([radii[i] for i in good])
    accums_nodup = np.array([accums_prob[i] for i in good])
    return cx_nodup, cy_nodup, radii_nodup, accums_nodup

def lim_num_drops(cx, cy, radii, accums, num_drops):
    '''Keeps only n circles from a list sorted by circle strength or accums value, where n is user specified num_drops.'''
    cx_lim = cx[:num_drops]
    cy_lim = cy[:num_drops]
    radii_lim = radii[:num_drops]
    accums_lim = accums[:num_drops]
    return cx_lim, cy_lim, radii_lim, accums_lim

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

def circle_mask(img, cx, cy, radii, fn):
    '''Create a mask using all detected circles, and a list of individual masks for each circle.'''
    y, x = img.shape
    mask = np.zeros((y,x))
    y, x  = np.indices((y,x))
    ind_mask = []
    num = 0

    for center_y, center_x, radius in zip(cy, cx, radii):
        radius = int(radius)
        circle = (x-center_x)**2 + (y-center_y)**2 < radius**2
        ind_mask.append(circle)
        mask += circle
        num += 1

    for var in range(len(ind_mask)):
        frame = ind_mask[var]
        frame = np.invert(frame)
        ind_mask[var] = frame

    mask = mask.astype(bool)
    mask = np.invert(mask)
    img_m = img.copy()
    img_m[mask] = 0
    
    fig, ax = plt.subplots()
    ax.imshow(img_m)
    fig.tight_layout()
    fig.savefig('_figs/%s_mask.%s' % (fn.replace("/","__"), 'png'), dpi=700)
    plt.close()

    # if np.max(circy) < len(img[:,0,0]) and  np.max(circx) < len(img[0,:,0]):
    #     img[circy, circx] = (220, 20, 20)
    # else:
    #     continue
    return mask, ind_mask

def intensity_of_droplets(img, ind_mask, radii, fn):
    '''Using the raw .nd2 image with full bit depth, and the mask of detected circles, extract the pixel value histogram
    for each circle. Save the resulting pixel value histogram data with the circle ID and radius to a .csv file.'''
    full_dhist = pd.DataFrame()
    num = 0
    for val in range(len(ind_mask)):
        mask = ind_mask[val]
        radd = np.array(radii[val])
        temp = extract_intensities(img, mask, num, radd, fn)
        full_dhist = full_dhist.append(temp)
        num += 1
    full_dhist = full_dhist.reset_index(drop=True)
    full_dhist.to_csv('_figs/%s_intensity.%s' % (fn.replace("/","__"), 'csv'))

def extract_intensities(img, mask, num, radd, fn):
    '''This function extracts the pixel values for a an image with a given mask.
    Currently, I have all areas outside the ROI set to 0. There may be a 
    better way to do this in the future, although all of our image counts in the 
    circles are far enough away from 0 that this does not yet cause confusion...'''
    temp = img.copy()
    temp = np.ma.array(temp, mask=mask, dtype=int)
    # fig, ax = plt.subplots()
    # ax.imshow(temp)
    # fig.tight_layout()
    # fig.savefig('_figs/%s_mask_d%s.%s' % (fn.replace("/","__"), num, 'png'), dpi=700)
    # plt.close()
    temp = temp.compressed()
    # temp[mask] = 0

    dhist, dbin = np.histogram(temp, bins=256)
    dbin = dbin[:-1]
    dno = np.array([str(num)])
    dno = np.repeat(dno, len(dbin))
    radd = np.repeat(radd, len(dbin))
    dict = {'bin start': dbin, 'count': dhist, 'radius': radd, 'droplet number': dno}
    drop_hist = pd.DataFrame(dict)
    drop_hist.reset_index(inplace=True)
    drop_hist.rename(columns={'index':'bin number'}, inplace=True)
    return drop_hist

def comparison_image(comp_img, cx, cy, radii, accums, fn):
    '''Prepare a figure of the brightness-adjusted image with detected circles drawn in red and their IDs
    written near the upper-right side of the circle in colors corresponding to groups of 100. The different
    colors only aid in distnguishing circle IDs on busy comparison images, to aid removal of artificacts by ID.'''
    img_circles = draw_circles(comp_img, cx, cy, radii)

    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 10))
    # ax[0].imshow(comp_img, cmap='gray')
    # ax[0].set_title('Original image of droplets')
    ax.imshow(img_circles)
    for i in range(cx.shape[0]):
        if i<101:
            ax.text(cx[i],cy[i],str(i),fontsize=15, color='gray') #round(accums[i],2)
        elif i<201:
            ax.text(cx[i],cy[i],str(i),fontsize=15, color='palegoldenrod') #round(accums[i],2)
        elif i<301:
            ax.text(cx[i],cy[i],str(i),fontsize=15, color='lightcoral') #round(accums[i],2)
        elif i<401:
            ax.text(cx[i],cy[i],str(i),fontsize=15, color='mediumaquamarine') #round(accums[i],2)
        else:
            ax.text(cx[i],cy[i],str(i),fontsize=15, color='lightskyblue') #round(accums[i],2)
    ax.set_title('Detected circles (red) on droplet image')
    fig.tight_layout()
    fig.savefig('_figs/%s_compimg.%s' % (fn.replace("/","__"), 'png'), dpi=700)
    plt.close()

def diagnostics_plot(edges, hough_res,fn, hgroup):
    '''Plots of the hough transform at each radius tested.'''
    fig, ax = plt.subplots()
    ax.imshow(edges)
    ax.set_title('edges')
    fig.tight_layout()
    fig.savefig('_figs/%s_diagnostics.%s' % (fn.replace("/","__"), 'png'), dpi=700)
    plt.close()

    for i in range(hough_res.shape[0]):
        fig, ax = plt.subplots()
        ax.imshow(hough_res[i], cmap='gray')
        ax.set_title('hough res')
        fig.tight_layout()
        fig.savefig('_figs/%s_diagnostics_%s_%s.%s' % (fn.replace("/","__"), str(hgroup), str(i), 'png'), dpi=700)
        plt.close()

def hist_full_img(img, fn):
    '''To get the intensity values and bins from the complete image. This information is useful in detemining if
    and image is overexposed. Plotting code is not correct atm.'''
    dhist, dbin = np.histogram(img, bins=256)
    dbin = dbin[:-1]
    dict = {'bin start': dbin, 'count': dhist}
    drop_hist = pd.DataFrame(dict)
    drop_hist = drop_hist.reset_index()

    # fig, ax = plt.subplots()
    # ax.hist(val)
    # fig.tight_layout()
    # fig.savefig('_figs/%s_hist.%s' % (fn.replace("/","__"), 'png'), dpi=700)
    # plt.close()

def labeled_drop(img, cx, cy, drop_no_array):
    '''Plotting the mask with circle labels for troubleshooting. Needs to be added/cleaned.'''
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 4))
    ax.imshow(label_img)
    for i in range(len(cx)):
        ax.text(cx[i],cy[i],str(drop_no_array[i]),fontsize=6)
    fig.tight_layout()
    fig.savefig('_figs/%s_labeled.%s' % (fn.replace("/","__"), 'png'), dpi=700)
    plt.close()

def radii_hist(radii, pix_micron, fn):
    '''Plot a histogram of the detected circle radii.'''
    radii_um = pix_micron*radii
    fig, ax = plt.subplots()
    ax.hist(radii_um, bins=len(np.arange(10, 50, 2)), rwidth=0.8)
    ax.set_title('A histogram of detected droplet radii (um)')
    ax.set_xlabel('Droplet radius (um)')
#    ax.set_xticks(np.round(1.61*np.arange(10, 50, 2)))
    ax.set_ylabel('Count')
    fig.tight_layout()
    fig.savefig('_figs/%s_radhist.%s' % (fn.replace("/","__"), 'png'), dpi=700)
    plt.close()


'''A note on sequential circle detection past troubleshooting: Pandas series are indexed differently than numpy arrays, 
so code breaks if the below data aren't converted before getting piped through "remove_overlap". This would be a good 
thing to understand later for now make sure this actually fixes the issue and you can get through different types of 
images with different needs. Indexing should be the same but perhaps this is an issue with copy vs deepcopy?'''



if __name__ == '__main__':
    main()
