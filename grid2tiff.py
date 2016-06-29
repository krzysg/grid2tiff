from __future__ import print_function
import re
import os
import tifffile as tiff
import numpy as np
try:                 #python 2.x
    from itertools import izip
except ImportError:  #python3.x
    izip = zip

'''
This simple script concatenates small 2d/3d tiff files into one big image. Required tiff files naming:

    x_y_anyName.tif[f]

or

    x_y_z_anyName.tif[f]

where x, y, z are coordinates of tiff file image in an output image.

NOTICE: This script is not checking if input files cover all pixels of output image (if not they are zeroed) or if they overlap (if 
        yes, they will overlap randomly - the last file read from dir will be put on top).
        Size of output image is calculated basing on file with maximum x_y_z... coordinates in name + its image size
        All files from provided directory are taken (and must follow naming rules).
        
To use script provide correct paths for INPUT_DIR and OUTPUT_FILE
'''


INPUT_DIR = '/Users/gonciarz/Documents/MOSAIC/work/test/mosaic'
OUTPUT_FILE = '/tmp/ij.tif'


def getCoordinatesFromName(aFileName):
    # match 2D or 3D coordinates from filename in format x_y_z_anyName.anyExt or x_y_anyName.anyExt
    # Output: for 2D is [x, y] and for 3D is [x, y, z] or None if coords not found
    m = re.search(r"^([0-9]+){1}_([0-9]+){1}_([0-9]+){0,1}.*$", aFileName)
    if m == None:
        print("Parsing coordinates failed for name: [", aFileName, "]", sep = "")
        return None
    else:
        return [int(g) for g in m.groups() if g != None]

def findMaxCoordinates(aCoords):
    idx = None
    maxC = [-1] * len(aCoords[0])
    for i, c in enumerate(aCoords):
        if all([c[x] >= maxC[x] for x in range(len(c))]):
            idx = i
            maxC = c
    return idx, maxC

def calculateDims3D(aXYZcoords, aImgSizeZYX):
    imgsize = aImgSizeZYX[::-1] #reverse to have (x, y, z)
    return [a + b for a,b in izip(aXYZcoords, imgsize)]

def imageDimsTo3D(aInput):
    # Convert reversed (y,x) image dims from 2D to 3D (z,y,x):  (200, 100) -> (1, 200, 100)
    # or do nothing if already in 3D 
    if len(aInput) == 3: return aInput
    return (1, aInput[0], aInput[1])

def coordinates2Dto3D(aInput):
    # converts (x, y) coordinates to (x, y, z): (100, 200) -> (100, 200, 0) or do nothing if already 3D
    if len(aInput) == 3: return aInput
    return (aInput[0], aInput[1], 0)

def concatenateTiffs(aInputDir, aOutputFile):
    # Read all files in provided directory and find maximum coordinates
    tiffFiles = [f for f in os.listdir(aInputDir) if os.path.isfile(os.path.join(aInputDir, f)) and f.lower().endswith(('.tif', '.tiff'))]
    coordinates = [getCoordinatesFromName(c) for c in tiffFiles]
    if any(c is None for c in coordinates):
        print ("Provided directory contains not possible to parse tiff files!")
        return
    coordinates = [coordinates2Dto3D(c) for c in coordinates]
    if not coordinates:
        print ("No valid tiff files in provided directory!")
        return
    maxCoordsIdx, maxCoords = findMaxCoordinates(coordinates)
    maxCoordsFile = tiffFiles[maxCoordsIdx]
    print("Read ", len(tiffFiles), " TIFF files", sep = "")
    
    # Calculate output image size
    maxTiff = tiff.imread(os.path.join(aInputDir, maxCoordsFile))
    print("Max coordinates found in file:", maxCoordsFile, " x,y,z =", maxCoords, " image dims =", imageDimsTo3D(maxTiff.shape)[::-1])
    outDims = calculateDims3D(maxCoords, imageDimsTo3D(maxTiff.shape))
    outType = maxTiff.dtype
    print("Output image dimensions (x/y/z): ", outDims, " outType =", outType)
    
    # create output container
    outData = np.zeros(outDims[::-1], dtype=outType)
    outDataSize = outData.size * np.dtype(outData.dtype).itemsize
    print("Output data size: ", outDataSize)
    
    # Put images data to output data container
    for i in range(len(tiffFiles)):
        print ("Processing file #", i + 1, ": [", tiffFiles[i], "]", sep="")
        tiffFile =  tiff.imread(os.path.join(aInputDir, tiffFiles[i]))
        fromCoor = coordinates[i]
        toCoor = calculateDims3D(fromCoor, imageDimsTo3D(tiffFile.shape))
        shapeDims = calculateDims3D((0,0,0), imageDimsTo3D(tiffFile.shape))
        # data is kept in reverse order (z, y, x) so reverse coordinates
        # reshaping tiffFile has only effect for 2D images when size like (200, 100) is reshaped to (1, 200, 100) z/y/x
        outData[fromCoor[2]:toCoor[2], fromCoor[1]:toCoor[1], fromCoor[0]:toCoor[0]] = tiffFile.reshape(shapeDims[::-1])
    
    # Save file. BigTiff is not compatibile with imagej (but still it can be opened with Bio-Formats Import)
    isBigTiff = outDataSize  > 2**32 - 256  # 4GB - 256 for header
    print("Saving in BigTIFF mode:", isBigTiff) 
    tiff.imsave(aOutputFile, outData, imagej = not isBigTiff, bigtiff = isBigTiff)

if __name__ == '__main__':
    print("Parameters: input dir = [", INPUT_DIR, "] output filename = [", OUTPUT_FILE, "]", sep = "")
    concatenateTiffs(INPUT_DIR, OUTPUT_FILE)
    print("DONE!")
