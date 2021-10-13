import os
import SimpleITK as sitk

'''
Often, some content in the images may not correspond. For example, there may be background content or noisy areas. 
A mask defined on the fixed and/or moving image can be used to exclude these regions at a pixel level from the 
similarity metric computations. This improves the robustness of registration. A mask is a binary image with 1 meaning 
that a pixel is include in elastix' computation and a 0 meaning it's not.
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
    fixed_mask_name = "CT_3D_lung_fixed_mask.mha"
    moving_mask_name = "CT_3D_lung_moving_mask.mha"

    # Load images and masks
    fixed_image = sitk.ReadImage(os.path.join(path_to_input, fixed_image_name))
    moving_image = sitk.ReadImage(os.path.join(path_to_input, moving_image_name))
    fixed_mask = sitk.ReadImage(os.path.join(path_to_input, fixed_mask_name))
    moving_mask = sitk.ReadImage(os.path.join(path_to_input, moving_mask_name))


    # Or Optionally Create Masks from scratch - NOT WORKING YET
    # MaskImageType = sitk.Image[sitk.UC, 2]
    # fixed_mask = sitk.BinaryThresholdImageFilter(fixed_image,
    #                                              lower_threshold=80.0,
    #                                              inside_value=1,
    #                                              ttype=(type(fixed_image), MaskImageType))
    # moving_mask = sitk.BinaryThresholdImageFilter(moving_image,
    #                                               lower_threshold=80.0,
    #                                               inside_value=1,
    #                                               ttype=(type(moving_image), MaskImageType))

    # Run the registration if the output file does not yet exist
    if not os.path.exists(os.path.join(path_to_output, result_image_name)):
        print("Running elastix registration... ")

        # Import Custom Parameter Map
        # Load the default parameter map
        elastix_image_filter = sitk.ElastixImageFilter()
        elastix_image_filter.SetFixedImage(fixed_image)
        elastix_image_filter.SetMovingImage(moving_image)
        elastix_image_filter.SetFixedMask(fixed_mask)
        elastix_image_filter.SetMovingMask(moving_mask)
        elastix_image_filter.SetOutputDirectory(path_to_output)
        elastix_image_filter.LogToConsoleOff()
        elastix_image_filter.LogToFileOn()
        elastix_image_filter.SetParameterMap(
        sitk.ReadParameterFile(os.path.join(path_to_input, 'parameters.3D.NC.affine.ASGD.001.txt')))

        elastix_image_filter.Execute()

        # # Call registration function
        # result_image, result_transform_parameters = itk.elastix_registration_method(
        #     fixed_image, moving_image,
        #     parameter_object=parameter_object,
        #     fixed_mask=fixed_mask, moving_mask=moving_mask,
        #     log_to_console=False)

        # Save image with itk
        result_image = elastix_image_filter.GetResultImage()
        sitk.WriteImage(result_image, os.path.join(path_to_output, result_image_name))

    else:
        print("Output file already exists...")

        result_image = sitk.ReadImage(os.path.join(path_to_output, result_image_name))


