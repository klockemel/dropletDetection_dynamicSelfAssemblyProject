1-22-2021 MAK

In each example image folder are a few different files:
1. raw nd2 micrograph (can be opened with imageJ/FIJI Bio-formats importer for further inspection)
2. brightness adjusted tif of the micrograph for quick observation of droplet size and distribution
3. a csv of the values input to the droplet detection script to get the following two example output images - min radius, max radius, step size, and number of droplets in each subgroup. The last parameter is further explained within comments in the script but ultimately helps control runtime/number of droplets detected
4. the initial output image in which detected droplets are outlined in red and given a numeric ID (later versions change the font size for each 100 set of droplets to increase legibility)
5. the final detected droplets after artifacts which are ID'd using the above "compimg" are removed from the final sample using the appropriate filter scripts

Input parameters may be adjusted based on the user's needs: range of radii present in the image, time limitations due to processing many images, step size based on individual need for precision, and so on.

img1: No artifacts found, no droplets were removed.
img2: 3 artifacts found, droplets 385, 420, 421 removed.
