import os
import time
import warnings
import numpy as np
import SimpleITK as sitk

# CHECKERBOARD IMAGE GENERATOR
def checkerboardImage(image_1, image_2, gridSize=20):

    # Check for input size of images
    if image_1.shape != image_2.shape:

        # Return a warning and a errors
        # TODO: Test this warning
        raise Warning("Input images do not have the same dimensions")
        return -1

    # Create tiles of 0s and 1s
    tile_0 = np.zeros((gridSize, gridSize), dtype='bool')
    tile_1 = np.ones((gridSize, gridSize), dtype='bool')
    tiles = np.block([[tile_1, tile_0],
                      [tile_0, tile_1]])
    num_blocks_0 = int(np.ceil(image_1.shape[0] / tiles.shape[0]))
    num_blocks_1 = int(np.ceil(image_1.shape[1] / tiles.shape[1]))

    # Create a mask image and crop it to original dimensions
    mask = np.tile(tiles, (num_blocks_0, num_blocks_1))
    mask = mask[0:image_1.shape[0], 0:image_1.shape[1]]

    # Combine both images to one
    return image_1 * mask + image_2 * np.invert(mask)