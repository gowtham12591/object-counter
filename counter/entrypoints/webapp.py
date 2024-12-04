from io import BytesIO
import os
from flask import Flask, request, jsonify
from logger_config import logger  
from counter import config

def create_app():
    app = Flask(__name__)
    count_action = config.get_count_action()

    @app.route('/')
    def home():
        return "Welcome to Objection detection and counting project!"

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"}), 200

    @app.route('/api/v1/object-detect-count', methods=['POST'])
    def object_detection():
        try:
            logger.info("Received a request for object detection.")
            threshold = float(request.form.get('threshold', 0.5))
            logger.info(f"Threshold received: {threshold}")

            uploaded_file = request.files.get('file')
            if not uploaded_file:
                logger.error("No file uploaded in the request.")
                return jsonify({"error": "No file uploaded"}), 400

            logger.info(f"Processing uploaded file: {uploaded_file.filename}")
            image = BytesIO()
            uploaded_file.save(image)

            logger.info("Executing count action.")
            count_response = count_action.execute(image, threshold)

            logger.info(f"Count action executed successfully. Response: {count_response}")
            return jsonify(count_response)
        except KeyError as e:
            logger.error(f"KeyError: {e}")
            return jsonify({"error": "Missing or incorrect input parameters"}), 400
        except ValueError as e:
            logger.error(f"ValueError: {e}")
            return jsonify({"error": "Invalid threshold value"}), 400
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            return jsonify({"error": "An unexpected error occurred"}), 500
        finally:
            logger.info("Request processing completed.")

    return app

if __name__ == '__main__':
    try:
        env = os.getenv("ENV", "dev")
        debug_mode = env != "prod"
        logger.info(f"Starting the application in {env} mode.")
        app = create_app()
        app.run('0.0.0.0', port=8080, debug=debug_mode)
    except Exception as e:
        logger.critical(f"Failed to start the application: {e}")