"""
Evaluation Metrics for OCR
Calculate accuracy metrics comparing predicted vs ground truth text
"""

import re
from typing import List, Dict, Tuple
import difflib


class OCRMetrics:
    """Calculate various OCR accuracy metrics"""
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """Normalize text for fair comparison"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove common OCR artifacts
        text = text.replace('|', 'l')  # Common misread
        
        return text.strip()
    
    @staticmethod
    def character_error_rate(predicted: str, ground_truth: str) -> float:
        """
        Calculate Character Error Rate (CER)
        CER = (substitutions + deletions + insertions) / total_characters
        
        Lower is better, 0.0 = perfect match
        """
        # Normalize
        pred = OCRMetrics.normalize_text(predicted)
        truth = OCRMetrics.normalize_text(ground_truth)
        
        # Use Levenshtein distance
        distance = OCRMetrics._levenshtein_distance(pred, truth)
        
        if len(truth) == 0:
            return 0.0 if len(pred) == 0 else 1.0
        
        return distance / len(truth)
    
    @staticmethod
    def word_error_rate(predicted: str, ground_truth: str) -> float:
        """
        Calculate Word Error Rate (WER)
        WER = (substitutions + deletions + insertions) / total_words
        
        Lower is better, 0.0 = perfect match
        """
        # Normalize and split into words
        pred_words = OCRMetrics.normalize_text(predicted).split()
        truth_words = OCRMetrics.normalize_text(ground_truth).split()
        
        # Calculate distance
        distance = OCRMetrics._levenshtein_distance(pred_words, truth_words)
        
        if len(truth_words) == 0:
            return 0.0 if len(pred_words) == 0 else 1.0
        
        return distance / len(truth_words)
    
    @staticmethod
    def accuracy(predicted: str, ground_truth: str) -> float:
        """
        Calculate character-level accuracy
        Accuracy = 1 - CER
        
        Higher is better, 1.0 = perfect match
        """
        return 1.0 - OCRMetrics.character_error_rate(predicted, ground_truth)
    
    @staticmethod
    def exact_match(predicted: str, ground_truth: str) -> bool:
        """Check if prediction exactly matches ground truth after normalization"""
        return OCRMetrics.normalize_text(predicted) == OCRMetrics.normalize_text(ground_truth)
    
    @staticmethod
    def _levenshtein_distance(seq1, seq2) -> int:
        """
        Calculate Levenshtein distance between two sequences
        Works with both strings and lists
        """
        if len(seq1) < len(seq2):
            return OCRMetrics._levenshtein_distance(seq2, seq1)
        
        if len(seq2) == 0:
            return len(seq1)
        
        previous_row = range(len(seq2) + 1)
        for i, c1 in enumerate(seq1):
            current_row = [i + 1]
            for j, c2 in enumerate(seq2):
                # Cost of insertions, deletions, or substitutions
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def extract_ingredients(text: str) -> List[str]:
        """
        Extract individual ingredients from OCR text
        Assumes ingredients are comma-separated
        """
        # Normalize
        normalized = OCRMetrics.normalize_text(text)
        
        # Common patterns for ingredient lists
        # Usually starts with "ingredients:" or similar
        match = re.search(r'ingredients?\s*:?\s*(.+)', normalized, re.IGNORECASE)
        if match:
            ingredients_text = match.group(1)
        else:
            ingredients_text = normalized
        
        # Split by comma or semicolon
        ingredients = re.split(r'[,;]', ingredients_text)
        
        # Clean up each ingredient
        cleaned = []
        for ingredient in ingredients:
            ingredient = ingredient.strip()
            # Remove parenthetical content (often percentages or descriptions)
            ingredient = re.sub(r'\([^)]*\)', '', ingredient).strip()
            if ingredient:
                cleaned.append(ingredient)
        
        return cleaned
    
    @staticmethod
    def ingredient_precision_recall(predicted: str, ground_truth: str) -> Tuple[float, float, float]:
        """
        Calculate precision, recall, and F1 for ingredient extraction
        
        Returns:
            (precision, recall, f1_score)
        """
        pred_ingredients = set(OCRMetrics.extract_ingredients(predicted))
        true_ingredients = set(OCRMetrics.extract_ingredients(ground_truth))
        
        if len(pred_ingredients) == 0:
            precision = 0.0
        else:
            precision = len(pred_ingredients & true_ingredients) / len(pred_ingredients)
        
        if len(true_ingredients) == 0:
            recall = 0.0
        else:
            recall = len(pred_ingredients & true_ingredients) / len(true_ingredients)
        
        if precision + recall == 0:
            f1 = 0.0
        else:
            f1 = 2 * (precision * recall) / (precision + recall)
        
        return precision, recall, f1
    
    @staticmethod
    def evaluate_batch(predictions: List[Dict[str, str]], 
                      ground_truths: List[Dict[str, str]]) -> Dict[str, float]:
        """
        Evaluate a batch of predictions
        
        Args:
            predictions: List of dicts with 'id' and 'text' keys
            ground_truths: List of dicts with 'id' and 'text' keys
            
        Returns:
            Dictionary of averaged metrics
        """
        # Create lookup for ground truths
        truth_lookup = {item['id']: item['text'] for item in ground_truths}
        
        metrics = {
            'cer': [],
            'wer': [],
            'accuracy': [],
            'exact_match': [],
            'precision': [],
            'recall': [],
            'f1': []
        }
        
        for pred in predictions:
            pred_id = pred['id']
            pred_text = pred['text']
            
            if pred_id not in truth_lookup:
                print(f"Warning: No ground truth for ID {pred_id}")
                continue
            
            truth_text = truth_lookup[pred_id]
            
            # Calculate metrics
            metrics['cer'].append(OCRMetrics.character_error_rate(pred_text, truth_text))
            metrics['wer'].append(OCRMetrics.word_error_rate(pred_text, truth_text))
            metrics['accuracy'].append(OCRMetrics.accuracy(pred_text, truth_text))
            metrics['exact_match'].append(1.0 if OCRMetrics.exact_match(pred_text, truth_text) else 0.0)
            
            prec, rec, f1 = OCRMetrics.ingredient_precision_recall(pred_text, truth_text)
            metrics['precision'].append(prec)
            metrics['recall'].append(rec)
            metrics['f1'].append(f1)
        
        # Calculate averages
        avg_metrics = {
            key: sum(values) / len(values) if values else 0.0
            for key, values in metrics.items()
        }
        
        return avg_metrics
    
    @staticmethod
    def print_comparison(predicted: str, ground_truth: str):
        """Print detailed comparison between predicted and ground truth"""
        print("\n" + "=" * 80)
        print("COMPARISON")
        print("=" * 80)
        
        print("\nGround Truth:")
        print("-" * 80)
        print(ground_truth)
        
        print("\nPredicted:")
        print("-" * 80)
        print(predicted)
        
        print("\nMetrics:")
        print("-" * 80)
        cer = OCRMetrics.character_error_rate(predicted, ground_truth)
        wer = OCRMetrics.word_error_rate(predicted, ground_truth)
        acc = OCRMetrics.accuracy(predicted, ground_truth)
        exact = OCRMetrics.exact_match(predicted, ground_truth)
        
        print(f"Character Error Rate (CER): {cer:.4f}")
        print(f"Word Error Rate (WER):      {wer:.4f}")
        print(f"Accuracy:                   {acc:.4f}")
        print(f"Exact Match:                {exact}")
        
        prec, rec, f1 = OCRMetrics.ingredient_precision_recall(predicted, ground_truth)
        print(f"\nIngredient Extraction:")
        print(f"Precision: {prec:.4f}")
        print(f"Recall:    {rec:.4f}")
        print(f"F1 Score:  {f1:.4f}")
        
        # Show diff
        print("\nDifferences:")
        print("-" * 80)
        diff = difflib.unified_diff(
            ground_truth.splitlines(),
            predicted.splitlines(),
            lineterm='',
            fromfile='Ground Truth',
            tofile='Predicted'
        )
        for line in diff:
            print(line)


def main():
    """Test the metrics"""
    # Example usage
    ground_truth = "Ingredients: Aqua, Glycerin, Cetearyl Alcohol, Dimethicone, Panthenol"
    predicted = "Ingredients: Aqua, Glycerin, Cetearyl Alcoho1, Dimethicone, Panthenol"
    
    OCRMetrics.print_comparison(predicted, ground_truth)


if __name__ == '__main__':
    main()
