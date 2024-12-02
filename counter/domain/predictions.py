from functools import reduce
from typing import List
from logger_config import logger  # Importing the logger

from counter.domain.models import Prediction, ObjectCount


def over_threshold(predictions: List[Prediction], threshold: float):
    try:
        logger.info(f"Filtering predictions with a threshold of {threshold}.")
        filtered_predictions = list(filter(lambda prediction: prediction.score >= threshold, predictions))
        logger.debug(f"Filtered predictions: {list(filtered_predictions)}")
        return filtered_predictions
    except Exception as e:
        logger.error(f"Error in over_threshold: {e}")
        raise e


def count(predictions: List[Prediction]) -> List[ObjectCount]:
    try:
        logger.info("Counting object occurrences in predictions.")
        object_classes = map(lambda prediction: prediction.class_name, predictions)
        object_classes_counter = reduce(__count_object_classes, object_classes, {})
        logger.debug(f"Object class counts: {object_classes_counter}")
        return [ObjectCount(object_class, occurrences) for object_class, occurrences in object_classes_counter.items()]
    except Exception as e:
        logger.error(f"Error in count: {e}")
        raise e


def __count_object_classes(class_counter: dict, object_class: str):
    try:
        logger.debug(f"Incrementing count for class: {object_class}. Current counter: {class_counter}")
        class_counter[object_class] = class_counter.get(object_class, 0) + 1
        return class_counter
    except Exception as e:
        logger.error(f"Error in __count_object_classes: {e}")
        raise e