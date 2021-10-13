import os
import SimpleITK as sitk

'''
Groupwise registration methods try to mitigate uncertainties associated with any one image by simultaneously registering
all images in a population. This incorporates all image information in registration process and eliminates bias towards 
a chosen reference frame. The method described here uses a 3D (2D+time) free-form B-spline deformation model and a 
similarity metric that minimizes variance of intensities under the constraint that the average deformation over images 
is zero. This constraint defines a true mean frame of reference that lie in the center of the population without having 
to calculate it explicitly.

The method can take into account temporal smoothness of the deformations and a cyclic transform in the time dimension.
This may be appropriate if it is known a priori that the anatomical motion has a cyclic nature e.g. in cases of cardiac 
or respiratory motion.
'''

if __name__ == "__main__":

    # Get the path to working directory, input and output
    path_to_working_directory = os.getcwd()
    path_to_input = os.path.join(path_to_working_directory, 'data')
    path_to_output = os.path.join(path_to_working_directory, 'output')

    # Folder containing the image
    folder_image_name = "00"
    result_image_name = "result_image.mha"

    # Load all the images in the folder, convert them to 2D and add them to a list
    images = os.listdir(os.path.join(path_to_input, folder_image_name))
    images.sort()
    vectorOfImages = sitk.VectorOfImage()
    for image in images:

        temp_image = sitk.ReadImage(os.path.join(path_to_input, folder_image_name, image))
        temp_image = sitk.Extract(temp_image, (temp_image.GetWidth(), temp_image.GetHeight(), 0), (0, 0, 0))
        vectorOfImages.push_back(temp_image)

    # Change the origin of the images to avoid errors
    image_origin = vectorOfImages[0].GetOrigin()
    for n in range(vectorOfImages.size()):
        vectorOfImages[n].SetOrigin(image_origin)




    # Join all images
    images = sitk.JoinSeries(vectorOfImages)

    # Run the registration if the output file does not yet exist
    if not os.path.exists(os.path.join(path_to_output, result_image_name)):
        print("Running elastix registration... ")

        # Call registration function
        elastix_image_filter = sitk.ElastixImageFilter()
        elastix_image_filter.SetFixedImage(images)
        elastix_image_filter.SetMovingImage(images)
        elastix_image_filter.SetParameterMap(sitk.GetDefaultParameterMap('groupwise'))
        elastix_image_filter.SetParameter("Transform", "EulerStackTransform")
        elastix_image_filter.SetOutputDirectory(path_to_output)
        elastix_image_filter.LogToConsoleOff()
        elastix_image_filter.Execute()

        # Save image with itk
        result_image = elastix_image_filter.GetResultImage()
        sitk.WriteImage(result_image, os.path.join(path_to_output, result_image_name))

    else:
        print("Output file already exists...")

        result_image = sitk.ReadImage(os.path.join(path_to_output, result_image_name))