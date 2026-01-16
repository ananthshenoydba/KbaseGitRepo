#!/usr/bin/env python3
"""
Cosmetic Ingredient OCR with Tiny Local LLM (transformers)
Uses: distilbert or similar lightweight models
No Ollama needed - pure Python!
"""

import pytesseract
from PIL import Image
from pathlib import Path
import re
from typing import List, Dict, Tuple
import time
from difflib import get_close_matches, SequenceMatcher

# Try to import transformers, but make it optional
try:
    from transformers import pipeline
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False
    print("⚠ transformers not installed. Install with: pip install transformers torch")


class IngredientDatabase:
    """In-memory ingredient database"""
    
    def __init__(self):
        self.ingredients = [
            # Water and solvents  
            "Aqua", "Water", "Alcohol Denat", "SD Alcohol 40",
            "Glycerin", "Propylene Glycol", "Butylene Glycol",
            
            # Surfactants
            "Sodium Lauryl Sulfate", "Ammonium Lauryl Sulfate",
            "Cocamidopropyl Betaine", "Decyl Glucoside", "Lauryl Glucoside",
            
            # Silicones
            "Dimethicone", "Amodimethicone", "Cyclomethicone",
            
            # Polymers
            "Polyquaternium-7", "Polyquaternium-10",
            "Acrylates Copolymer", "Acrylates/C10-30 Alkyl Acrylate Crosspolymer",
            "Carbomer",
            
            # Alcohols
            "Cetyl Alcohol", "Stearyl Alcohol", "Cetearyl Alcohol", "Benzyl Alcohol",
            
            # Emulsifiers
            "Glycol Distearate", "Glyceryl Stearate", "Glyceryl Stearate SE",
            "Hydrogenated Coco-Glycerides",
            "PEG-150 Distearate", "PEG-45M", "Laureth-4", "Laureth-23",
            "Sodium Cetearyl Sulfate",
            "Stearalkonium Chloride", "Distearyldimonium Chloride", "Quaternium-18",
            "Isopropyl Palmitate", "Isopropyl Myristate",
            
            # Preservatives
            "Sodium Benzoate", "Potassium Sorbate", "Phenoxyethanol",
            "Methylchloroisothiazolinone", "Methylisothiazolinone",
            "Ethylhexylglycerin",
            
            # pH adjusters
            "Citric Acid", "Sodium Hydroxide",
            
            # Chelating
            "Disodium EDTA", "Trisodium EDTA",
            
            # Fragrance
            "Fragrance", "Parfum", "Linalool", "Limonene", "Citronellol",
            "Eugenol", "Hexyl Cinnamal", "Alpha-Isomethyl Ionone",
            
            # Actives
            "Creatine", "Ubiquinone", "1-Methyl-hydantoin-2-Imide",
            "Panthenol", "Tocopherol", "Niacinamide",
            "Betaine", "Allantoin", "Arginine",
            "1,2-Hexanediol", "Ethyl Hexanediol",
            
            # Natural extracts
            "Cicer Arietinum Seed Extract", "Terminalia Bellerica Fruit Extract",
            "Snail Secretion Filtrate",
            "Avena Sativa Kernel Flour", "Avena Sativa (Oat) Kernel Flour",
            
            # Humectants
            "Maltooligosyl Glucoside", "Hydrogenated Starch Hydrolysate",
            "Sodium Hyaluronate", "Hyaluronic Acid",
            
            # UV filters
            "Octocrylene", "Butyl Methoxydibenzoylmethane",
            
            # Others
            "BHT", "Octyldodecanol", "Butyrospermum Parkii Butter",
            "Petrolatum", "Mineral Oil", "Paraffinum Liquidum",
            "Sodium Chloride", "Sodium Polyacrylate",
        ]
        self.ingredients_lower = [i.lower() for i in self.ingredients]


