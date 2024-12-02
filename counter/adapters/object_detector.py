import json                                                 # Importing JSON library to handle JSON files and data
from typing import List, BinaryIO                           # Importing List for type hinting and BinaryIO for file input

import numpy as np                                          # Importing NumPy for numerical operations
import requests                                             # Importing requests library to handle HTTP requests
from PIL import Image                                       # Importing PIL for image processing

from counter.domain.models import Prediction, Box           # Importing Prediction and Box domain models
from counter.domain.ports import ObjectDetector             # Importing ObjectDetector interface/port
from logger_config import logger                            # Importing logger from logger_config

# Fake object detector implementation for testing purposes
class FakeObjectDetector(ObjectDetector):
    def predict(self, image: BinaryIO) -> List[Prediction]:
        try:
            logger.info("FakeObjectDetector: Generating fake prediction.")
            return [Prediction(
                class_name='cat',                                                               # Predicted class is 'cat'
                score=0.999190748,                                                              # High confidence score
                box=Box(xmin=0.367288858, ymin=0.278333426, xmax=0.735821366, ymax=0.6988855)   # Predicted bounding box
            )]
        except Exception as e:
            logger.error(f"Error in FakeObjectDetector: {e}")
            raise e

# TensorFlow Serving-based object detector implementation
class TFSObjectDetector(ObjectDetector):
    def __init__(self, host, port, model):
        try:
            self.url = f"http://{host}:{port}/v1/models/{model}:predict"
            logger.info(f"TFSObjectDetector initialized with URL: {self.url}")
            self.classes_dict = self.__build_classes_dict()
        except Exception as e:
            logger.error(f"Error initializing TFSObjectDetector: {e}")
            raise e

    def predict(self, image: BinaryIO) -> List[Prediction]:
        try:
            logger.info("Starting prediction using TFSObjectDetector.")
            np_image = self.__to_np_array(image)
            predict_request = '{"instances" : %s}' % np.expand_dims(np_image, 0).tolist()
            logger.debug(f"Sending prediction request to URL: {self.url}")
            response = requests.post(self.url, data=predict_request)
            response.raise_for_status()
            predictions = response.json()['predictions'][0]
            logger.info("Prediction response received successfully.")
            return self.__raw_predictions_to_domain(predictions)
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP error during prediction: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error in TFSObjectDetector predict method: {e}")
            raise e

    @staticmethod
    def __build_classes_dict():
        try:
            logger.info("Building class dictionary from JSON file.")
            with open('counter/adapters/mscoco_label_map.json') as json_file:
                labels = json.load(json_file)
                logger.debug("Class dictionary loaded successfully.")
                return {label['id']: label['display_name'] for label in labels}
        except FileNotFoundError as e:
            logger.error(f"JSON file not found: {e}")
            raise e
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON file: {e}")
            raise e
        except Exception as e:
            logger.error(f"Unexpected error while building class dictionary: {e}")
            raise e

    @staticmethod
    def __to_np_array(image: BinaryIO):
        try:
            logger.info("Converting image to NumPy array.")
            image_ = Image.open(image)
            (im_width, im_height) = image_.size
            np_array = np.array(image_.getdata()).reshape((im_height, im_width, 3)).astype(np.uint8)
            logger.debug("Image converted to NumPy array successfully.")
            return np_array
        except Exception as e:
            logger.error(f"Error converting image to NumPy array: {e}")
            raise e

    def __raw_predictions_to_domain(self, raw_predictions: dict) -> List[Prediction]:
        try:
            logger.info("Parsing raw predictions.")
            num_detections = int(raw_predictions.get('num_detections'))
            predictions = []
            for i in range(num_detections):
                detection_box = raw_predictions['detection_boxes'][i]
                box = Box(
                    xmin=detection_box[1], ymin=detection_box[0],
                    xmax=detection_box[3], ymax=detection_box[2]
                )
                detection_score = raw_predictions['detection_scores'][i]
                detection_class = raw_predictions['detection_classes'][i]
                class_name = self.classes_dict[detection_class]
                predictions.append(Prediction(class_name=class_name, score=detection_score, box=box))
            logger.debug(f"Parsed predictions: {predictions}")
            return predictions
        except KeyError as e:
            logger.error(f"Error parsing raw predictions - missing key: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error parsing raw predictions: {e}")
            raise e