import sys
from logger_config import logger  # Importing the logger
from counter import config

if __name__ == '__main__':
    try:
        logger.info("Starting the script.")
        img_path = sys.argv[1]
        threshold = float(sys.argv[2])
        logger.info(f"Image path: {img_path}, Threshold: {threshold}")

        with open(img_path, 'rb') as img:
            logger.info("Executing the count action.")
            predictions = config.get_count_action().execute(img, threshold)
            logger.info(f"Predictions: {predictions}")
            print(predictions)
    except FileNotFoundError as e:
        logger.error(f"File not found: {e}")
        sys.exit(1)
    except ValueError as e:
        logger.error(f"Invalid input: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        sys.exit(1)
    finally:
        logger.info("Script execution completed.")