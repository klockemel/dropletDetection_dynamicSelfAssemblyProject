# dropletDetection_dynamicSelfAssemblyProject
The goal of this project is to 1) establish a python-based automated detection of circular objects of varying sizes in micrographs and extract their pixel brightness values and 2) illustrate temporal dynamics of different nanotube monomer behaviors via an ODE model in Matlab. The primary task of the image processing portion of this project was to scale-up the quantification of data from differently sized circular droplets from tens of droplets per image (by hand in FIJI) to hundreds of droplets per image via digital image processing (DIP). The DIP scripts here work with proprietary "nd2" files from Nikon NIS-Elements, but can be adapted to process other file formats. This project contains all scripts used in the droplet detection and data extraction for the dynamic self-assembly project. Using the suggested directory organization is recommended, but not necessary as long as the input-output data for each script maintain their location relative to each other.

Dependencies are listed in the ".dependencies" file. This project uses ND2Reader from nd2reader, found <a href="https://github.com/rbnvrw/nd2reader">here.</a> 

The workflow is as follows:

### pre-processing > nd2_brightness_adjust_fiji.py

This folder contains a script run using ImageJ or Fiji's script editor/interpreter. This script reads all raw .nd2 files in a user-selected directory, applies the "auto" brightness-adjust process, and saves the adjusted images as 8-bit tiff files. To use, drag all images for a given sample which you intend to process to a "pre-processing" folder. I recommend working with just one sample at a time, i.e. all images for single set of parameters, to keep your task load manageable. Open the "nd2_brightness_adjust_fiji.py" file in Fiji, and select "Run". The resulting tiff files will be saved to the "_figs" folder. Move all .nd2 and tiff files to a "dropletDetection" folder to continue.

**Input files in pre-processing directory:** raw nd2 micrograps

**Output files in pre-processing/_figs directory:** brightness-adjusted tiffs

**Commands:** NA, run in FIJI/ImageJ

### dropletDetection > headless_nd2_scaled_droplet.py

This folder contains the droplet detection Python script, and the "_figs" folder where generated data will be created and further processing scripts are located. The "_figs" directory will be created when running the script for the first time. To run droplet detection, both the brightness-adjusted tiff file and raw nd2 files must be in this folder. 

Before running the droplet detection script, open the script in your editor of choice, and input the following parameters 1) min radius (pixels), 2) max radius (pixels), 3) step size (pixels), and 4) num drops and save. Further explanation of these parameters are found in comments in the script. 

Input parameters may be adjusted based on the user's needs: range of radii present in the image, time limitations due to processing many images, step size based on individual need for precision, and so on. You may have to guess these parameters at first. You can make an educated guess by opening either image in Fiji, and measuring the diameters of the droplets you wish to detect. Run the script in your terminal, or interpreter of choice, by calling "python headless_nd2_scaled_droplet.py [filename].nd2". 

Running the script may take seconds or tens of minutes. Output will be stores in the "_figs" folder. Note: for a time series, the script will have to be run on each image individually. I usually go through the entire workflow for all timepoints at a given set of parameters at once, i.e. process all timepoints for 50 nM gene at once.

**Input files in dropletDetection directory:** fn_nd2, fn.tif where "fn" is your filename

**Output files in dropletDetection/_figs directory:** fn_values.csv, fn_intensity.csv, fn_runvalues.csv, fn_compimg.png 

**Commands:**

    python headless_nd2_scaled_droplet.py fn.nd2 

### dropletDetection/_figs > remaining scripts

This folder will contain the output of the detection code, as well as scripts for artifact removal, skewness and kurtosis generation, and labeling the final set of detected droplets on the brightness adjusted image. 
  
  1. The first step in continuing the processing, is to visually confirm the detected droplets and remove any artifacts. By creating a text file, you can keep track of droplet IDs of artifacts which need to be removed in each image (in our case, at each time point). This list should be comma separated, and there is a maximum number of artifacts which can removed with each run of the filter scripts. This limitation is caused by the having the use provide a comma-separated list in the dialogue box and can probably be resolved by inputting the artifact IDs in another way (reading a .csv file, etc). Save the text file in which you list droplets you removed for future reference. You can also note which timepoints in which you did not have any artifacts to remove.
  
  2a. If you are taking note of the IDs of artifacts, you will run the "bad_filter.py" script.
  
  **Input files:** fn_values.csv, fn_intensity.csv
    
  **Output files:** fn_val_filtered.csv, fn_intensity_filtered.csv
    
  **Commands:**
  
    python bad_filter.py fn_values.csv
  
  2b. If you are noting the IDs of correctly-detected droplets, you will run the "good_filter.py" script. 
    
  **Input files:** fn_values.csv, fn_intensity.csv
    
  **Output files:** fn_val_filtered.csv, fn_intensity_filtered.csv
    
  **Commands:** 
  
    python good_filter.py fn_values.csv 
  
The filter scripts will create new files with the artifacts removed for both the "fn_values.csv" and "fn_intensity.csv" files. I suggest keeping both the filtered and unfiltered data for your records, but continue processing only the filtered data. You will have to run the filter scripts for each timepoint in your series. Because the following scripts are expecting files with names following the format "fn_intensity_filtered.csv" and "fn_val_filtered.csv", if you do not have any artifacts to remove you can copy the "fn_values.csv" and "fn_intensity.csv" files and rename the copies to follow the necessary format. 
  
  3. Once artifacts are removed, skewness and kurtosis values can be generated using the "generating_skew_kurt_dno.py" script.
  
  **Input files:** fn_val_filtered.csv, fn_intensity_filtered.csv
    
  **Output files:** fn_final_data.csv, fn_generated_intensities.csv
    
  **Commands:** 
    
      python generating_skew_kurt_dno.py fn_intensity_filtered.csv
    
  4. Finally, an updated reference image with only the final detected droplets can be prepared using the finalDrops_img.py script.
  
  **Input files:** fn_final_data.csv, fn.tif
    
  **Output files:** fn_finalimg.png
    
  **Commands:** 
  
    python finalDrops_img.py fn.tif
    
Further analysis of the data (skewness, kurtosis, droplet size, etc)  can be done in separate plotting scripts or an interactive environment.

**Two representative images from the project are available to try with the code in the _dropletDetection_examples_ directory.**


## Matlab Simulations 

The code to simulate the ODE models from S7 can be found in the matlab_simulations directory. The plots can be rendered by running those files in the local directory path. The shading and color of those plots were done using Kristjan Jonasson's RGB.m function file. You can download it <a href="https://www.mathworks.com/matlabcentral/fileexchange/24497-rgb-triple-of-color-name-version-2?s_tid=prof_contriblnk">here.</a> 
