from PIL import Image, ImageDraw, ImageFont
import os


def preprocess_image(file_path, agent_id):
    try:
        # Open the image and convert it to RGB (for non-RGB images)
        image = Image.open(file_path).convert('RGB')
        watermark = f"AgentID: {agent_id}"

        # Create an image draw object
        draw = ImageDraw.Draw(image)

        # Load a better font, fall back to default if not available
        try:
            font = ImageFont.truetype("arial.ttf", int(image.size[1] * 0.05))  # Font size 5% of image height
        except IOError:
            font = ImageFont.load_default()

        # Get the bounding box for the watermark text (textbbox gives the box instead of size)
        bbox = draw.textbbox((0, 0), watermark, font=font)
        text_width, text_height = bbox[2] - bbox[0], bbox[3] - bbox[1]

        # Position the watermark in the bottom-right corner
        width, height = image.size
        position = (width - text_width - 10, height - text_height - 10)

        # Add the watermark text
        # draw.text(position, watermark, fill=(0, 0, 0), font=font)  # Black color for better visibility
        draw.text(position, watermark, fill=(255, 255, 255), font=font)  # White color for better invisibility

        # Generate output file name (keep the same file extension)
        output_file = f"{os.path.splitext(file_path)[0]}_{agent_id}{os.path.splitext(file_path)[1]}"

        # Save the new image with watermark
        image.save(output_file)

        return output_file
    except Exception as e:
        print(f"Error processing image file {file_path}: {e}")
        return None


'''
1) Dynamic Font Sizing:
    The font size is now dynamically set to 5% of the image height, so the watermark will scale appropriately across 
    different image sizes.

2) Custom Font Handling:
    The code tries to load a more visually appealing font (arial.ttf) and falls back to the default font if it’s not 
    available on the system. We can replace "arial.ttf" with any available font on our system or provide a path to a 
    custom font.
    
3) Handling File Extensions:
    The output file retains the same file extension as the input file, ensuring that we don’t force .jpg for all images.

4) Error Handling:
    A try-except block ensures that any errors during image processing (such as issues with file formats or file I/O) 
    are caught and logged, and the function returns None in case of failure.
'''


'''
Additional Improvements that can be done:
1) Watermark Color Adaptation:
    If we want the watermark to adapt to light or dark backgrounds, we can analyze the image's pixel brightness in the
    watermark area and adjust the text color accordingly.

2) Watermark Opacity:
    If we want to make the watermark less obtrusive, we can create a semi-transparent watermark by blending it into 
    the image.

3) Test with Multiple Formats:
    Ensure we test the function with different image formats (.jpg, .bmp, .png, etc.) to verify that the preprocessing 
    works across all supported types.
'''