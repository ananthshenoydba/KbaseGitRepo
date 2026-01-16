"""
Baseline OCR Testing Script
Tests multiple OCR engines on cosmetic ingredient labels
"""

import os
import time
from pathlib import Path
from typing import Dict, List, Tuple
import cv2
import numpy as np
from PIL import Image


class BaselineOCR:
    """Test different OCR engines on the same images"""
    
    def __init__(self, image_dir: str):
        self.image_dir = Path(image_dir)
        self.results = {}
        
    def load_image(self, image_path: str) -> np.ndarray:
        """Load image using OpenCV"""
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"Could not load image: {image_path}")
        return img
    
    def preprocess_image(self, img: np.ndarray) -> np.ndarray:
        """Basic preprocessing to improve OCR accuracy"""
        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Denoise
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Increase contrast using CLAHE
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(denoised)
        
        # Threshold
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return binary
    
    def test_easyocr(self, image_path: str) -> Dict:
        """Test EasyOCR"""
        try:
            import easyocr
            reader = easyocr.Reader(['en'], gpu=False)
            
            start_time = time.time()
            result = reader.readtext(str(image_path))
            elapsed = time.time() - start_time
            
            # Extract just the text
            text = ' '.join([detection[1] for detection in result])
            
            return {
                'engine': 'EasyOCR',
                'text': text,
                'time': elapsed,
                'raw_result': result,
                'success': True
            }
        except Exception as e:
            return {
                'engine': 'EasyOCR',
                'text': '',
                'time': 0,
                'error': str(e),
                'success': False
            }
    
    def test_tesseract(self, image_path: str) -> Dict:
        """Test Tesseract OCR"""
        try:
            import pytesseract
            
            img = Image.open(image_path)
            
            start_time = time.time()
            text = pytesseract.image_to_string(img)
            elapsed = time.time() - start_time
            
            return {
                'engine': 'Tesseract',
                'text': text.strip(),
                'time': elapsed,
                'success': True
            }
        except Exception as e:
            return {
                'engine': 'Tesseract',
                'text': '',
                'time': 0,
                'error': str(e),
                'success': False
            }
    
    def test_paddleocr(self, image_path: str) -> Dict:
        """Test PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            
            ocr = PaddleOCR(use_textline_orientation=True, lang='en')
    
            start_time = time.time()
            result = ocr.predict(str(image_path))
            elapsed = time.time() - start_time
            
            # Extract text
            text = ' '.join([line[1][0] for line in result[0]]) if result and result[0] else ''
            
            return {
                'engine': 'PaddleOCR',
                'text': text,
                'time': elapsed,
                'raw_result': result,
                'success': True
            }
        except Exception as e:
            return {
                'engine': 'PaddleOCR',
                'text': '',
                'time': 0,
                'error': str(e),
                'success': False
            }
    
    def run_all_tests(self, image_path: str) -> List[Dict]:
        """Run all OCR engines on a single image"""
        print(f"\nTesting: {image_path}")
        print("-" * 60)
        
        results = []
        
        # Test each engine
        for test_func in [self.test_easyocr, self.test_tesseract, self.test_paddleocr]:
            result = test_func(image_path)
            results.append(result)
            
            if result['success']:
                print(f"\n{result['engine']}:")
                print(f"  Time: {result['time']:.2f}s")
                print(f"  Text length: {len(result['text'])} chars")
                print(f"  Preview: {result['text'][:100]}...")
            else:
                print(f"\n{result['engine']}: FAILED - {result.get('error', 'Unknown error')}")
        
        return results
    
    def test_directory(self, limit: int = None) -> Dict[str, List[Dict]]:
        """Test all images in the directory"""
        image_files = list(self.image_dir.glob('*.jpg')) + \
                      list(self.image_dir.glob('*.png')) + \
                      list(self.image_dir.glob('*.jpeg'))
        
        if limit:
            image_files = image_files[:limit]
        
        print(f"Found {len(image_files)} images")
        
        all_results = {}
        for img_path in image_files:
            results = self.run_all_tests(str(img_path))
            all_results[img_path.name] = results
        
        return all_results
    
    def compare_results(self, results: Dict[str, List[Dict]]):
        """Print comparison summary"""
        print("\n" + "=" * 80)
        print("COMPARISON SUMMARY")
        print("=" * 80)
        
        for image_name, image_results in results.items():
            print(f"\n{image_name}:")
            for result in image_results:
                if result['success']:
                    print(f"  {result['engine']:15} | {result['time']:5.2f}s | {len(result['text']):4} chars")
                else:
                    print(f"  {result['engine']:15} | FAILED")


def main():
    """Main execution"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Test OCR engines on cosmetic labels')
    parser.add_argument('--image-dir', type=str, default='data/raw_images',
                        help='Directory containing images')
    parser.add_argument('--limit', type=int, default=None,
                        help='Limit number of images to test')
    
    args = parser.parse_args()
    
    # Run tests
    tester = BaselineOCR(args.image_dir)
    results = tester.test_directory(limit=args.limit)
    tester.compare_results(results)
    
    return results


if __name__ == '__main__':
    main()
