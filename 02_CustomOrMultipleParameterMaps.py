import os
import SimpleITK as sitk

'''
We can run the registration with multiple stages, using the spatial transformation result from the current stage to 
initialize registration at the next stage. Typically, we start with a simple spatial transformation and advance to a 
more complex spatial transformation. The default, conservative, registration parameters progress from a 
translation -> affine -> bspline transformation, with 4 resolutions for each transformation type.

When multiple resolutions are used, a multi-scale image pyramid is generated with downscaled versions of the image.
Registration results at a lower resolution is used to initialize registration at a higher resolution. This improves 
speed and robustness. The number of resolutions can be manually specified as well.

A default set of registration parameters are available for:

    translation
    rigid
    affine
    bspline
    spline
    groupwise

transformations. More information on these transformation and on all possible parameter settings can be found in the 
elastix manual
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

    # Load the images
    fixed_image = sitk.ReadImage(os.path.join(path_to_input, fixed_image_name))
    moving_image = sitk.ReadImage(os.path.join(path_to_input, moving_image_name))

    # Initialize the elastix registration
    elastix_image_filter = sitk.ElastixImageFilter()
    elastix_image_filter.SetFixedImage(fixed_image)
    elastix_image_filter.SetMovingImage(moving_image)

    '''
    ElastixImageFilter will register our images with a translation -> affine -> b-spline multi-resolution approach by 
    default. We simply leave out the call to SetParameterMap to achieve this functionality.
    '''

    # Add the default rigid parameter map
    resolutions = 3
    parameter_map_rigid = sitk.GetDefaultParameterMap("rigid", resolutions)

    # First call is a "SetParameterMap" method. This deletes any previously set parameter maps. Subsequent calls to
    # "AddParameterMap" appends parameter maps to the internal list of parameter maps
    elastix_image_filter.SetParameterMap(parameter_map_rigid)

    # Print the parameter map
    # sitk.PrintParameterMap(elastix_image_filter.GetParameterMap())

    # Add the default b-spline parameter map
    # Extra argument can be specified that define the final bspline grid spacing in physical space.
    parameter_map_bspline = sitk.GetDefaultParameterMap("bspline", resolutions, 20.0)
    elastix_image_filter.AddParameterMap(parameter_map_bspline)

    # Load custom parameter maps from .txt file
    parameter_map_file = sitk.ReadParameterFile(os.path.join(path_to_input, 'parameters_BSpline.txt'))
    elastix_image_filter.AddParameterMap(parameter_map_file)

    # Load and customize the default parameter map
    parameter_map_custom = sitk.GetDefaultParameterMap('rigid')
    parameter_map_custom['Transform'] = ['BSplineTransform']
    parameter_map_custom['Metric'] = ['AdvancedMattesMutualInformation']
    elastix_image_filter.AddParameterMap(parameter_map_custom)

    # Customize the parameter maps afterwards
    # here the 'NumberOfResolutions' parameter of the 2nd parameter map of the parameter_object is set to 1.
    elastix_image_filter.SetParameter(2, "NumberOfResolutions", "1")

    # Set the 'DefaultPixelValue' of all parameter maps in the parameter_object to 0
    elastix_image_filter.SetParameter("DefaultPixelValue", "0")

    # Remove a parameter
    elastix_image_filter.RemoveParameter("ResultImageFormat")

    # Save a custom parameter map
    elastix_image_filter.WriteParameterFile(parameter_map_custom, os.path.join(path_to_output, 'parameters_custom.txt'))

    # Or serialize each parameter map to a file.
    for index in range(elastix_image_filter.GetNumberOfParameterMaps()):
        parameter_map = elastix_image_filter.GetParameterMap()[index]
        elastix_image_filter.WriteParameterFile(parameter_map, os.path.join(path_to_output, "Parameters.{0}.txt".format(index)))







