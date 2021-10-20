import os
import time
import numpy as np
from matplotlib import pyplot as plt
import SimpleITK as sitk

'''
The process of image registration can be made faster, when smaller version of the fixed and moving images are used for 
calculation of the transformation parameters. These parameters can subsequently be used for the transformation of larger
images. In this example image generators are used to get small and larger versions of hypothetical fixed and moving 
images. An important note is that the width and the height of an image should remain the same. Downsampling of an image
means decreasing the number of pixels by increasing the size (or spacing) of a pixel and thereby remaining the width and
height of the image the same.
'''

# To generate a downsampled smaller image, the spacing of the image should be increased 10-fold in both directions,
# when the number of pixels is decreased 10-fold in both directions.
def image_generator(x1, x2, y1, y2, downsampled=False):
    if downsampled:
        image = np.zeros([100, 100], np.float32)
    else:
        image = np.zeros([1000, 1000], np.float32)
    image[y1:y2, x1:x2] = 1
    image_sikt = sitk.GetImageFromArray(image)
    if downsampled:
        image_sikt.SetSpacing([10,10])
    return image_sikt

# MAIN FUNCTION
if __name__ == "__main__":

    # Create small images for registration
    fixed_image_small = image_generator(25, 75, 25, 75, downsampled=True)
    moving_image_small = image_generator(10, 45, 10, 75, downsampled=True)

    # .. and a big moving image for transformation
    moving_image_large = image_generator(100, 450, 100, 750)

    # # Create a grid image
    # size_x = 1000
    # size_y = 1000
    # gridSize = 23
    #
    # img = np.zeros((int(size_x), int(size_y)), dtype=np.float32)
    # img[::gridSize, :] = 1
    # img[:, ::gridSize] = 1
    #
    # moving_image_large = sitk.GetImageFromArray(img)


    # Elastix registration
    # Load the default parameter map
    elastix_image_filter = sitk.ElastixImageFilter()
    elastix_image_filter.SetFixedImage(fixed_image_small)
    elastix_image_filter.SetMovingImage(moving_image_small)

    parameter_map = sitk.GetDefaultParameterMap("affine")
    elastix_image_filter.SetParameterMap(parameter_map)
    elastix_image_filter.SetParameter('FinalBSplineInterpolationOrder', '0')

    elastix_image_filter.LogToConsoleOff()
    elastix_image_filter.SetOutputDirectory(os.path.join(os.getcwd(),'output'))
    elastix_image_filter.Execute()

    # Get the resulting image and transform parameters
    result_image_elastix = elastix_image_filter.GetResultImage()
    result_transform_parameters = elastix_image_filter.GetTransformParameterMap()



    # Transformix transformation
    transformix_image_filter = sitk.TransformixImageFilter()
    transformix_image_filter.SetMovingImage(moving_image_large)
    transformix_image_filter.SetTransformParameterMap(result_transform_parameters)
    transformix_image_filter.SetTransformParameter(0, "Size", ['1000', '1000'])
    transformix_image_filter.SetTransformParameter(0, "Spacing", ['1', '1'])
    transformix_image_filter.LogToConsoleOff()
    transformix_image_filter.Execute()

    # Get the resulting image and transform parameters
    result_image_transformix = transformix_image_filter.GetResultImage()


    # Get arrays from images
    fixed_image_small_arr = sitk.GetArrayFromImage(fixed_image_small)
    moving_image_small_arr = sitk.GetArrayFromImage(moving_image_small)
    result_image_small_arr = sitk.GetArrayFromImage(result_image_elastix)

    moving_image_large_arr = sitk.GetArrayFromImage(moving_image_large)
    result_image_large_arr = sitk.GetArrayFromImage(result_image_transformix)

    # Plot the images
    titles = ["Fixed image (small)",
              "Moving image (small)",
              "Result image (small)",
              "Moving image (large)",
              "Result image (large)"]

    images = [fixed_image_small_arr, moving_image_small_arr, result_image_small_arr, moving_image_large_arr, result_image_large_arr]

    cmaps = ['gray', 'gray', 'gray', 'gray', 'gray']

    for i in range(5):
        plt.subplot(2, 3, i + 1)
        plt.imshow(images[i], cmap=cmaps[i], interpolation='none')
        plt.title(titles[i])
        # plt.xticks([]), plt.yticks([])
    plt.show()
