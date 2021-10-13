import os
import numpy as np
import SimpleITK as sitk

'''
Point-based registration allows us to help the registration via pre-defined sets of corresponding points. The 
'CorrespondingPointsEuclideanDistanceMetric' minimises the distance of between a points on the fixed image and 
corresponding points on the moving image. The metric can be used to help in a difficult registration task by taking 
into account positions are known to correspond. Think of it as a way of embedding expert knowledge in the registration 
procedure. We can manually or automatically select points via centroids of segmentations for example. Anything is 
possible. Point sets should always be given to elastix with their corresponding image.

In order for 3D registration to work with a point set, the 'CorrespondingPointsEuclideanDistanceMetric', should be set 
as metric. For the 3D case, this means that the metric should be a multimetric with the first metric of type 
AdvancedImageToImageMetric and the second the 'CorrespondingPointsEuclideanDistanceMetric'. The Registration parameter 
should therefore be set to 'MultiMetricMultiResolutionRegistration', to allow a multimetric parameter.
'''

if __name__ == "__main__":

    # Get the path to working directory, input and output
    path_to_working_directory = os.getcwd()
    path_to_input = os.path.join(path_to_working_directory, 'data')
    path_to_output = os.path.join(path_to_working_directory, 'output')

    # Image names
    fixed_image_name = "CT_3D_lung_fixed.mha"
    moving_image_name = "CT_3D_lung_moving.mha"
    result_image_name = "result_image.mha"

    # Point set names
    fixed_point_set_name = 'CT_3D_lung_fixed_point_set_corrected.txt'
    moving_point_set_name = 'CT_3D_lung_moving_point_set_corrected.txt'

    # Load path to images, output and parameter file
    fixed_image = sitk.ReadImage(os.path.join(path_to_input, fixed_image_name))
    moving_image = sitk.ReadImage(os.path.join(path_to_input, moving_image_name))

    # Load point sets
    fixed_point_set = np.loadtxt(os.path.join(path_to_input, fixed_point_set_name), skiprows=2, delimiter=' ')
    moving_point_set = np.loadtxt(os.path.join(path_to_input, moving_point_set_name), skiprows=2, delimiter=' ')

    # Run the registration if the output file does not yet exist
    if not os.path.exists(os.path.join(path_to_output, result_image_name)):
        print("Running elastix registration... ")

        # Load the default parameter map
        parameter_map_rigid = sitk.GetDefaultParameterMap('rigid')
        parameter_map_rigid['Registration'] = ['MultiMetricMultiResolutionRegistration']
        original_metric = parameter_map_rigid['Metric']

        # The "CorrespondingPointsEuclideanDistanceMetric" metric must be specified as the last metric due to
        # technical constraints in elastix.
        parameter_map_rigid['Metric'] = [original_metric[0], 'CorrespondingPointsEuclideanDistanceMetric']

        # Elastix registration
        elastix_image_filter = sitk.ElastixImageFilter()
        elastix_image_filter.SetFixedImage(fixed_image)
        elastix_image_filter.SetMovingImage(moving_image)
        elastix_image_filter.SetOutputDirectory(path_to_output)
        elastix_image_filter.SetParameterMap(parameter_map_rigid)
        elastix_image_filter.SetFixedPointSetFileName(os.path.join(path_to_input, fixed_point_set_name))
        elastix_image_filter.SetMovingPointSetFileName(os.path.join(path_to_input, moving_point_set_name))
        elastix_image_filter.Execute()

        # Save image with sitk
        result_image = elastix_image_filter.GetResultImage()
        sitk.WriteImage(result_image, os.path.join(path_to_output, result_image_name))

    else:
        print("Output file already exists...")

        result_image = sitk.ReadImage(os.path.join(path_to_output, result_image_name))





