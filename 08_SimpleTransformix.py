import os
import numpy as np
from matplotlib import pyplot as plt
import SimpleITK as sitk

'''
After image registrations it is often useful to apply the transformation as found by the registration to another image. 
Maybe you want to apply the transformation to an original (larger) image to gain resolution. Or maybe you need the 
transformation to apply it to a label image (segmentation). Transformix is an image filter that was developed together 
with elastix, that can be used to do these transformations.

A spatial transformation is defined as a mapping from the fixed image domain to the moving image domain. More information
on the precise definition of the transform can be found in the elastix manual. Transformix can be used to apply this 
mapping not only to images, but also to masks (binary images) and point sets see example 09.

The transform parameters that elastix outputs can be given to transformix as input for the transformations. The output 
transform parameters from elastix are mappings from the fixed image to the moving image domain. Transformix therefore 
uses a backwards mapping to obtain a registered version of the moving image (moving -> fixed domain).
'''

if __name__ == "__main__":

    # Get the path to working directory, input and output
    path_to_working_directory = os.getcwd()
    path_to_input = os.path.join(path_to_working_directory, 'data')
    path_to_output = os.path.join(path_to_working_directory, 'output')

    # Image names
    fixed_image_name = "CT_2D_head_fixed.mha"
    moving_image_name = "CT_2D_head_moving.mha"

    # Output
    result_image_name = "result_image.mha"
    result_transform_parameters_name = "result_transform_parameters.txt"

    # Load path to images, output and parameter file
    fixed_image = sitk.ReadImage(os.path.join(path_to_input, fixed_image_name))
    moving_image = sitk.ReadImage(os.path.join(path_to_input, moving_image_name))


    # Run the registration if the output file does not yet exist
    print("Running elastix registration... ")

    # Load the default parameter map
    elastix_image_filter = sitk.ElastixImageFilter()
    elastix_image_filter.SetFixedImage(fixed_image)
    elastix_image_filter.SetMovingImage(moving_image)
    parameter_map = sitk.GetDefaultParameterMap("bspline")
    elastix_image_filter.SetParameterMap(parameter_map)

    # Other options
    elastix_image_filter.SetOutputDirectory(path_to_output)
    elastix_image_filter.LogToConsoleOff()

    # Run elastix!
    elastix_image_filter.Execute()

    # Get the resulting image and transform parameters
    result_image = elastix_image_filter.GetResultImage()
    result_transform_parameters = elastix_image_filter.GetTransformParameterMap()

    # Import Image to transform - In this example the same moving image is used, that was used for elastix, this however
    # will result in the same image as was already given by the first elastix registration.
    moving_image_transformix = moving_image

    # Call transformix function
    transformix_image_filter = sitk.TransformixImageFilter()
    transformix_image_filter.SetMovingImage(moving_image_transformix)
    transformix_image_filter.SetTransformParameterMap(result_transform_parameters)

    # Other options
    transformix_image_filter.SetOutputDirectory(path_to_output)
    transformix_image_filter.LogToConsoleOff()

    # Run transformix!
    transformix_image_filter.Execute()

    # Get the resulting imagefrom transformix
    result_image_transformix = transformix_image_filter.GetResultImage()

    # Get arrays from images
    fixed_image_arr = sitk.GetArrayFromImage(fixed_image)
    moving_image_arr = sitk.GetArrayFromImage(moving_image)
    result_image_arr = sitk.GetArrayFromImage(result_image)

    moving_image_tr_arr = sitk.GetArrayFromImage(moving_image_transformix)
    result_image_tr_arr = sitk.GetArrayFromImage(result_image_transformix)

    difference_1 = result_image_arr - result_image_tr_arr



    # Plot the images
    titles = ["Fixed image",
              "Moving image",
              "Result image (after registration)",
              "Moving image (transformix input)",
              "Result image (transformix output)",
              "Diference between both results"]

    images = [fixed_image_arr, moving_image_arr, result_image_arr, moving_image_tr_arr, result_image_tr_arr, difference_1]
    cmaps = ['gray', 'gray', 'gray', 'gray', 'gray', 'gray']

    for i in range(6):
        plt.subplot(2, 3, i + 1)
        plt.imshow(images[i], cmap=cmaps[i], interpolation='none')
        plt.title(titles[i])
        plt.xticks([]), plt.yticks([])
    plt.show()



