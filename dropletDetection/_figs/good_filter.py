#!/usr/bin/env python

__author__ = "Melissa A. Klocke"
__email__ = "klocke@ucr.edu"
__version__ = "1.0"


import pandas as pd
import sys
import os

'''This file takes in the _values.csv file and separates the "good" droplets which the user gives as input in a comma-separated list.
It then save the _values.csv and _intensity.csv files with only these "good" values remaining. This is to be used when it is easier 
to label the correctly-detected droplets.'''

def main():
    if len(sys.argv)==1:
        print("Need to specify file to process as a parameter.")
        print("   Exiting")
        exit()

    fn = sys.argv[1] 
    short_fn, fn_inten, val_ext, int_ext = get_fnames(fn)
    good = list([int(x) for x in input('\nProvide the list of good droplets separated by ",": ').split(',')])
    good.sort()
    good = pd.Series(good).unique()
    filter_df_val(fn, good, short_fn, val_ext)
    filter_df_int(fn_inten, good, short_fn, int_ext)

def get_fnames(fn):
    basdir, basename = os.path.split(fn)
    fname, fext = os.path.splitext(basename)
    split_char = '_'
    fn_short = fname.split(split_char)
    fn_short = fn_short[:-1]
    fn_short = '_'.join([str(elem) for elem in fn_short])

    int_fn = fn_short + '_intensity.csv'
    ext_val = '_val_filtered.csv'
    ext_int = '_intensity_filtered.csv'
    return fn_short, int_fn, ext_val, ext_int

def filter_df_val(fname, good, fn_short, ext):
    df = pd.read_csv(fname, index_col=0)
    df_filtered = df.filter(items=good, axis=0)
    df_filtered.to_csv(fn_short + ext)

def filter_df_int(fname, good, fn_short, ext):
    df = pd.read_csv(fname, index_col=0)
    good = df['droplet number'].isin(good)
    df_filtered = df[good]
    df_filtered.to_csv(fn_short + ext)

if __name__ == '__main__':
    main()