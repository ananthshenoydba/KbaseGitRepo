import cv2
import os

def process_image(img_path):
    """
    Reads an image, converts to grayscale, upscales, lightly sharpens, returns processed image.
    """
    img = cv2.imread(img_path)
    if img is None:
        return None

    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Upscale 2x using Lanczos
    upscaled = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LANCZOS4)

    # Light sharpening
    blurred = cv2.GaussianBlur(upscaled, (0, 0), 1.0)
    sharpened = cv2.addWeighted(upscaled, 1.5, blurred, -0.5, 0)

    return sharpened

def process_directory(input_dir, output_dir):
    """
    Processes all images in input_dir and writes to output_dir as PNG.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    supported_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff')

    for filename in os.listdir(input_dir):
        if filename.lower().endswith(supported_ext):
            input_path = os.path.join(input_dir, filename)
            output_filename = os.path.splitext(filename)[0] + ".png"
            output_path = os.path.join(output_dir, output_filename)

            processed_img = process_image(input_path)
            if processed_img is not None:
                cv2.imwrite(output_path, processed_img)
                print(f"Processed: {filename} → {output_filename}")
            else:
                print(f"Failed to read: {filename}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="OCR-ready image preprocessing")
    parser.add_argument("input_dir", help="Directory containing input images")
    parser.add_argument("output_dir", help="Directory to save processed images")
    args = parser.parse_args()

    process_directory(args.input_dir, args.output_dir)