class CosmeticOCRSimple:
    """OCR with smart rule-based filtering (no LLM needed)"""
    
    def __init__(self):
        self.db = IngredientDatabase()
    
    def simple_parse(self, text: str) -> List[str]:
        """
        SIMPLE parsing - just split by commas
        BUT stop at packaging text first!
        """
        # Find ingredients with fuzzy matching
        match = re.search(r'\w{0,2}ngredients?\s*:?\s*', text, flags=re.IGNORECASE)
        if match:
            text = text[match.end():]
        
        # Handle hyphenated line breaks ONLY
        text = re.sub(r'-\s*\n\s*', '', text)
        
        # FIX OCR ERRORS: Period between ingredients should be comma
        # "Panthenol. Arginine" → "Panthenol, Arginine"
        # Only replace period if followed by space and capital letter (next ingredient)
        text = re.sub(r'\.\s+(?=[A-Z])', ', ', text)
        
        # CRITICAL: Stop at packaging text BEFORE splitting!
        # Look for common stop phrases
        stop_phrases = ['No animal', 'animal derived', 'Fri från', 'Uden', 'tA.', 
                       'tap et', 'Warning:', 'For external use', 'Keep out']
        
        for stop in stop_phrases:
            if stop in text:
                # Find position and cut text there
                pos = text.find(stop)
                before_stop = text[:pos]
                
                # Look back for last separator: comma, period, OR multiple newlines/spaces
                last_comma = before_stop.rfind(',')
                last_period = before_stop.rfind('.')
                
                # Also look for significant whitespace (2+ newlines or 5+ spaces)
                last_whitespace = -1
                # Find sequences of 2+ newlines or 5+ spaces
                whitespace_matches = list(re.finditer(r'\n\n+|\s{5,}', before_stop))
                if whitespace_matches:
                    last_whitespace = whitespace_matches[-1].end()
                
                # Use the LAST separator (whichever comes latest)
                last_separator = max(last_comma, last_period, last_whitespace)
                
                if last_separator > 0:
                    text = text[:last_separator + 1]  # Keep up to and including separator
                else:
                    text = before_stop.rstrip()
                break
        
        # Protect commas in chemical names
        text = re.sub(r'(\d),(\d)', r'\1|COMMA|\2', text)
        
        # Split by comma ONLY (periods already converted to commas above)
        raw = [p.strip() for p in text.split(',')]
        
        # Restore commas and normalize whitespace
        cleaned = []
        for ing in raw:
            ing = ing.replace('|COMMA|', ',')
            ing = ing.replace('\n', ' ')
            ing = ' '.join(ing.split())
            ing = ing.strip(' .')
            if len(ing) >= 2:
                cleaned.append(ing)
        
        return cleaned
    
    def smart_filter_ingredients(self, candidates: List[str]) -> List[str]:
        """
        Smart rule-based filtering - no LLM needed
        Uses multiple heuristics to identify real ingredients
        WITH DETAILED LOGGING
        """
        filtered = []
        
        # Keywords that indicate non-ingredients
        bad_keywords = [
            'warning', 'for external', 'keep out', 'avoid', 'rinse', 'thoroughly',
            'apply', 'use only', 'needed', 'children', 'child', 'ony', 'out of reach',
            'patent', 'manufacture', 'batch', 'exp', 'mfg', 'lic', 'directions',
            'store in', 'cool', 'dry', 'place', 'made in', 'dist by', 'net wt',
            'tested', 'proven', 'dermatologist', 'hypoallergenic'
        ]
        
        # Patterns that look like ingredient names
        ingredient_patterns = [
            r'[A-Z][a-z]+\s+[A-Z][a-z]+',  # "Sodium Chloride"
            r'[A-Z][a-z]+\s+\([A-Za-z]+\)',  # "Avena (Oat)"
            r'\d,\d-[A-Za-z]+',  # "1,2-Hexanediol"
            r'[A-Z][a-z]+\s+[A-Z][a-z]+\s+[A-Z][a-z]+',  # "Avena Sativa Kernel"
        ]
        
        print("\n" + "="*80)
        print("FILTERING DETAILS:")
        print("="*80)
        
        for i, item in enumerate(candidates, 1):
            item_lower = item.lower()
            reasons = []
            
            # Rule 1: Skip if too short
            if len(item) < 3:
                print(f"{i:2}. ❌ FILTERED: {repr(item):40} → Too short (len={len(item)})")
                continue
            
            # Rule 2: Skip if contains bad keywords
            bad_found = [bad for bad in bad_keywords if bad in item_lower]
            if bad_found:
                print(f"{i:2}. ❌ FILTERED: {repr(item):40} → Bad keywords: {bad_found}")
                continue
            
            # Rule 3: Skip if mostly non-alphabetic (junk OCR)
            alpha_count = sum(c.isalpha() for c in item)
            alpha_pct = alpha_count / len(item) if len(item) > 0 else 0
            if alpha_pct < 0.4:  # Less than 40% letters
                print(f"{i:2}. ❌ FILTERED: {repr(item):40} → Junk OCR (alpha={alpha_pct:.1%})")
                continue
            
            # Rule 3b: Skip if contains too many special characters
            special_chars = sum(1 for c in item if c in '!—.,;:')
            if special_chars >= 3:
                print(f"{i:2}. ❌ FILTERED: {repr(item):40} → Too many special chars ({special_chars})")
                continue
            
            # Rule 3c: Skip if still contains the word "ingredient" or "PIGREDIENT"
            if 'ingredient' in item_lower or 'gredient' in item_lower:
                print(f"{i:2}. ❌ FILTERED: {repr(item):40} → Contains 'ingredient'")
                continue
            
            # Rule 4: Skip if looks like a sentence (has common words)
            common_words = ['the', 'and', 'for', 'with', 'from', 'this', 'that', 'as']
            word_count = sum(1 for word in common_words if word in item_lower)
            if word_count >= 2:
                print(f"{i:2}. ❌ FILTERED: {repr(item):40} → Sentence ({word_count} common words)")
                continue
            
            # Rule 5: Prefer items matching ingredient patterns
            matches_pattern = any(re.search(pattern, item) for pattern in ingredient_patterns)
            if matches_pattern:
                reasons.append("matches pattern")
            
            # Rule 6: Check if it's close to a known ingredient
            close_to_known = self.is_close_to_known(item)
            if close_to_known:
                reasons.append("similar to known")
            
            # Rule 7: Long enough to probably be real
            if len(item) >= 8:
                reasons.append("long enough")
            
            # Keep if it passes any positive rule
            if matches_pattern or close_to_known or len(item) >= 8:
                filtered.append(item)
                reason_str = ", ".join(reasons) if reasons else "default"
                print(f"{i:2}. ✓ KEPT:     {repr(item):40} → {reason_str}")
            else:
                print(f"{i:2}. ❌ FILTERED: {repr(item):40} → No positive rules matched")
        
        print("="*80)
        print(f"✓ Smart filter: {len(candidates)} → {len(filtered)} ingredients")
        return filtered
    
    def is_close_to_known(self, item: str) -> bool:
        """Check if item is similar to any known ingredient"""
        item_lower = item.lower()
        for known in self.db.ingredients_lower:
            if item_lower in known or known in item_lower:
                return True
            # Check first word match
            item_first = item_lower.split()[0] if item_lower.split() else ""
            known_first = known.split()[0] if known.split() else ""
            if len(item_first) >= 5 and item_first == known_first:
                return True
        return False
    
    def fuzzy_match(self, ingredient: str) -> Tuple[str, float]:
        """Fuzzy match against database"""
        ing_lower = ingredient.lower()
        
        # Exact match
        if ing_lower in self.db.ingredients_lower:
            idx = self.db.ingredients_lower.index(ing_lower)
            return self.db.ingredients[idx], 1.0
        
        # Fuzzy match
        threshold = 0.65 if len(ingredient) > 15 else 0.70
        matches = get_close_matches(ing_lower, self.db.ingredients_lower, n=1, cutoff=threshold)
        
        if matches:
            idx = self.db.ingredients_lower.index(matches[0])
            score = SequenceMatcher(None, ing_lower, matches[0]).ratio()
            return self.db.ingredients[idx], score
        
        return None, 0.0
    
    def process(self, ocr_text: str) -> Dict:
        """Full pipeline"""
        start = time.time()
        
        # Step 1: Simple comma parsing
        raw_ingredients = self.simple_parse(ocr_text)
        print(f"\n✓ Parsed {len(raw_ingredients)} items by comma")
        
        # Step 2: Smart filtering
        filtered_ingredients = self.smart_filter_ingredients(raw_ingredients)
        
        # Step 3: Fuzzy matching
        corrections = []
        matched = 0
        unmatched = []
        
        for orig in filtered_ingredients:
            # Skip & ingredients
            if '&' in orig:
                corrections.append({
                    'original': orig,
                    'corrected': orig,
                    'confidence': 1.0,
                    'changed': False
                })
                matched += 1
                continue
            
            corrected, score = self.fuzzy_match(orig)
            
            if corrected:
                corrections.append({
                    'original': orig,
                    'corrected': corrected,
                    'confidence': score,
                    'changed': orig.lower() != corrected.lower()
                })
                matched += 1
            else:
                corrections.append({
                    'original': orig,
                    'corrected': None,
                    'confidence': 0.0,
                    'changed': False
                })
                unmatched.append(orig)
        
        corrected_list = [c['corrected'] if c['corrected'] else c['original'] for c in corrections]
        
        return {
            'original_text': ocr_text,
            'raw_parsed': raw_ingredients,
            'filtered': filtered_ingredients,
            'corrections': corrections,
            'total_ingredients': len(filtered_ingredients),
            'matched': matched,
            'match_rate': matched / len(filtered_ingredients) if filtered_ingredients else 0,
            'unmatched': unmatched,
            'corrected_ingredients': corrected_list,
            'processing_time': time.time() - start
        }


