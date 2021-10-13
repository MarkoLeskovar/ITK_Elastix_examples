import os

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

    elastix_image_filter = sitk.ElastixImageFilter()
    elastix_image_filter.SetFixedImage(fixed_image)
    elastix_image_filter.SetMovingImage(moving_image)
    parameter_map_rigid = sitk.GetDefaultParameterMap('rigid')
    parameter_map_bspline = sitk.GetDefaultParameterMap('bspline')
    elastix_image_filter.SetParameterMap(parameter_map_bspline)
    elastix_image_filter.AddParameterMap(parameter_map_bspline)

    # Other options
    elastix_image_filter.SetOutputDirectory(path_to_output)
    elastix_image_filter.LogToConsoleOff()

    # Run elastix!
    elastix_image_filter.Execute()

    # Get the resulting image and transform parameters
    result_image_elastix = elastix_image_filter.GetResultImage()
    result_transform_parameters = elastix_image_filter.GetTransformParameterMap()



    # TRANSFORMIX - DEFORMATION FIELD CALCULATION
    # Import Image to transform, transformix is transforming from moving -> fixed;
    # for this example the exact same moving image is used, this however is normally not
    # very useful since the elastix algorithm already transformed this image.
    moving_image_transformix = moving_image

    print("Running transformix transformation... ")

    transformix_image_filter = sitk.TransformixImageFilter()
    transformix_image_filter.SetMovingImage(moving_image_transformix)
    transformix_image_filter.SetTransformParameterMap(result_transform_parameters)

    # Calculate Jacobian matrix and it's determinant in a tuple
    transformix_image_filter.ComputeDeformationFieldOn()

    # Other options
    transformix_image_filter.SetOutputDirectory(path_to_output)
    transformix_image_filter.LogToConsoleOff()

    # Run transformix!
    transformix_image_filter.Execute()

    # Get the resulting deformation field
    result_deformation_field = transformix_image_filter.GetDeformationField()




    # DEFORMATION FIELD INVERSION
    '''
    The DisplacementMagnitudePenalty is a cost function that penalises ||Tµ(x) − x||2. You can use this to invert 
    transforms, by setting the transform to be inverted as an initial transform (using -t0), setting 
    (HowToCombineTransforms "Compose"), and running elastix with this metric, using the original fixed image set both as
    fixed (-f) and moving (-m) image. After that you can manually set the initial transform in the last parameter file 
    to "NoInitialTransform", and voila, you have the inverse transform! Strictly speaking, you should then also change 
    the Size/Spacing/Origin/Index/Direction settings to match that of the moving image. Note that inverting a 
    transformation becomes conceptually very similar to performing an image registration in this way. Consequently, the 
    same choices are relevant: optimisation algorithm, multiresolution etc... With Transformix the inverted transform 
    can then be used to calculate the inversion of the deformation field, just like Transformix normally calculates the
    deformation field from a transform.
    '''

    # Get arrays from images
    fixed_image_arr = sitk.GetArrayFromImage(fixed_image)
    moving_image_arr = sitk.GetArrayFromImage(moving_image)
    result_image_arr = sitk.GetArrayFromImage(result_image_elastix)
    result_deformation_arr = sitk.GetArrayFromImage(result_deformation_field)

    # Plot the images
    titles = ["Fixed image",
              "Moving image",
              "Result image (after registration)",
              "Deformation field - X",
              "Deformation field - Y"]
    images = [fixed_image_arr, moving_image_arr, result_image_arr, result_deformation_arr[:, :, 1], result_deformation_arr[:, :, 0]]
    cmaps = ['gray', 'gray', 'gray', 'viridis', 'viridis']

    for i in range(5):
        plt.subplot(2, 3, i + 1)
        plt.imshow(images[i], cmap=cmaps[i], interpolation='none')
        plt.title(titles[i])
        plt.xticks([]), plt.yticks([])
    plt.show()











