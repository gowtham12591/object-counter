from PIL import Image
from logger_config import logger  # Importing the logger

from counter.debug import draw
from counter.domain.models import CountResponse
from counter.domain.ports import ObjectDetector, ObjectCountRepo
from counter.domain.predictions import over_threshold, count


class CountDetectedObjects:
    def __init__(self, object_detector: ObjectDetector, object_count_repo: ObjectCountRepo):
        try:
            logger.info("Initializing CountDetectedObjects.")
            self.__object_detector = object_detector
            self.__object_count_repo = object_count_repo
        except Exception as e:
            logger.error(f"Error during CountDetectedObjects initialization: {e}")
            raise e

    def execute(self, image, threshold) -> CountResponse:
        try:
            logger.info(f"Executing object count with threshold: {threshold}")
            predictions = self.__find_valid_predictions(image, threshold)

            object_counts = count(predictions)
            logger.debug(f"Object counts: {object_counts}")

            self.__object_count_repo.update_values(object_counts)
            logger.info("Updated object counts in the repository.")
            
            total_objects = self.__object_count_repo.read_values()
            logger.debug(f"Total objects from repository: {total_objects}")
            print('-*'*50)
            print(f"current_objects: {object_counts}, total_objects: {total_objects}")
            return CountResponse(current_objects=object_counts, total_objects=total_objects)
        except Exception as e:
            logger.error(f"Error during execute: {e}")
            raise e

    def __find_valid_predictions(self, image, threshold):
        try:
            logger.info(f"Finding valid predictions with threshold: {threshold}")
            predictions = self.__object_detector.predict(image)
            logger.debug(f"Predictions received: {predictions}")
            self.__debug_image(image, predictions, "all_predictions.jpg")
            valid_predictions = over_threshold(predictions, threshold=threshold)
            logger.debug(f"Valid predictions after applying threshold: {valid_predictions}")
            self.__debug_image(image, valid_predictions, f"valid_predictions_with_threshold_{threshold}.jpg")
            return valid_predictions
        except Exception as e:
            logger.error(f"Error in __find_valid_predictions: {e}")
            raise e

    @staticmethod
    def __debug_image(image, predictions, image_name):
        try:
            if __debug__ and image is not None:
                logger.info(f"Debugging image: {image_name}")
                image = Image.open(image)
                draw(predictions, image, image_name)
                logger.info(f"Debug image saved as {image_name}.")
        except Exception as e:
            logger.error(f"Error during __debug_image: {e}")
            raise e