import os
from matplotlib import pyplot as plt
import SimpleITK as sitk
import custom_functions as cf

'''
In this notebook other options of the elastix algorithm are shown: initial transformation and multithreading. They're 
shown together just to reduce the number of example notebooks and thus can be used independently as well as in 
combination with whichever other functionality of the elastix algorithm. Initial transforms are transformations that are
done on the moving image before the registration is started. Multithreading spreaks for itself and can be used in 
similar fashion in the transformix algorithm.
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

    # Initial transform parameter file
    initial_parameter_file = os.path.join(path_to_input, 'TransformParameters.1.txt')

    # Load path to images, output and parameter file
    fixed_image = sitk.ReadImage(os.path.join(path_to_input, fixed_image_name))
    moving_image = sitk.ReadImage(os.path.join(path_to_input, moving_image_name))


    # Run the registration if the output file does not yet exist
    if not os.path.exists(os.path.join(path_to_output, result_image_name)):
        print("Running elastix registration... ")

        # Load the default parameter map
        elastix_image_filter = sitk.ElastixImageFilter()
        elastix_image_filter.SetFixedImage(fixed_image)
        elastix_image_filter.SetMovingImage(moving_image)
        elastix_image_filter.SetOutputDirectory(path_to_output)
        elastix_image_filter.SetParameterMap(sitk.GetDefaultParameterMap('rigid'))
        elastix_image_filter.AddParameterMap(sitk.GetDefaultParameterMap('rigid'))
        elastix_image_filter.LogToConsoleOn()
        elastix_image_filter.SetInitialTransformParameterFileName(initial_parameter_file)
        elastix_image_filter.SetNumberOfThreads(4)
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
    checkerboard_image = cf.checkerboardImage(fixed_image_arr, result_image_arr, gridSize=30)

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




