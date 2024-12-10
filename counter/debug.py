import os
from PIL import ImageDraw, ImageFont
from logger_config import logger

def draw(predictions, image, image_name):
    try:
        draw_image = ImageDraw.Draw(image, "RGBA")
        image_width, image_height = image.size

        # Load the font
        font_path = "counter/resources/arial.ttf"
        font = ImageFont.truetype(font_path, 20)
        logger.info(f"Loaded font from {font_path}")

        # Draw predictions on the image
        for i, prediction in enumerate(predictions):
            box = prediction.box
            draw_image.rectangle(
                [(box.xmin * image_width, box.ymin * image_height),
                 (box.xmax * image_width, box.ymax * image_height)],
                outline='red'
            )
            class_name = prediction.class_name
            draw_image.text(
                (box.xmin * image_width, box.ymin * image_height - font.getlength(class_name)),
                f"{class_name}: {prediction.score}", font=font, fill='black'
            )
        logger.info(f"Annotated {len(predictions)} predictions on the image.")

        # Ensure the directory exists
        debug_dir = 'tmp/debug'
        if not os.path.exists(debug_dir):
            os.makedirs(debug_dir)
            logger.info(f"Created directory: {debug_dir}")

        # Save the annotated image
        output_path = os.path.join(debug_dir, image_name)
        image.save(output_path, "JPEG")
        logger.info(f"Saved annotated image to {output_path}")

    except FileNotFoundError as fnfe:
        logger.error(f"Font file not found: {fnfe}")
    except Exception as e:
        logger.error(f"An error occurred while drawing predictions: {e}")