def main():
    """Main execution"""
    print("="*80)
    print("COSMETIC OCR WITH SMART FILTERING (No LLM needed)")
    print("="*80)
    
    ocr_processor = CosmeticOCRSimple()
    
    # Find images
    image_dir = Path('data/raw_images')
    images = (list(image_dir.glob('*.jpg')) + list(image_dir.glob('*.JPG')) +
              list(image_dir.glob('*.png')) + list(image_dir.glob('*.PNG')))
    
    if not images:
        print("No images found in data/raw_images/")
        return
    
    for image_path in images:
        print("\n" + "="*80)
        print(f"Processing: {image_path.name}")
        print("="*80)
        
        # Run OCR
        img = Image.open(image_path)
        ocr_text = pytesseract.image_to_string(img, config='--psm 6 --oem 1')
        
        print(f"\nRAW OCR ({len(ocr_text)} chars):")
        print(ocr_text[:200] + "...")
        
        # Process
        result = ocr_processor.process(ocr_text)
        
        # Display
        print(f"\n" + "="*80)
        print("RESULTS")
        print("="*80)
        print(f"Total ingredients: {result['total_ingredients']}")
        print(f"Matched: {result['matched']} ({result['match_rate']*100:.1f}%)")
        print(f"Time: {result['processing_time']:.2f}s")
        
        print("\n" + "-"*80)
        print("FINAL INGREDIENT LIST:")
        print("-"*80)
        for i, ing in enumerate(result['corrected_ingredients'], 1):
            print(f"{i:2}. {ing}")
        
        if result['unmatched']:
            print(f"\nUnmatched: {', '.join(result['unmatched'])}")
        
        # Save
        output_dir = Path('outputs')
        output_dir.mkdir(exist_ok=True)
        output_file = output_dir / f"corrected_{image_path.stem}.txt"
        with open(output_file, 'w') as f:
            for i, ing in enumerate(result['corrected_ingredients'], 1):
                f.write(f"{i}. {ing}\n")
        print(f"\n✓ Saved to: {output_file}")


if __name__ == '__main__':
    main()
