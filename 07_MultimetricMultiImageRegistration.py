import os
import time
import numpy as np
from matplotlib import pyplot as plt
import  SimpleITK as sitk
import  custom_functions as cf

'''
Image registration finds the spatial transformation that aligns images in the presence of noise. In image registration,
we typically identify the two images as the fixed and moving image. Our goal is to find the spatial transformation that 
makes the moving image align with the fixed image. First, let's load our fixed image and the image we will align to our
fixed image, the moving image.
'''

if __name__ == "__main__":

    # Get the path to working directory, input and output
    path_to_working_directory = os.getcwd()
    path_to_input = os.path.join(path_to_working_directory, 'data')
    path_to_output = os.path.join(path_to_working_directory, 'output')

    # Image names
    fixed_image_name = "CT_2D_head_fixed.mha"
    moving_image_name = "CT_2D_head_moving.mha"
    result_image_name = "result_image.mha"

    # Load path to images, output and parameter file
    fixed_image = sitk.ReadImage(os.path.join(path_to_input, fixed_image_name))
    moving_image = sitk.ReadImage(os.path.join(path_to_input, moving_image_name))


    # Run the registration if the output file does not yet exist
    if not os.path.exists(os.path.join(path_to_output, result_image_name)):
        print("Running elastix registration... ")

        # Import Multimetric Parameter Map (see elastix documentation,
        # KNNGraphAlphaMutualInformation is not supported yet by ITKElastix)
        elastix_image_filter = sitk.ElastixImageFilter()
        elastix_image_filter.SetFixedImage(fixed_image)
        elastix_image_filter.SetMovingImage(moving_image)
        parameter_map = sitk.ReadParameterFile(os.path.join(path_to_input, 'parameters_Bspline_Multimetric.txt'))
        elastix_image_filter.SetParameterMap(parameter_map)
        elastix_image_filter.SetOutputDirectory(path_to_output)
        elastix_image_filter.LogToConsoleOff()
        elastix_image_filter.Execute()

        # Save image with itk
        result_image = elastix_image_filter.GetResultImage()
        sitk.WriteImage(result_image, os.path.join(path_to_output, result_image_name))

    else:
        print("Output file already exists...")

        result_image = sitk.ReadImage(os.path.join(path_to_output, result_image_name))

    # Get arrays from images
    fixed_image_arr = sitk.GetArrayFromImage(fixed_image)
    moving_image_arr = sitk.GetArrayFromImage(moving_image)
    result_image_arr = sitk.GetArrayFromImage(result_image)

    # Create images for inspection
    difference_1 = fixed_image_arr - moving_image_arr
    difference_2 = fixed_image_arr - result_image_arr
    checkerboard_image = cf.checkerboardImage(fixed_image_arr, result_image_arr, gridSize=50)

    # Plot the images
    titles = ["Fixed image", "Moving image", "Result image", "Fixed and Moving overlay", "Fixed minus Moving",
              "Fixed minus Result"]
    images = [fixed_image_arr, moving_image_arr, result_image_arr, checkerboard_image, difference_1, difference_2]
    cmaps = ['gray', 'gray', 'gray', 'gray', 'viridis', 'viridis']

    for i in range(6):
        plt.subplot(2, 3, i + 1)
        plt.imshow(images[i], cmap=cmaps[i], interpolation='none')
        plt.title(titles[i])
        plt.xticks([]), plt.yticks([])
    plt.show()



    # # MULTI_SPECTRAL IMAGE REGISTRATION
    # # Images of actual different spectra should be used here, for now same images are used.
    # fixed_image_spectrum1 = itk.imread('data/CT_2D_head_fixed.mha', itk.F)
    # moving_image_spectrum1 = itk.imread('data/CT_2D_head_moving.mha', itk.F)
    # fixed_image_spectrum2 = itk.imread('data/CT_2D_head_fixed.mha', itk.F)
    # moving_image_spectrum2 = itk.imread('data/CT_2D_head_moving.mha', itk.F)
    #
    # # Import Parameter Map
    # parameter_object = itk.ParameterObject.New()
    # parameter_object.AddParameterFile('data/parameters_BSpline.txt')
    #
    # # Load Elastix Image Filter Object
    # elastix_object = itk.ElastixRegistrationMethod.New(fixed_image_spectrum1, moving_image_spectrum1)
    # # elastix_object.SetFixedImage(fixed_image_spectrum1)
    # elastix_object.AddFixedImage(fixed_image_spectrum2)
    #
    # # elastix_object.SetMovingImage(moving_image_spectrum1)
    # elastix_object.AddMovingImage(moving_image_spectrum2)
    # elastix_object.SetParameterObject(parameter_object)
    #
    # # Set additional options
    # elastix_object.SetLogToConsole(False)
    #
    # # Update filter object (required)
    # elastix_object.UpdateLargestPossibleRegion()
    #
    # # Results of Registration
    # result_image = elastix_object.GetOutput()
    # result_transform_parameters = elastix_object.GetTransformParameterObject()
