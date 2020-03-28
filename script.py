# Author: Sébastien Tosi (IRB Barcelona)
# Version: 1.1
# Date: 04/02/2019

import os
import numpy as np
from skimage import io
from skimage import morphology
from skimage.filters import gaussian, threshold_adaptive
from skimage.feature import peak_local_max
from skimage.morphology import watershed,remove_small_objects
import skimage.segmentation
from scipy import ndimage
import argparse
from argparse import RawTextHelpFormatter
import glob

parser = argparse.ArgumentParser(add_help=True, description='Segment blob objects in input images', formatter_class=RawTextHelpFormatter)
parser.add_argument('--infld', help='input folder', required=True)
parser.add_argument('--outfld', help='output folder', required=True)
parser.add_argument('--blurad', help='gaussian filter blur radius', required=True)
parser.add_argument('--radthr', help='local threshold radius', required=True)
parser.add_argument('--intthr', help='local threshold intensity offset', required=True)
parser.add_argument('--spltnt', help='watershed regional maxima noise tolerance', required=True)
parser.add_argument('--minsize', help='minimum size of output objects', required=True)
args = parser.parse_args()

# Input/Output paths
InputPath = args.infld # "E:/Neubias/Luxembourg/NucleiSegmentation-Python/Test_imgs/in"
OutputPath = args.outfld # "E:/Neubias/Luxembourg/NucleiSegmentation-Python/Test_imgs/out"

# Functional parameters
IntensityBlurRad = float(args.blurad) # 0.0
RadThr = float(args.radthr) # 75
Thr = float(args.intthr)   # -10
DistanceBlurRad = float(args.spltnt) # 3
MinSize = int(args.minsize) # 25

# Loop through all tif files in input folder
Images = (glob.glob(InputPath+"/*.tif"))
for img in Images:

    # Read image
    I = io.imread(img)

    # Processing

    # Gaussian filter
    if IntensityBlurRad >= 1:
        I = 255*gaussian(I, sigma=IntensityBlurRad)

    # Adaptive threshold
    mask = threshold_adaptive(I, RadThr, offset = Thr).astype(np.uint8)

    # Binary watershed
    distance = ndimage.distance_transform_edt(mask)
    distance = gaussian(distance, sigma=DistanceBlurRad)
    local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((3, 3)), labels=mask)
    markers = morphology.label(local_maxi)
    nuclei_labels = watershed(-distance, markers, mask=mask)
    nuclei_labels = nuclei_labels.astype(np.uint16)
    nuclei_labels = remove_small_objects(nuclei_labels, min_size=MinSize)
    nuclei_labels = skimage.segmentation.relabel_sequential(nuclei_labels)[0]
    nuclei_labels = nuclei_labels.astype(np.uint16)

    # Write label mask
    filename = os.path.basename(img)
    io.imsave(OutputPath+"/"+filename, nuclei_labels)
