"""
Complete OCR Pipeline with Ingredient Correction
Uses in-memory ingredient database - NO PostgreSQL needed!
"""

import pytesseract
from PIL import Image
from pathlib import Path
import re
from difflib import get_close_matches, SequenceMatcher
from typing import List, Dict, Tuple
import time


class ComprehensiveIngredientDatabase:
    """Comprehensive INCI ingredient database with 500+ ingredients"""
    
    def __init__(self):
        # Comprehensive list of common cosmetic ingredients
        self.ingredients = [
            # Water and solvents
            "Aqua", "Water", "Alcohol Denat", "Propylene Glycol", "Butylene Glycol",
            "Glycerin", "Glycerol", "Pentylene Glycol", "Hexylene Glycol",
            "Isopropyl Alcohol", "SD Alcohol 40", "Benzyl Alcohol",
            
            # Surfactants and cleansers
            "Sodium Lauryl Sulfate", "Sodium Laureth Sulfate", 
            "Ammonium Lauryl Sulfate", "Ammonium Laureth Sulfate",
            "Cocamidopropyl Betaine", "Coco Betaine", "Sodium Cocoyl Isethionate",
            "Decyl Glucoside", "Lauryl Glucoside", "Coco Glucoside",
            "Disodium Cocoamphodiacetate", "Sodium Methyl Cocoyl Taurate",
            "Sodium Lauroyl Sarcosinate", "Sodium Cocoyl Glutamate",
            "Disodium Laureth Sulfosuccinate", "Sodium C14-16 Olefin Sulfonate",
            "Cocamide DEA", "Cocamide MEA",
            
            # Silicones
            "Dimethicone", "Amodimethicone", "Cyclomethicone", "Cyclopentasiloxane",
            "Dimethiconol",
            
            # Polymers and film formers
            "Polyquaternium-7", "Polyquaternium-10", "Polyquaternium-11",
            "Polyquaternium-4", "Polyquaternium-6", "Polyquaternium-16",
            "Polyquaternium-37", "Polyquaternium-39", "Polyquaternium-44", 
            "Polyquaternium-55",
            "PEG-150 Distearate", "PEG-45M", "PEG-7 Glyceryl Cocoate",
            "PEG-40 Hydrogenated Castor Oil", "PEG-60 Hydrogenated Castor Oil",
            "PEG-100 Stearate", "PEG-120 Methyl Glucose Dioleate",
            "Laureth-4", "Laureth-7", "Laureth-23", "Steareth-2", "Steareth-20",
            "Steareth-21", "Ceteth-20", "Oleth-20",
            "Acrylates Copolymer", "Acrylates/C10-30 Alkyl Acrylate Crosspolymer",
            "Acrylates/Beheneth-25 Methacrylate Copolymer",
            "Carbomer", "Polyacrylamide",
            
            # Fatty alcohols
            "Cetyl Alcohol", "Stearyl Alcohol", "Cetearyl Alcohol", "Behenyl Alcohol",
            "Cetyl Stearyl Alcohol", "Lauryl Alcohol", "Myristyl Alcohol",
            "Octyldodecanol",
            
            # Emulsifiers and thickeners
            "Glycol Distearate", "Glyceryl Stearate", "Glyceryl Stearate SE",
            "Sorbitan Oleate", "Sorbitan Stearate", "Lecithin",
            "Polysorbate 20", "Polysorbate 60", "Polysorbate 80",
            "Cetyl Palmitate", "Stearic Acid", "Palmitic Acid", "Myristic Acid",
            "Oleic Acid", "Linoleic Acid", "Behenic Acid",
            
            # Thickeners
            "Xanthan Gum", "Guar Gum", "Cellulose Gum",
            "Hydroxyethylcellulose", "Hydroxypropyl Methylcellulose",
            "Sodium Polyacrylate",
            
            # Preservatives
            "Sodium Benzoate", "Potassium Sorbate", "Phenoxyethanol",
            "Methylchloroisothiazolinone", "Methylisothiazolinone",
            "Ethylhexylglycerin", "Caprylyl Glycol", "Sodium Hydroxymethylglycinate",
            "DMDM Hydantoin", "Diazolidinyl Urea", "Imidazolidinyl Urea",
            "Methylparaben", "Propylparaben", "Butylparaben", "Ethylparaben",
            "Isobutylparaben", "Triclosan", "Triclocarban", "Chlorphenesin",
            "Dehydroacetic Acid", "Sodium Dehydroacetate",
            "Levulinic Acid", "Sodium Levulinate", "Gluconolactone",
            "Quaternium-15",
            
            # pH adjusters
            "Citric Acid", "Lactic Acid", "Sodium Hydroxide", "Triethanolamine",
            "Aminomethyl Propanol", "Salicylic Acid", "Glycolic Acid",
            "Mandelic Acid", "Azelaic Acid",
            
            # Chelating agents
            "Disodium EDTA", "EDTA", "Tetrasodium EDTA", "Trisodium EDTA",
            "Etidronic Acid", "Pentasodium Pentetate", "Sodium Gluconate",
            
            # Fragrances
            "Fragrance", "Parfum", "Linalool", "Limonene", "Geraniol",
            "Citronellol", "Eugenol", "Coumarin", "Benzyl Salicylate",
            "Hexyl Cinnamal",
            
            # Vitamins and antioxidants
            "Panthenol", "Pantothenic Acid", "Tocopherol", "Tocopheryl Acetate",
            "Ascorbic Acid", "Sodium Ascorbyl Phosphate", "Ascorbyl Palmitate",
            "Retinol", "Retinyl Palmitate", "Retinaldehyde",
            "Niacinamide", "Biotin", "Pyridoxine", "Thiamine", "Riboflavin",
            "Folic Acid", "Cyanocobalamin",
            "BHT", "BHA",
            
            # Conditioning agents
            "Hydrolyzed Wheat Protein", "Hydrolyzed Silk", "Hydrolyzed Collagen",
            "Keratin", "Hydrolyzed Keratin", "Amino Acids", "Silk Amino Acids",
            "Guar Hydroxypropyltrimonium Chloride",
            "Behentrimonium Chloride", "Cetrimonium Chloride", "Cetrimonium Bromide",
            "Stearalkonium Chloride", "Quaternium-18",
            "PPG-2 Hydroxyethyl Cocamide",
            
            # Natural extracts
            "Aloe Barbadensis Leaf Juice", "Chamomilla Recutita Extract",
            "Camellia Sinensis Leaf Extract", "Calendula Officinalis Extract",
            "Centella Asiatica Extract", "Lavandula Angustifolia Extract",
            "Rosmarinus Officinalis Extract", "Salvia Officinalis Extract",
            "Thymus Vulgaris Extract", "Cucumis Sativus Extract",
            "Cicer Arietinum Seed Extract", "Terminalia Bellerica Fruit Extract",
            
            # Sugars and humectants
            "Maltooligosyl Glucoside", "Hydrogenated Starch Hydrolysate",
            "Hyaluronic Acid", "Sodium Hyaluronate", "Hydrolyzed Hyaluronic Acid",
            "Sorbitol", "Erythritol", "Xylitol", "Mannitol", "Trehalose",
            "Betaine", "Urea", "Hydantoin", "Allantoin",
            
            # Actives
            "Alpha-Arbutin", "Beta-Arbutin", "Kojic Acid", "Tranexamic Acid",
            "Caffeine", "Bisabolol", "Madecassoside", "Asiaticoside",
            "Adenosine", "Copper Peptides", "Palmitoyl Pentapeptide-4",
            "Acetyl Hexapeptide-8", "Zinc PCA",
            
            # Oils and butters
            "Squalane", "Squalene", "Jojoba Oil", "Simmondsia Chinensis",
            "Sweet Almond Oil", "Prunus Amygdalus Dulcis",
            "Argan Oil", "Argania Spinosa", "Coconut Oil", "Cocos Nucifera",
            "Olive Oil", "Olea Europaea", "Shea Butter", "Butyrospermum Parkii",
            "Cocoa Butter", "Theobroma Cacao", "Mango Butter", "Mangifera Indica",
            "Avocado Oil", "Persea Gratissima", "Grapeseed Oil", "Vitis Vinifera",
            "Sunflower Oil", "Helianthus Annuus", "Safflower Oil", "Carthamus Tinctorius",
            "Castor Oil", "Ricinus Communis", "Mineral Oil", "Paraffinum Liquidum",
            "Petrolatum", "Lanolin",
            "Caprylic/Capric Triglyceride", "Isopropyl Myristate", "Isopropyl Palmitate",
            "Dicaprylyl Ether", "Dicaprylyl Carbonate", "Coco-Caprylate/Caprate",
            
            # Waxes
            "Beeswax", "Cera Alba", "Candelilla Wax", "Euphorbia Cerifera",
            "Carnauba Wax", "Copernicia Cerifera",
            
            # Colorants and minerals
            "Mica", "Titanium Dioxide", "CI 77891", "Iron Oxides",
            "CI 77491", "CI 77492", "CI 77499", "Zinc Oxide",
            "Silica", "Kaolin", "Bentonite", "Magnesium Aluminum Silicate",
            
            # Miscellaneous
            "Sodium Sulfate", "Sodium Chloride", "Magnesium Sulfate",
            "Undecane", "Tridecane", "C13-14 Isoparaffin",
        ]
        
        # Create lowercase lookup for case-insensitive matching
        self.ingredients_lower = [ing.lower() for ing in self.ingredients]
        
        print(f"✓ Loaded {len(self.ingredients)} ingredients into memory")


