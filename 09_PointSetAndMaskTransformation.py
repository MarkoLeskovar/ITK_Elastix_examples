import os
import numpy as np
import SimpleITK as sitk

'''
Transformix can be used to transform point sets and mask images as well. Masks can be seen as images so the registration
of masks is done in similar fashion as the registration of a moving image. When transforming an image or mask (defined 
in the moving image domain), it is transformed to the fixed image domain. This is useful for example when one needs to
deform a segmentation from the moving image to the fixed image, to obtain an estimate of a segmentation in the fixed 
image. When transforming a point set, this happens the other way around: from the fixed image domain to the moving image
domain. This is useful for example when you want to know where a point maps to. Point sets therefore need not be 
transformed with the backwards mapping protocol, but can instead be transformed with regular forward transformation 
(fixed -> moving). Transforming point sets can be used to get the regions of interest (ROI) in the moving image, based
on ROI of the fixed image.
'''

# In case of boolaen segmentation, the dice loss is equal to 2 x dot product of the flattened arrays divided by the
# total volume of both masks.
def dice_loss(y_true, y_pred):
    y_true = y_true.flatten()
    y_pred = y_pred.flatten()
    intersection = y_true.dot(y_pred)
    union = sum(y_true) + sum(y_pred)
    dice = 2 * intersection / union
    return dice

# MAIN FUNCTION
if __name__ == "__main__":

    # Get the path to working directory, input and output
    path_to_working_directory = os.getcwd()
    path_to_input = os.path.join(path_to_working_directory, 'data')
    path_to_output = os.path.join(path_to_working_directory, 'output')

    # Image names
    fixed_image_name = "CT_3D_lung_fixed.mha"
    moving_image_name = "CT_3D_lung_moving.mha"
    result_image_name = "result_image.mha"

    moving_mask_name = "CT_3D_lung_moving_mask.mha"
    fixed_mask_name = "CT_3D_lung_fixed_mask.mha"

    # Load path to images, output and parameter file
    fixed_image = sitk.ReadImage(os.path.join(path_to_input, fixed_image_name))
    moving_image = sitk.ReadImage(os.path.join(path_to_input, moving_image_name))

    fixed_mask = sitk.ReadImage(os.path.join(path_to_input, fixed_mask_name))
    moving_mask = sitk.ReadImage(os.path.join(path_to_input, moving_mask_name))


    # RUN ELASTIX
    print("Running elastix registration... ")

    elastix_image_filter = sitk.ElastixImageFilter()
    elastix_image_filter.SetFixedImage(fixed_image)
    elastix_image_filter.SetMovingImage(moving_image)

    parameter_map_rigid = sitk.GetDefaultParameterMap('rigid')
    parameter_map_affine = sitk.GetDefaultParameterMap('affine')
    parameter_map_bspline = sitk.GetDefaultParameterMap('bspline')

    elastix_image_filter.SetParameterMap(parameter_map_rigid)
    elastix_image_filter.AddParameterMap(parameter_map_affine)
    elastix_image_filter.AddParameterMap(parameter_map_bspline)

    # Other options
    elastix_image_filter.SetOutputDirectory(path_to_output)
    elastix_image_filter.LogToConsoleOff()

    # Run elastix!
    elastix_image_filter.Execute()


    # Get the resulting image and transform parameters
    result_image_elastix = elastix_image_filter.GetResultImage()
    result_transform_parameters = elastix_image_filter.GetTransformParameterMap()


    # RUN TRANSFORMIX
    print("Running transformix transformation... ")

    transformix_image_filter = sitk.TransformixImageFilter()
    transformix_image_filter.SetMovingImage(moving_mask)
    transformix_image_filter.SetTransformParameterMap(result_transform_parameters)
    transformix_image_filter.SetTransformParameter('FinalBSplineInterpolationOrder', '0')

    # Other options
    transformix_image_filter.SetOutputDirectory(path_to_output)
    transformix_image_filter.LogToConsoleOff()

    # Run transformix!
    transformix_image_filter.Execute()

    # Get the resulting image and transform parameters
    result_image_transformix = transformix_image_filter.GetResultImage()


    # SEGMENTATION TRANSFORMATION EVALUATION
    '''
    The result of a segmentation transformation can be evaluated by means of, for example, the dice loss. The dice loss
    is the proportion of the 2 segmentations that overlap. In the example above the masks used were segmentations of the
    images. This is of course not always the case, masks could also hide the artifacts, in which case they're not 
    (only) image segmentations. The dice loss of the segmentation transformation can therefore be calculated with the 
    dice loss of the 2 masks.
    '''

    # Cast itk images to numpy arrays and round result image to boolean array.
    fixed_mask_np = np.asarray(fixed_mask)
    result_mask_np = np.asarray(result_image_transformix).round().astype(int)

    print("Dice loss:", dice_loss(fixed_mask_np, result_mask_np))


    # POINT SET TRANSFORMATION
    # Procedural interface of transformix filter
    print("Running transformix transformation for a point set... ")
    transformix_image_filter = sitk.TransformixImageFilter()
    transformix_image_filter.SetMovingImage(moving_mask)
    transformix_image_filter.SetTransformParameterMap(result_transform_parameters)
    transformix_image_filter.SetFixedPointSetFileName(os.path.join(path_to_input, 'CT_3D_lung_fixed_point_set_corrected.txt'))

    # Other options
    transformix_image_filter.SetOutputDirectory(path_to_output)
    transformix_image_filter.LogToConsoleOff()

    # Run transformix!
    transformix_image_filter.Execute()




