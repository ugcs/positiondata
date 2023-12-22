import numpy as np
import os
import rasterio
from rasterio.transform import from_origin
from rasterio import warp
from scipy.interpolate import RBFInterpolator
import shutil
import tempfile

xi = np.linspace(0, 10, 5)
yi = np.linspace(10, 20, 5)

xi, yi = np.meshgrid(xi, yi)

print(xi,yi)