import pytesseract
from PIL import Image, ImageEnhance, ImageFilter
import re

# IMPORTANT: Windows users need to point to the tesseract executable
# If strictly necessary, we could add auto-detection, but usually this is set in PATH or manually.
# For this environment, we'll try to rely on PATH or a standard location.
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def preprocess_image(image):
    """
    Convert image to grayscale and apply mild processing to improve OCR accuracy.
    """
    # Convert to grayscale
    img = image.convert('L')
    
    # Increase contrast roughly
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.5)
    
    # Optional: Apply mild sharpening if needed, but sometimes it adds noise.
    # img = img.filter(ImageFilter.SHARPEN)
    
    return img

def extract_text(image):
    """
    Run Tesseract OCR on the image.
    """
    try:
        processed_img = preprocess_image(image)
        text = pytesseract.image_to_string(processed_img)
        return text
    except Exception as e:
        # Check if tesseract is not found, try pointing to default location
        if "tesseract is not installed" in str(e).lower() or "not found" in str(e).lower():
            try:
                # Common default installation path on Windows
                default_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                pytesseract.pytesseract.tesseract_cmd = default_path
                return pytesseract.image_to_string(preprocess_image(image))
            except Exception as e2:
                # If still failing, return the missing error
                if "not found" in str(e2).lower() or "permission denied" in str(e2).lower():
                     return "TESSERACT_MISSING"
                return f"Error extracting text (Retry failed): {e2}"

        return f"Error extracting text: {e}"

def parse_total(text):
    """
    Attempt to find the 'Total' amount from OCR text using Regex.
    Returns the float amount or 0.0 if not found.
    """
    lines = text.split('\n')
    total_candidates = []

    # Common patterns for total lines
    # Look for "Total", "Amount Due", "Grand Total" followed by digits
    # Regex explanations:
    # 1. (?:Total|Amount|Due|Pay)... matches keywords
    # 2. [^0-9\.]* matches any non-digit/dot chars (like currency symbols, spaces, colons)
    # 3. (\d+\.\d{2}) captures the number (assuming 2 decimal places usually)
    
    pattern = r"(?i)(?:total|grand total|amount due|balance|subtotal).*?(\d{1,5}\.\d{2})"
    
    for line in lines:
        cleaned_line = line.strip()
        match = re.search(pattern, cleaned_line)
        if match:
            try:
                amount = float(match.group(1))
                total_candidates.append(amount)
            except ValueError:
                continue
                
    # Fallback: Just look for the largest number that looks like a price at the bottom of the receipt?
    # This is risky. Let's stick to explicit keywords first.
    
    # If multiple matches, usually the last "Total" is the Grand Total (after tax etc)
    if total_candidates:
        return total_candidates[-1]
    
    # Strategy B: If no keyword found, look for isolated prices and take the max? 
    # Or just return 0.0 and let user fill it. Better to be safe.
    
    return 0.0

if __name__ == "__main__":
    # Test stub
    pass
