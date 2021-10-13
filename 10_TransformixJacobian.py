import os

import SimpleITK
import numpy as np
from matplotlib import pyplot as plt
import SimpleITK as sitk

'''
With the transformix algorithm the spatial jacobian and the determinant of the spatial jacobian of the transformation 
can be calculated. Especially the determinant of the spatial Jacobian, which identifies the amount of local compression
or expansion and can be useful, for example in lung ventilation studies
'''

# MAIN FUNCTION
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


    # ELASTIX
    print("Running elastix registration... ")

    elastix_image_filter = sitk.ElastixImageFilter()
    elastix_image_filter.SetFixedImage(fixed_image)
    elastix_image_filter.SetMovingImage(moving_image)
    parameter_map_bspline = sitk.GetDefaultParameterMap('bspline')
    elastix_image_filter.SetParameterMap(parameter_map_bspline)

    # Other options
    elastix_image_filter.SetOutputDirectory(path_to_output)
    elastix_image_filter.LogToConsoleOff()

    # Run elastix!
    elastix_image_filter.Execute()

    # Get the resulting image and transform parameters
    result_image_elastix = elastix_image_filter.GetResultImage()
    result_transform_parameters = elastix_image_filter.GetTransformParameterMap()


    # TRANSFORMIX - JACOBIAN CALCULATION
    # Import Image to transform, transformix is transforming from moving -> fixed;
    # for this example the exact same moving image is used, this however is normally not
    # very useful since the elastix algorithm already transformed this image.
    moving_image_transformix = moving_image

    print("Running transformix transformation... ")

    transformix_image_filter = sitk.TransformixImageFilter()
    transformix_image_filter.SetMovingImage(moving_image_transformix)
    transformix_image_filter.SetTransformParameterMap(result_transform_parameters)

    # Calculate Jacobian matrix and it's determinant in a tuple
    transformix_image_filter.ComputeSpatialJacobianOn()
    transformix_image_filter.ComputeDeterminantOfSpatialJacobianOn()
    transformix_image_filter.ComputeDeformationFieldOn()

    # Other options
    transformix_image_filter.SetOutputDirectory(path_to_output)
    transformix_image_filter.LogToConsoleOff()

    # Run transformix!
    transformix_image_filter.Execute()

    # Get the resulting deformation field
    result_deformation_field = transformix_image_filter.GetDeformationField()


    # Load spatial jacobian and deformation field from a file
    result_spatial_jacobian = sitk.ReadImage(os.path.join(path_to_output, "fullSpatialJacobian.nii"))
    result_det_spatial_jacobian = sitk.ReadImage(os.path.join(path_to_output, "spatialJacobian.nii"))

    '''
    Inspect the deformation field by looking at the determinant of the Jacobian of Tµ(x). Values smaller than 1 indicate
    local compression, values larger than 1 indicate local expansion, and 1 means volume preservation. The measure is 
    quantitative: a value of 1.1 means a 10% increase in volume. If this value deviates substantially from 1, you may be
    worried (but maybe not if this is what you expect for your application). In case it is negative you have “foldings” 
    in your transformation, and you definitely should be worried.
    '''

    # Get arrays from images
    fixed_image_arr = sitk.GetArrayFromImage(fixed_image)
    moving_image_arr = sitk.GetArrayFromImage(moving_image)
    result_image_arr = sitk.GetArrayFromImage(result_image_elastix)

    # Casting tuple to two numpy matrices for further calculations.
    spatial_jacobian = sitk.GetArrayFromImage(result_spatial_jacobian)
    det_spatial_jacobian = sitk.GetArrayFromImage(result_det_spatial_jacobian)

    print("Number of foldings in transformation:", np.sum(det_spatial_jacobian < 0))

    # Plot the images
    titles = ["Fixed image",
              "Moving image",
              "Result image (after registration)",
              "Determinant of spatial jacobian (transformix output)"]
    images = [fixed_image_arr, moving_image_arr, result_image_arr, det_spatial_jacobian]
    cmaps = ['gray', 'gray', 'gray', 'viridis']

    for i in range(4):
        plt.subplot(2, 2, i + 1)
        plt.imshow(images[i], cmap=cmaps[i], interpolation='none')
        plt.title(titles[i])
        plt.xticks([]), plt.yticks([])
    plt.show()











