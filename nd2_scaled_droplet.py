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

def main():
    if len(sys.argv)==1:
        print("Need to specify file to process as a parameter.")
        print("   Exiting")
        exit()

    fn = sys.argv[1] 
    min_ac_relative = 0.45 
    #make sys.argv for all global vars
    os.system("mkdir _figs")

    print("\nOpening file: ", fn)
    comp_img, fname, timept = read_file(fn)
    full_img, pix_micron = nd2_read(fn)

    min_rad = np.int(input('\nProvide a minimum search radius (px): '))
    max_rad = np.int(input('Provide a maximum search radius (px): '))
    step = np.int(input('Provide a step size (px): '))

    hr = np.arange(min_rad, max_rad, step)
    hr_group = group_radii(hr)
    drops_df, num_drops = sequential_drop_detection(full_img, comp_img, hr_group, min_ac_relative, fname)
    # temp_write_drops_csv(drops_df, fn)

    cx = np.array(drops_df['X (pixels)'])
    cy = np.array(drops_df['Y (pixels)'])
    radii = np.array(drops_df['Radius (pixels)'])
    accums = np.array(drops_df['Probability count'])
    cx, cy, radii, accums = remove_low_accum(accums, cx, cy, radii, min_ac_relative, fname)
    cx, cy, radii, accums = remove_overlap(cx, cy, radii, accums)
    write_drops_csv(cx, cy, radii, accums, fname, timept, pix_micron)
    write_run_info_csv(fn, fname, pix_micron, min_rad, max_rad, step, num_drops)

    print("Making figures")

    mask, ind_mask = circle_mask(comp_img, cx, cy, radii, fname)

    intensity_of_droplets(full_img, ind_mask, radii, fname)

    comparison_image(comp_img, cx, cy, radii, accums, fname)
    # radii_hist(radii, pix_micron, fname)
    # diagnostics_plot(edges, hough_res,fname)

    print('Done')

def read_file(fn):
    basdir, basename = os.path.split(fn)
    fname, fext = os.path.splitext(basename)
    split_char = '_'
    timept = fname.split(split_char)
    timept = sub(r'\D', '', timept[-1])
    img = imageio.imread(fname + '.tif')
    img = np.array(img)
    return img, fname, timept

def nd2_read(fn):
    '''Read nd2 cy3 file and return the image as a 2d np.array of pixel intensity 
    both undcaled and scaled to int8 format for detection of droplets.'''
    img = ND2Reader(fn)
    pix_micron = img.metadata['pixel_microns']
    img = np.array(img[0])
    # img_comp = img-np.min(img)
    # img_comp = np.uint8(img * (255./np.max(img_comp)))
    return img, pix_micron

def grouper(iterable, chunksize):
    args = [iter(iterable)] * chunksize
    return zip_longest(*args, fillvalue=None)

def group_radii(hr):
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
    '''Pandas series are indexed differently than numpy arrays, so code breaks if the below data aren't converted
    before getting piped through "remove_overlap". This would be a good thing to understand later
    for now make sure this actually fixes the issue and you can get through different types of images
    with different needs
    Indexing should be the same but perhaps this is an issue with copy vs deepcopy?'''

    df = pd.DataFrame()
    num_drops = np.int(input('\nHow many droplets should be plotted: '))
    # print("\nFinding droplets and etracting intensities")

    for i in hr_group:
        accums, cx, cy, radii, edges, hough_res = find_droplets(comp_img, i)
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

def temp_write_drops_csv(df, fn):
    df.to_csv('_figs/%s_values.%s' % (fn.replace("/","__"), 'csv'))

def write_drops_csv(cx, cy, radii, accums, fn, timept, pix_micron):
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
    dict_vals = {'Filename': fn, 'Pix to micron': pix_micron, 'Min radius (px)': min_rad, 'Max radius (px)': max_rad, 'Step size (px)': step, 'Number of droplets': num_drops}
    df = pd.DataFrame([dict_vals])
    # df = df.reset_index()
    df.to_csv('_figs/%s_runvalues.%s' % (fname.replace("/","__"), 'csv'))