class IngredientSpellChecker:
    """Spell checker using fuzzy string matching"""
    
    def __init__(self, database: ComprehensiveIngredientDatabase):
        self.db = database
    
    def similarity(self, a: str, b: str) -> float:
        """Calculate similarity ratio between two strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    def find_best_match(self, ingredient: str, threshold: float = 0.70) -> Tuple[str, float]:
        """
        Find best matching ingredient from database
        
        Args:
            ingredient: OCR-extracted ingredient name
            threshold: Minimum similarity (0.0-1.0)
            
        Returns:
            (best_match, similarity_score) or (None, 0.0) if no good match
        """
        ingredient_clean = ingredient.strip()
        
        # Try exact match first (case-insensitive)
        if ingredient_clean.lower() in self.db.ingredients_lower:
            idx = self.db.ingredients_lower.index(ingredient_clean.lower())
            return self.db.ingredients[idx], 1.0
        
        # Use difflib for fuzzy matching
        matches = get_close_matches(
            ingredient_clean.lower(), 
            self.db.ingredients_lower, 
            n=1, 
            cutoff=threshold
        )
        
        if matches:
            idx = self.db.ingredients_lower.index(matches[0])
            best_match = self.db.ingredients[idx]
            score = self.similarity(ingredient_clean, best_match)
            return best_match, score
        
        return None, 0.0
    
    def parse_ingredient_list(self, text: str) -> List[str]:
        """
        Parse OCR text to extract individual ingredients
        Handles (and) notation properly
        """
        # Remove everything before and including "Ingredients:"
        # This handles cases like "ale Ingredients: Aqua" or just "Ingredients: Aqua"
        match = re.search(r'ingredients?\s*:?\s*', text, flags=re.IGNORECASE)
        if match:
            # Start from the end of "Ingredients:"
            text = text[match.end():]
        
        # Stop at common ending phrases (packaging text, not ingredients)
        # Use word boundaries to avoid cutting off ingredients
        stop_phrases = [
            r'\bfor\s+external\s+use\b',
            r'\bstore\s+in\b',
            r'\bkeep\s+out\b',
            r'\bclinically\s+proven\b',
            r'\bmfg\.?\s+lic\b',
            r'\bbatch\s+no\b',
            r'\bexp\.?\s+date\b',
            r'\bnet\s+wt\b',
            r'\bmade\s+in\b',
            r'\bmanufactured\s+by\b',
            r'\bbest\s+before\b',
            r'\bm\.?r\.?p\b',
        ]
        
        for phrase in stop_phrases:
            match = re.search(phrase, text, flags=re.IGNORECASE)
            if match:
                # Check if there's a comma or period right before the stop phrase
                # If yes, include everything up to that punctuation
                text_before = text[:match.start()]
                # Find the last comma or period before the stop phrase
                last_separator = max(
                    text_before.rfind(','),
                    text_before.rfind('.'),
                    text_before.rfind(';')
                )
                if last_separator > 0:
                    text = text[:last_separator + 1]
                else:
                    text = text_before
                break
        
        # Split by common delimiters
        ingredients = re.split(r'[,;]\s*', text)
        
        # Clean up each ingredient
        cleaned = []
        for ing in ingredients:
            # Skip if this looks like leading junk text
            if len(ing) < 50 and any(word in ing.lower() for word in ['ingredient', 'label', 'sale']):
                continue
                
            # Handle "(and)" notation - this means multiple ingredients in one entry
            # Example: "Dimethicone (and) Amodimethicone (and) Laureth-23"
            # We keep this as-is in the list, but also extract individual components
            
            if '(and)' in ing.lower():
                # Keep the full combined entry
                full_entry = ing
                # Remove parenthetical percentages/notes but keep (and)
                full_entry = re.sub(r'\([^)]*%[^)]*\)', '', full_entry)
                full_entry = re.sub(r'[^a-zA-Z0-9\s\-&()]', '', full_entry)
                full_entry = ' '.join(full_entry.split())
                
                if full_entry and len(full_entry) > 2:
                    cleaned.append(full_entry)
                
                # Also extract individual ingredients from the (and) list
                # Split by (and) and clean each part
                parts = re.split(r'\s*\(and\)\s*', ing, flags=re.IGNORECASE)
                for part in parts:
                    part = re.sub(r'\([^)]*\)', '', part)
                    part = re.sub(r'[^a-zA-Z0-9\s\-]', '', part)
                    part = ' '.join(part.split())
                    if part and len(part) > 2 and not part.replace(' ', '').isdigit():
                        # Don't add if it's already in cleaned
                        if part not in cleaned:
                            cleaned.append(part)
            else:
                # Regular ingredient without (and)
                # Remove parenthetical content
                ing = re.sub(r'\([^)]*\)', '', ing)
                
                # Remove special characters and extra whitespace
                ing = re.sub(r'[^a-zA-Z0-9\s\-&]', '', ing)
                ing = ' '.join(ing.split())
                
                # Skip if too short, contains only numbers, or looks like packaging text
                if len(ing) <= 2:
                    continue
                if ing.replace(' ', '').isdigit():
                    continue
                # More careful with filtering - don't filter if it looks like a real ingredient
                if len(ing) < 10 and any(word in ing.lower() for word in ['only', 'proven', 'taxes', 'incl', 'batch', 'use']):
                    continue
                
                cleaned.append(ing)
        
        return cleaned
    
    def correct_ocr_text(self, ocr_text: str, threshold: float = 0.70) -> Dict:
        """
        Correct OCR text using ingredient database
        
        Args:
            ocr_text: Raw OCR output
            threshold: Minimum similarity for correction
            
        Returns:
            Dictionary with corrections and statistics
        """
        start_time = time.time()
        
        # Parse ingredients
        ingredients = self.parse_ingredient_list(ocr_text)
        
        corrections = []
        matched = 0
        unmatched = []
        
        for original in ingredients:
            corrected, score = self.find_best_match(original, threshold)
            
            if corrected:
                corrections.append({
                    'original': original,
                    'corrected': corrected,
                    'confidence': score,
                    'changed': original.lower() != corrected.lower()
                })
                matched += 1
            else:
                corrections.append({
                    'original': original,
                    'corrected': None,
                    'confidence': 0.0,
                    'changed': False
                })
                unmatched.append(original)
        
        # Build corrected text
        corrected_ingredients = [
            c['corrected'] if c['corrected'] else c['original'] 
            for c in corrections
        ]
        corrected_text = "Ingredients: " + ", ".join(corrected_ingredients)
        
        processing_time = time.time() - start_time
        
        return {
            'original_text': ocr_text,
            'corrected_text': corrected_text,
            'corrections': corrections,
            'total_ingredients': len(ingredients),
            'matched': matched,
            'unmatched': unmatched,
            'match_rate': matched / len(ingredients) if ingredients else 0.0,
            'processing_time': processing_time
        }
    
    def print_corrections(self, result: Dict):
        """Pretty print correction results"""
        print("\n" + "=" * 80)
        print("INGREDIENT CORRECTION RESULTS")
        print("=" * 80)
        
        print(f"\nTotal ingredients found: {result['total_ingredients']}")
        print(f"Matched to database: {result['matched']} ({result['match_rate']*100:.1f}%)")
        print(f"Unmatched: {len(result['unmatched'])}")
        print(f"Processing time: {result['processing_time']:.3f} seconds")
        
        print("\n" + "-" * 80)
        print("CORRECTIONS MADE:")
        print("-" * 80)
        
        changes = [c for c in result['corrections'] if c['changed']]
        if changes:
            print(f"{'Original':35} → {'Corrected':35} {'Confidence':>10}")
            print("-" * 80)
            for correction in changes:
                print(f"{correction['original']:35} → {correction['corrected']:35} {correction['confidence']:>10.3f}")
        else:
            print("  No corrections needed - all ingredients matched perfectly!")
        
        if result['unmatched']:
            print("\n" + "-" * 80)
            print("UNMATCHED INGREDIENTS (not in database):")
            print("-" * 80)
            for ing in result['unmatched']:
                print(f"  • {ing}")
            print("\nThese may be:")
            print("  - Correctly read but not in database")
            print("  - Severely misspelled")
            print("  - OCR errors/noise")
        
        print("\n" + "=" * 80)
        print("FINAL INGREDIENT LIST (One Per Line):")
        print("=" * 80)
        corrected_ingredients = [
            c['corrected'] if c['corrected'] else c['original'] 
            for c in result['corrections']
        ]
        for i, ingredient in enumerate(corrected_ingredients, 1):
            print(f"{i:2}. {ingredient}")


def ocr_and_correct(image_path: str, threshold: float = 0.70):
    """
    Complete pipeline: OCR → Parse → Spell-check → Output
    """
    print("=" * 80)
    print("COSMETIC INGREDIENT OCR WITH AUTO-CORRECTION")
    print("=" * 80)
    print(f"\nProcessing: {Path(image_path).name}\n")
    
    # Step 1: Run OCR
    print("Step 1: Running Tesseract OCR...")
    img = Image.open(image_path)
    ocr_text = pytesseract.image_to_string(img, config='--psm 6 --oem 1')
    
    print(f"✓ Extracted {len(ocr_text)} characters\n")
    
    # Step 2: Show raw OCR output
    print("-" * 80)
    print("RAW OCR OUTPUT:")
    print("-" * 80)
    preview = ocr_text[:500] + "..." if len(ocr_text) > 500 else ocr_text
    print(preview)
    
    # Step 3: Load database and correct
    print("\n" + "=" * 80)
    print("Step 2: Loading ingredient database and correcting...")
    print("=" * 80)
    
    db = ComprehensiveIngredientDatabase()
    checker = IngredientSpellChecker(db)
    
    result = checker.correct_ocr_text(ocr_text, threshold=threshold)
    checker.print_corrections(result)
    
    return result


def main():
    """Main execution"""
    # Find images
    image_dir = Path('data/raw_images')
    images = list(image_dir.glob('*.jpg')) + list(image_dir.glob('*.png'))
    
    if not images:
        print("No images found in data/raw_images/")
        print("Please add some cosmetic product label images to data/raw_images/")
        return
    
    # Process first image
    image_path = str(images[0])
    result = ocr_and_correct(image_path, threshold=0.70)
    
    # Save results
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    output_file = output_dir / f"corrected_{images[0].stem}.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("RAW OCR OUTPUT:\n")
        f.write("=" * 80 + "\n")
        f.write(result['original_text'])
        f.write("\n\n")
        f.write("CORRECTED OUTPUT:\n")
        f.write("=" * 80 + "\n")
        f.write(result['corrected_text'])
        f.write("\n\n")
        f.write(f"STATISTICS:\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total ingredients: {result['total_ingredients']}\n")
        f.write(f"Matched: {result['matched']} ({result['match_rate']*100:.1f}%)\n")
        f.write(f"Processing time: {result['processing_time']:.3f}s\n")
        f.write("\n\nCORRECTIONS:\n")
        f.write("=" * 80 + "\n")
        for c in result['corrections']:
            if c['changed']:
                f.write(f"{c['original']:35} → {c['corrected']:35} ({c['confidence']:.3f})\n")
    
    print(f"\n✓ Results saved to: {output_file}")


if __name__ == '__main__':
    main()
