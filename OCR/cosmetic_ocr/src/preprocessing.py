"""
Image Preprocessing Utilities
Functions to enhance images before OCR processing
"""

import cv2
import numpy as np
from typing import Tuple, Optional
from pathlib import Path


class ImagePreprocessor:
    """Preprocessing pipeline for cosmetic label images"""
    
    def __init__(self):
        self.debug_mode = False
    
    def resize_image(self, img: np.ndarray, max_width: int = 1600) -> np.ndarray:
        """Resize image while maintaining aspect ratio"""
        height, width = img.shape[:2]
        if width > max_width:
            ratio = max_width / width
            new_width = max_width
            new_height = int(height * ratio)
            img = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_AREA)
        return img
    
    def rotate_image(self, img: np.ndarray, angle: float) -> np.ndarray:
        """Rotate image by given angle"""
        height, width = img.shape[:2]
        center = (width // 2, height // 2)
        
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(img, rotation_matrix, (width, height),
                                 flags=cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    def deskew_image(self, img: np.ndarray) -> np.ndarray:
        """Automatically deskew image using edge detection"""
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi / 180, 200)
        
        if lines is not None and len(lines) > 0:
            # Calculate average angle
            angles = []
            for rho, theta in lines[:, 0]:
                angle = np.degrees(theta) - 90
                if -45 < angle < 45:  # Only consider reasonable angles
                    angles.append(angle)
            
            if angles:
                avg_angle = np.median(angles)
                if abs(avg_angle) > 0.5:  # Only rotate if significant skew
                    return self.rotate_image(img, avg_angle)
        
        return img
    
    def enhance_contrast(self, img: np.ndarray) -> np.ndarray:
        """Enhance image contrast using CLAHE"""
        # Convert to LAB color space
        if len(img.shape) == 3:
            lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
        else:
            l = img
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced_l = clahe.apply(l)
        
        if len(img.shape) == 3:
            # Merge channels
            enhanced_lab = cv2.merge([enhanced_l, a, b])
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        else:
            enhanced = enhanced_l
        
        return enhanced
    
    def denoise(self, img: np.ndarray) -> np.ndarray:
        """Remove noise from image"""
        if len(img.shape) == 3:
            denoised = cv2.fastNlMeansDenoisingColored(img, None, 10, 10, 7, 21)
        else:
            denoised = cv2.fastNlMeansDenoising(img, None, 10, 7, 21)
        return denoised
    
    def sharpen(self, img: np.ndarray) -> np.ndarray:
        """Sharpen image to enhance text edges"""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]])
        sharpened = cv2.filter2D(img, -1, kernel)
        return sharpened
    
    def binarize(self, img: np.ndarray, method: str = 'otsu') -> np.ndarray:
        """Convert to binary image"""
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        if method == 'otsu':
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == 'adaptive':
            binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
        else:
            raise ValueError(f"Unknown binarization method: {method}")
        
        return binary
    
    def remove_shadows(self, img: np.ndarray) -> np.ndarray:
        """Remove shadows using morphological operations"""
        # Convert to grayscale
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img
        
        # Dilate to get background
        dilated = cv2.dilate(gray, np.ones((7, 7), np.uint8))
        
        # Median blur the background
        bg = cv2.medianBlur(dilated, 21)
        
        # Calculate difference
        diff = 255 - cv2.absdiff(gray, bg)
        
        # Normalize
        normalized = cv2.normalize(diff, None, alpha=0, beta=255,
                                  norm_type=cv2.NORM_MINMAX, dtype=cv2.CV_8UC1)
        
        return normalized
    
    def preprocess_pipeline(self, img: np.ndarray,
                           resize: bool = True,
                           deskew: bool = True,
                           denoise: bool = True,
                           enhance: bool = True,
                           sharpen: bool = True,
                           remove_shadow: bool = False,
                           binarize: bool = False) -> np.ndarray:
        """
        Complete preprocessing pipeline
        
        Args:
            img: Input image
            resize: Resize to max width
            deskew: Auto-rotate to fix skew
            denoise: Remove noise
            enhance: Enhance contrast
            sharpen: Sharpen edges
            remove_shadow: Remove shadows
            binarize: Convert to binary
            
        Returns:
            Preprocessed image
        """
        result = img.copy()
        
        if resize:
            result = self.resize_image(result)
        
        if deskew:
            result = self.deskew_image(result)
        
        if remove_shadow:
            result = self.remove_shadows(result)
        
        if denoise:
            result = self.denoise(result)
        
        if enhance:
            result = self.enhance_contrast(result)
        
        if sharpen:
            result = self.sharpen(result)
        
        if binarize:
            result = self.binarize(result)
        
        return result
    
    def process_directory(self, input_dir: str, output_dir: str, **kwargs):
        """Process all images in a directory"""
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp']
        image_files = [f for f in input_path.iterdir() 
                      if f.suffix.lower() in image_extensions]
        
        print(f"Processing {len(image_files)} images...")
        
        for img_file in image_files:
            print(f"  Processing: {img_file.name}")
            
            # Load image
            img = cv2.imread(str(img_file))
            
            # Preprocess
            processed = self.preprocess_pipeline(img, **kwargs)
            
            # Save
            output_file = output_path / img_file.name
            cv2.imwrite(str(output_file), processed)
        
        print(f"Done! Processed images saved to {output_dir}")


def main():
    """Main execution for testing"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Preprocess cosmetic label images')
    parser.add_argument('--input-dir', type=str, default='data/raw_images',
                       help='Input directory')
    parser.add_argument('--output-dir', type=str, default='data/processed',
                       help='Output directory')
    parser.add_argument('--no-resize', action='store_true', help='Skip resize')
    parser.add_argument('--no-deskew', action='store_true', help='Skip deskew')
    parser.add_argument('--binarize', action='store_true', help='Convert to binary')
    
    args = parser.parse_args()
    
    preprocessor = ImagePreprocessor()
    preprocessor.process_directory(
        args.input_dir,
        args.output_dir,
        resize=not args.no_resize,
        deskew=not args.no_deskew,
        binarize=args.binarize
    )


if __name__ == '__main__':
    main()
