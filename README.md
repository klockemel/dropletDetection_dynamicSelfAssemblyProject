# dropletDetection_dynamicSelfAssemblyProject
This project contains the scripts used in the droplet detection and data extraction for the dynamic self-assembly project. Using the suggested directory organization is recommended, but not necessary as long as the input-output data for each script maintain their location relative to each other.

The workflow is as follows:

nd2_brightness_adjust_fiji.py

This script is run using ImageJ or Fiji's script editor/interpreter. This script reads all raw .nd2 files in a user-selected directory, applies the "auto" brightness-adjust process, and saves the adjusted images as 8-bit tiff files. To use, drag all images for a given sample which you intend to process to a "pre-processing" folder. I recommend working with just one sample at a time, i.e. all images for single set of parameters, to keep your task load manageable. Open the "nd2_brightness_adjust_fiji.py" file in Fiji, and select "Run". The resulting tiff files will be saved to the "_figs" folder. Move all .nd2 and tiff files to a "dropletDetection" folder to continue.

headless_nd2_scaled_droplet.py

This folder contains the droplet detection Python script, and the "_figs" folder where generated data will be created and further processing scripts are located. To run droplet detection, both the brightness-adjusted tiff file and raw nd2 files must be in this folder. Before running the droplet detection script, open it in your editor of choice, and input the appropriate 1) min radius, 2) max radius, 3) step size, and 4) num drops and save. You may have to guess these parameters at first. You can make an educated guess by opening either image in Fiji, and measuring the diameters of the droplets you wish to detect are. Run the script in your terminal, or interpreter of choice, by calling "python headless_nd2_scaled_droplet.py [filename].nd2". Running the script may take seconds or tens of minutes. Output will be stores in the "_figs" folder.

** in progress
