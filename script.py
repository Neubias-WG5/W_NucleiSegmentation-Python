# Author: Sébastien Tosi (IRB Barcelona)
# Version: 1.1
# Date: 04/02/2019

import os
import numpy as np
from skimage import io
from skimage import morphology
from skimage import img_as_uint
from skimage.filters import gaussian, threshold_adaptive
from skimage.feature import peak_local_max
from skimage.morphology import watershed
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
args = parser.parse_args()

# Input/Output paths
InputPath = args.infld # "E:/Neubias/Luxembourg/NucleiSegmentation-Python/Test_imgs/in"
OutputPath = args.outfld # "E:/Neubias/Luxembourg/NucleiSegmentation-Python/Test_imgs/out"

# Functional parameters
IntensityBlurRad = float(args.blurad) # 1.5
RadThr = float(args.radthr) # 75
Thr = float(args.intthr)   # -10
DistanceBlurRad = float(args.spltnt) # 3

# Loop through all tif files in input folder
Images = (glob.glob(InputPath+"/*.tif"))
for img in Images:

    # Read image
    I = io.imread(img)

    # Processing

    # Gaussian filter
    If = 255*gaussian(I, sigma=IntensityBlurRad)

    # Adaptive threshold
    mask = threshold_adaptive(If, RadThr, offset = Thr).astype(np.uint8)

    # Binary watershed
    distance = ndimage.distance_transform_edt(mask)
    distance = gaussian(distance, sigma=DistanceBlurRad)
    local_maxi = peak_local_max(distance, indices=False, footprint=np.ones((3, 3)), labels=mask)
    markers = morphology.label(local_maxi)
    nuclei_labels = watershed(-distance, markers, mask=mask)
    nuclei_labels = img_as_uint(nuclei_labels)

    # Write label mask
    filename = os.path.basename(img)
    io.imsave(OutputPath+"/"+filename, nuclei_labels)