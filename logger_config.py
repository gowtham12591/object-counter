import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,  # Set the lowest level of logs to capture
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='app.log',  # Log messages will be written to this file
    filemode='w'         # 'w' to overwrite the file; 'a' to append to it
)

# Create and export a logger
logger = logging.getLogger("MyLogger")
