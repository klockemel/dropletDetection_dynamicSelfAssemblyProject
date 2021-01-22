 #!/usr/bin/env python

__author__ = "Melissa A. Klocke"
__email__ = "klocke@ucr.edu"
__version__ = "1.0"

import pandas as pd
import sys
import os

'''This file takes in the _values.csv file and filters out the "bad" droplets which the user gives as input in a comma-separated list.
It then save the _values.csv and _intensity.csv files with these values filtered out.'''

def main():
    if len(sys.argv)==1:
        print("Need to specify file to process as a parameter.")
        print("   Exiting")
        exit()

    fn = sys.argv[1] 
    short_fn, fn_inten, val_ext, int_ext = get_fnames(fn)

    bad = list([int(x) for x in input('\nProvide the list of bad droplets separated by ",": ').split(',')])
    bad.sort()
    bad = pd.Series(bad).unique()
    filter_df_val_revamp(fn, bad, short_fn, val_ext)
    filter_df_int_revamp(fn_inten, bad, short_fn, int_ext)

def get_fnames(fn):
    basdir, basename = os.path.split(fn)
    fname, fext = os.path.splitext(basename)
    split_char = '_'
    fn_short = fname.split(split_char)
    # fn_short = fn_short[:-2] ## hacky repeat, edit and switch commented out line if have to run this filter script more than 1x
    fn_short = fn_short[:-1]      # original
    fn_short = '_'.join([str(elem) for elem in fn_short])

    int_fn = fn_short + '_intensity.csv'      ## original line here
    # int_fn = fn_short + '_intensity.csv' ## hacky repeat
    ext_val = '_val_filtered.csv'
    ext_int = '_intensity_filtered.csv'
    return fn_short, int_fn, ext_val, ext_int

def filter_df_val_revamp(fname, bad, fn_short, ext):
    df = pd.read_csv(fname, index_col=0)
    good = ~df['droplet number'].isin(bad)
    df_filtered = df[good]
    df_filtered.to_csv(fn_short + ext)

def filter_df_int_revamp(fname, bad, fn_short, ext):
    df = pd.read_csv(fname, index_col=0)
    good = ~df['droplet number'].isin(bad)
    df_filtered = df[good]
    df_filtered.to_csv(fn_short + ext)

def filter_df_val(fname, bad, fn_short, ext):
    df = pd.read_csv(fname, index_col=0)
    good = list(range(len(df['droplet number'])))
    good = [i for i in good if i not in bad]
    df_filtered = df.filter(items=good, axis=0)
    df_filtered.to_csv(fn_short + ext)

def filter_df_int(fname, bad, fn_short, ext):
    df = pd.read_csv(fname, index_col=0)
    good = ~df['droplet number'].isin(bad)
    df_filtered = df[good]
    df_filtered.to_csv(fn_short + ext)

if __name__ == '__main__':
    main()