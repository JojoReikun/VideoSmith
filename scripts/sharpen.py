import cv2
import numpy as np

# Adding salt & pepper noise to an image
def salt_pepper(prob, image):
      # Extract image dimensions
      row, col = image.shape

      # Declare salt & pepper noise ratio
      s_vs_p = 0.5
      output = np.copy(image)

      # Apply salt noise on each pixel individually
      num_salt = np.ceil(prob * image.size * s_vs_p)
      coords = [np.random.randint(0, i - 1, int(num_salt))
            for i in image.shape]
      output[coords] = 1

      # Apply pepper noise on each pixel individually
      num_pepper = np.ceil(prob * image.size * (1. - s_vs_p))
      coords = [np.random.randint(0, i - 1, int(num_pepper))
            for i in image.shape]
      output[coords] = 0

      return output


def sharpen(current_preview):
    image = current_preview

    # add salt and pepper noise
    # Call salt & pepper function with probability = 0.5
    #image_sp = salt_pepper(0.5, image)

    print("sharpening")

    # Create our sharpening kernel, the sum of all values must equal to one for uniformity
    kernel_sharpening = np.array([[-1, -1, -1],
                                  [-1, 9, -1],
                                  [-1, -1, -1]])

    sharpened_image = cv2.filter2D(image, -1, kernel_sharpening)

    return sharpened_image
