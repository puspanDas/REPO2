from PIL import Image
import pytesseract
import os

class ImageProcessor:
    def __init__(self):
        # Set tesseract path if needed (Windows)
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def extract_text_from_image(self, image_path):
        try:
            # Open and process image
            image = Image.open(image_path)
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            return text.strip()
        
        except Exception as e:
            return f"Error processing image: {str(e)}"
    
    def is_image_file(self, filename):
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif'}
        return any(filename.lower().endswith(ext) for ext in image_extensions)