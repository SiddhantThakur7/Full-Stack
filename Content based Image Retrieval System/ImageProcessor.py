import os
import numpy as np
import cv2
import multiprocessing as mp
import json

# Number of CPU cores available for multi-processing
N = mp.cpu_count()


def binary_of(x, bits=8):
    """Converts decimal to sepcified bits binary.

    Args:
        x: integer
        bits (int, optional): Number of bits required in the binary equivalent. Defaults to 8.

    Returns:
        str: binay representation of the decimal number.
    """
    return format(x, f"0{bits}b")


def int_of(x):
    """Converts binary to decimal bits binary.

    Args:
        x: string form binary representation.

    Returns:
        int: decimal conversion of a binary string.
    """
    return int(x, 2)


CACHE_PATH = ".\\cache\\representations.json"
COLOR_CODE = "color_code"
INTENSITY = "intensity"
COMBINED = "combined"
METHOD_MAP = {"Color": COLOR_CODE, "Intensity": INTENSITY, "Color + Intensity": COMBINED}
DEFAULT_WEIGHT = 1/89

class ImageProcessor:
    def __init__(self) -> None:
        # Dictionary containing image representations, histograms and general data
        self.images = {}

        # BGR coefficients for intensity representation calculation
        self.INTENSITY_COEFFICIENT_MATRIX = np.array([[0.114], [0.587], [0.299]])

        # Default image order
        self.default_image_list = []

        self.weights = []

        self.initialize()

    def initialize(self):
        """ Verifies the presence of cache data and generates data in its absence"""
        cache_data = self.load_cache_data()
        if cache_data:
            self.images = cache_data
            self.weights = np.repeat(1/89, 89)
        else:
            # Process pool spanning across all the available CPU cores 
            with mp.Pool(processes=N) as p:
                # Aggregate mutlti-processing results
                results = p.map(self.intialize_image_data, [x for x in range(1, 101)])
            # results = []
            # for i in range(1, 101):
            #     results.append(self.intialize_image_data(i))
            for idx, val in enumerate(results):
                self.images[idx + 1] = val[idx + 1]
            # Generate the intensity histogram
            self.process_histograms("intensity")
            # Generate the Color Code histogram
            self.process_histograms("color_code")
            # Generate combined histogram
            self.combine_histograms()
            # Normalize combined histogram features
            self.normalize_histograms()
            # Write the generated data to cache
            self.write_to_cache(self.images)


        # Initialize default image order
        self.default_image_list = list(self.images.values())

    def intialize_image_data(self, i):
        """Generates an image information object containing basic info, representations and histograms of the image.

        Args:
            i (int): image number. 

        Returns:
            Dictionary: image basic info(resolution, name), representations with respect to methods(intensity, color-code), and corresponding histograms.
        """
        image_info = {}
        filepath = f".\\images\\png\\{i}.png"
        image = cv2.imread(filepath, cv2.IMREAD_COLOR)
        resolution_x = len(image)
        resolution_y = len(image[0])
        image_info[i] = {
            "name": i,
            "representation": image,
            "resolution_x": resolution_x,
            "resolution_y": resolution_y,
            "resolution": resolution_x * resolution_y,
            "color_code_representation": self.get_color_code_representaion(
                image, resolution_x, resolution_y
            ),
            "intensity_representation": np.transpose(
                np.dot(image, self.INTENSITY_COEFFICIENT_MATRIX)
            )[0],
            "path": filepath,
        }
        return image_info

    def load_cache_data(self):
        """Loads data from cache.

        Returns:
            Dictionary: deserialized cache data.
        """
        if not os.path.exists(CACHE_PATH):
            return

        cache_data = json.load(open(CACHE_PATH, "r"))
        # Convert data to work within the context of the module
        return self.deserialize_image_data(cache_data)

    def write_to_cache(self, data):
        """Write data to cache.

        Args:
            data(Dictionary): data to be cached. 
        """
        json.dump(self.serialize_image_data(data), open(CACHE_PATH, "w+"))

    def serialize_image_data(self, images):
        """Pick and convert the data to JSON serializable format.

        Args:
            images(Dictionary): List of images with their info.

        Returns:
            Dictionary: Data contatining image info(name, resolution and histograms).
        """
        data = {}
        for image in images:
            # Image representations are not cahced as they are of no interest post histogram computation
            data[image] = {}
            data[image]["name"] = images[image]["name"]
            data[image]["resolution"] = images[image]["resolution"]
            data[image]["path"] = images[image]["path"]
            data[image]["intensity_histogram"] = images[image][
                "intensity_histogram"
            ].tolist()
            data[image]["color_code_histogram"] = images[image][
                "color_code_histogram"
            ].tolist()
            data[image]["combined_histogram"] = images[image][
                "combined_histogram"
            ].tolist()
            
        return data

    def deserialize_image_data(self, images):
        """Convert the cache data to usable form.

        Args:
            images(Dictionary): List of images with their info.

        Returns:
            Dictionary: Image data with deserialized histogram arrays.
        """
        data = images
        for image in images:
            data[image]["intensity_histogram"] = np.array(
                images[image]["intensity_histogram"]
            )
            data[image]["color_code_histogram"] = np.array(
                images[image]["color_code_histogram"]
            )
            data[image]["combined_histogram"] = np.array(
                images[image]["combined_histogram"]
            )
        return data

    def get_color_code_representaion(self, image, m, n):
        """Get 6 bit color code representation of an image.

        Args:
            image (Array): 3D array representation for a 24 bit image.
            m (Integer): resolution coordinate 1.
            n (Integer): resolution coordinate 2.

        Returns:
            list: Array of 6 bit color code calculations.
        """
        color_code_array = [[0 for _ in range(n)] for _ in range(m)]
        for i in range(m):
            for j in range(n):
                significant_bits = ""
                for k in reversed(range(3)):
                    significant_bits += binary_of(image[i][j][k])[:2]
                color_code_array[i][j] = int_of(significant_bits)
        return color_code_array

    def compute_histogram(self, representation, type="intensity"):
        """Computes the histogram with respect to the type passed.

        Args:
            representation (list): image representation with respect to specific method.
            type (str, optional): Method used for color histogram calculation. Defaults to "intensity".

        Returns:
            list: color histogram of a specific image .
        """
        hist = [0] * (25 if type == "intensity" else 64)
        for i in range(len(representation)):
            for j in range(len(representation[0])):
                x = (
                    int(representation[i][j] // 10)
                    if type == "intensity"
                    else representation[i][j]
                )
                if type == "intensity" and x > 24.0:
                    x = 24
                hist[x] += 1
        return np.array(hist)

    def process_histograms(self, type="intensity"):
        """Processes and saves histograms in-memory for all images. 

        Args:
            type (str, optional): Method used for color histogram calculation. Defaults to "intensity".
        """
        for image in self.images:
            self.images[image][f"{type}_histogram"] = self.compute_histogram(
                self.images[image][f"{type}_representation"], type
            )

    def combine_histograms(self):
        """Combines and saves histograms in-memory for all images. """
        for image in self.images:
            self.images[image]["combined_histogram"] = np.concatenate((self.images[image]["intensity_histogram"], self.images[image]["color_code_histogram"])) / self.images[image]["resolution"]
        
        num_of_features = len(self.images[1]['combined_histogram'])
        self.weights = np.repeat(1/num_of_features, num_of_features)

    def normalize_histograms(self):
        """Normalizes and saves histograms in-memory for all images. """
        histograms = []
        for image in self.images:
            histograms.append(self.images[image]["combined_histogram"])
        histograms = np.array(histograms)
        avg = np.mean(histograms, axis=0)
        sd = np.std(histograms, axis=0)


        for i in range(len(histograms)):
            for j in range(len(histograms[0])):
                if avg[j] != 0:
                    histograms[i][j] -= avg[j]
                    if sd[j] > 0:                        
                        histograms[i][j] /= sd[j]
                    else:
                        histograms[i][j] /= self.get_zero_sd_normalization(sd)
                else:
                    histograms[i][j] = histograms[i][j]

        for i, histogram in enumerate(histograms):
            self.images[i+1]["combined_histogram"] = histogram
    
    def get_zero_sd_normalization(self, sd):
        s = sorted(sd)
        i = 0
        while s[i] == 0 and i < len(s):
            i += 1
        return s[i] / 2
    
    def update_feature_weights(self, chosen_image, relevant_images):
        """updates the feature weights according to the selected relevant images

        Args:
            chosen_image (list[list]): Image chosen
            relevant_images (list[list]): Images selected as relevant
        """
        histograms = [self.images[chosen_image]['combined_histogram']]
        for image in relevant_images:
            histograms.append(self.images[image]['combined_histogram'])
        histograms = np.array(histograms)
        avg = np.mean(histograms, axis=0)
        sd = np.std(histograms, axis=0, ddof=1)
        sd = [sd[i] if sd[i] > 0 else self.get_zero_sd_normalization(sd) for i in range(len(sd))]

        updated_weights = np.divide(1, sd)
        sd_sum = np.sum(updated_weights)
        for i in range(len(sd)):
            if sd[i] == 0:
                if avg[i] == 0:
                    self.weights[i] = 0
                    continue
            self.weights[i] = updated_weights[i] / sd_sum
        return    


    def caclulate_distance(self, image1, image2, type="intensity"):
        """Calculates manhattan distance between two image histograms.

        Args:
            image1 (list): image1 representation.
            image2 (list): image2 representation.
            type (str, optional): Method used for color histogram calculation. Defaults to "intensity".

        Returns:
            Integer: manhattan distance betweeen the two images.
        """
        if type == 'combined':
            feature_distances = np.multiply(self.weights, np.abs(image1[f"{type}_histogram"] - image2[f"{type}_histogram"]))
            return np.sum(feature_distances)    
        
        im1 = image1[f"{type}_histogram"] / image1["resolution"]
        im2 = image2[f"{type}_histogram"] / image2["resolution"]
        return np.sum(np.abs(im1 - im2))

    def process_image_distances(self, chosen_image, type="intensity"):
        """Process image distances between 1 chosen image and all other images.

        Args:
            chosen_image (list): selected image number.
            type (str, optional): Method used for color histogram calculation. Defaults to "intensity".

        Returns:
            list: images distance list. 
        """
        image_distances = []
        for image in self.images:
            if chosen_image != image:
                distance_info = {
                    "name": image,
                    "path": self.images[image]["path"],
                    "distance": self.caclulate_distance(
                        self.images[chosen_image], self.images[image], type
                    ),
                }
                image_distances.append(distance_info)
        return image_distances

    def retrieve_similar_images(self, chosen_image, method_label, relevant_images = []):
        """Sorts the image distance pairs between a selected image and all other images.

        Args:
            chosen_image (list): selected image number.
            method_label (str): Method used for color histogram calculation.

        Returns:
            list: image list sorted on lowest to highest distance. 
        """
        method = METHOD_MAP[method_label]
        if method == COMBINED and relevant_images:
            self.update_feature_weights(chosen_image, relevant_images)
        
        distances = self.process_image_distances(chosen_image, method)
        distances.sort(key=lambda x: x["distance"])
        return distances
    
    def resetWeights(self):
        """resets the weights to their intital values"""
        for i in range(len(self.weights)):
            self.weights[i] = DEFAULT_WEIGHT