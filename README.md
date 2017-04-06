# grid2tiff
This simple script concatenates small 2d/3d tiff files into one big image.
Required tiff files naming:

    x_y_anyName.tif[f]    (like 0_20_myImg.tif, 25_010_img.tiff)

or

    x_y_z_anyName.tif[f] (like 0_20_5_myImg.tif, 025_010_3_img.tiff)

where x, y, z are 0-based coordinates of tiff file image in an output image.
(they may contain leading zero(s)).

NOTICE: 
* This script is not checking if input files cover all pixels of output image (if not they are zeroed) or if they overlap (if yes, they will overlap randomly - the last file read from dir will be put on top).
* Size of output image is calculated basing on file with maximum x_y(_z) coordinates in name + its image size
* All tiff files from provided directory are taken (and must follow naming rules).
* It is possible to give 3D coordinates for 2D images (they are treated as a 1 pixel depth) or 2D coordinates for 3D (they are then position in 2D x/y space at 0 coordinate for z (depth)) or even mix all above
* script is kept easy without over-safty-checkings to be easy to modify (initial idea was to easy concatenate output files produced in many nodes in HPC cluster)

To use script provide correct paths for INPUT_DIR and OUTPUT_FILE in a script.

Requires (and tested version):
* numpy Version: 1.12.1
* tifffile Version: 0.11.1
