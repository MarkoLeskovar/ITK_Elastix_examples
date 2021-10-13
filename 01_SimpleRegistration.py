import os
from matplotlib import pyplot as plt
import SimpleITK as sitk
import custom_functions as cf

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

    # Load the images
    fixed_image = sitk.ReadImage(os.path.join(path_to_input, fixed_image_name), sitk.sitkFloat32)
    moving_image = sitk.ReadImage(os.path.join(path_to_input, moving_image_name), sitk.sitkFloat32)

    # Run the registration if the output file does not yet exist
    if not os.path.exists(os.path.join(path_to_output, result_image_name)):
        print("Running elastix registration... ")

        # Initialize the elastix registration
        elastix_image_filter = sitk.ElastixImageFilter()
        elastix_image_filter.SetFixedImage(fixed_image)
        elastix_image_filter.SetMovingImage(moving_image)

        # Load the default parameter map
        parameter_map = sitk.GetDefaultParameterMap("bspline")
        elastix_image_filter.SetParameterMap(parameter_map)

        # Other settings
        elastix_image_filter.SetOutputDirectory(path_to_output)
        elastix_image_filter.LogToConsoleOff()

        # Run Elastix!
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
    titles = ["Fixed image", "Moving image", "Result image", "Fixed and Moving image overlay",
              "Difference between Fixed and Moving image", "Difference between Fixed and Result image"]
    images = [fixed_image_arr, moving_image_arr, result_image_arr, checkerboard_image, difference_1, difference_2]
    cmaps = ['gray', 'gray', 'gray', 'gray', 'viridis', 'viridis']

    for i in range(6):
        plt.subplot(2, 3, i + 1)
        plt.imshow(images[i], cmap=cmaps[i], interpolation='none')
        plt.title(titles[i])
        plt.xticks([]), plt.yticks([])
    plt.show()