def find_droplets(img, hr):
    '''First a Canny filter is used to detect edges in the image. Then the Circular Hough 
    Transform evaluates the probability that circles along a range of radii is on detected edges.'''
    edges = canny(img, sigma=3, low_threshold=10, high_threshold=20) #make these global vars too
    hough_radii = hr
    hough_res = hough_circle(edges, hough_radii)
    accums, cx, cy, radii = hough_circle_peaks(hough_res, hough_radii)
    return accums, cx, cy, radii, edges, hough_res

def volume(radius, pix_micron):
    radius = radius*pix_micron
    vol = 4./3.*(np.pi*(radius**3)) #femtoliters
    return vol

def distance(x0, y0, r0, x1, y1, r1):
    '''Used to determine whether two circular objects are overlapping.'''
    dist = np.sqrt((x1-x0)**2+(y1-y0)**2)
    ovr = dist < (3./4.)*(r1+r0)
    return ovr

def remove_low_accum(accums, cx, cy, radii, min_ac_relative,fname):
    '''Removes droplets which have low accum counts and are likely to just be artifacts of the image processing.'''
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
    '''Removes accums, cx, cy and radii for overlapping objects.'''
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
    '''Keeps only the n most likely droplets, where n is user specified.'''
    cx_lim = cx[:num_drops]
    cy_lim = cy[:num_drops]
    radii_lim = radii[:num_drops]
    accums_lim = accums[:num_drops]
    return cx_lim, cy_lim, radii_lim, accums_lim

def draw_circles(comp_img, cx, cy, radii):
    '''Draw detected circles onto the original image. Removes x,y coordinates which are outside the image.'''
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
    '''Create a mask using the detected droplets, and a list of individual masks for each
    droplet.'''
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
    
    # fig, ax = plt.subplots()
    # ax.imshow(img_m)
    # fig.tight_layout()
    # fig.savefig('_figs/%s_mask.%s' % (fn.replace("/","__"), 'png'), dpi=700)
    # plt.close()

    # if np.max(circy) < len(img[:,0,0]) and  np.max(circx) < len(img[0,:,0]):
    #     img[circy, circx] = (220, 20, 20)
    # else:
    #     continue
    return mask, ind_mask

def intensity_of_droplets(img, ind_mask, radii, fn):
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
    droplets are far enough away from 0 that this does not yet cause confusion...'''
    temp = img.copy()
    temp = np.ma.array(temp, mask=mask, dtype=int)
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

    # fig, ax = plt.subplots()
    # ax.imshow(temp)
    # fig.tight_layout()
    # fig.savefig('_figs/%s_mask_d%s.%s' % (fn.replace("/","__"), num, 'png'), dpi=700)
    # plt.close()

def comparison_image(comp_img, cx, cy, radii, accums, fn):
    '''Prepare a figure of the orignal image next to the image with droplets superimposed in red.'''
    img_circles = draw_circles(comp_img, cx, cy, radii)

    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 10))
    # ax[0].imshow(comp_img, cmap='gray')
    # ax[0].set_title('Original image of droplets')
    ax.imshow(img_circles)
    for i in range(cx.shape[0]):
        ax.text(cx[i],cy[i],str(i),fontsize=20, color='gray') #round(accums[i],2)
    ax.set_title('Detected circles (red) on droplet image')
    fig.tight_layout()
    fig.savefig('_figs/%s_compimg.%s' % (fn.replace("/","__"), 'png'), dpi=700)
    # plt.close()

def diagnostics_plot(edges, hough_res,fn):
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
        fig.savefig('_figs/%s_diagnostics_%s.%s' % (fn.replace("/","__"), str(i), 'png'), dpi=700)
        plt.close()

def hist_full_img(img, fn):
    '''To get the intensity values and bins from the complete image. Plotting
    code is not correct atm.'''
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
    '''Plotting the mask with droplet labels for troubleshooting. Needs to be added/cleaned.'''
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 4))
    ax.imshow(label_img)
    for i in range(len(cx)):
        ax.text(cx[i],cy[i],str(drop_no_array[i]),fontsize=6)
    fig.tight_layout()
    fig.savefig('_figs/%s_labeled.%s' % (fn.replace("/","__"), 'png'), dpi=700)
    plt.close()

def radii_hist(radii, pix_micron, fn):
    '''Plot a histogram of the detected droplet radii.'''
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

if __name__ == '__main__':
    main()
