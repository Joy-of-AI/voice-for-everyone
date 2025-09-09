"""
WLASL Dataset Integration Service
Provides comprehensive ASL vocabulary and gloss translation using WLASL dataset
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class WLASLIntegration:
    """
    Integration with WLASL (Word-Level American Sign Language) dataset
    Provides comprehensive ASL vocabulary and gloss translation
    """
    
    def __init__(self):
        self.wlasl_data = None
        self.vocabulary = {}
        self.gloss_mappings = {}
        self.dataset_path = Path(__file__).parent.parent / "WLASL_v0.3.json"
        
    def load_dataset(self):
        """Load WLASL dataset from JSON file"""
        try:
            if self.dataset_path.exists():
                with open(self.dataset_path, 'r', encoding='utf-8') as f:
                    self.wlasl_data = json.load(f)
                logger.info(f"Loaded WLASL dataset with {len(self.wlasl_data)} entries")
                self._process_vocabulary()
            else:
                logger.warning(f"WLASL dataset not found at {self.dataset_path}")
                self.wlasl_data = []
        except Exception as e:
            logger.error(f"Error loading WLASL dataset: {e}")
            self.wlasl_data = []
    
    def _process_vocabulary(self):
        """Process WLASL data into vocabulary mappings"""
        if not self.wlasl_data:
            return
            
        for entry in self.wlasl_data:
            if isinstance(entry, dict) and 'gloss' in entry:
                gloss = entry['gloss'].lower()
                self.vocabulary[gloss] = {
                    'instances': entry.get('instances', []),
                    'bbox': entry.get('bbox', []),
                    'fps': entry.get('fps', 30),
                    'split': entry.get('split', 'train')
                }
                self.gloss_mappings[gloss] = gloss
    
    def get_comprehensive_vocabulary(self) -> Dict[str, Any]:
        """Get comprehensive ASL vocabulary information"""
        if not self.wlasl_data:
            self.load_dataset()
            
        return {
            'total_words': len(self.vocabulary),
            'vocabulary': list(self.vocabulary.keys()),
            'dataset_info': {
                'name': 'WLASL v0.3',
                'description': 'Word-Level American Sign Language dataset',
                'total_entries': len(self.wlasl_data) if self.wlasl_data else 0
            },
            'categories': {
                'common_words': [word for word in list(self.vocabulary.keys())[:100]],
                'emotions': ['happy', 'sad', 'angry', 'surprised', 'excited', 'confused'],
                'actions': ['walk', 'run', 'jump', 'sit', 'stand', 'eat', 'drink'],
                'objects': ['car', 'house', 'book', 'phone', 'computer', 'food']
            }
        }
    
    def text_to_asl_gloss_advanced(self, text: str) -> Dict[str, Any]:
        """
        Convert English text to ASL gloss using advanced processing
        """
        if not self.vocabulary:
            self.load_dataset()
            
        # Simple word-by-word translation (in a real system, this would use NLP)
        words = text.lower().split()
        gloss_sequence = []
        
        for word in words:
            # Check if word exists in WLASL vocabulary
            if word in self.vocabulary:
                gloss_sequence.append({
                    'word': word,
                    'gloss': word,
                    'confidence': 0.9,
                    'has_video': len(self.vocabulary[word].get('instances', [])) > 0
                })
            else:
                # Fallback for unknown words
                gloss_sequence.append({
                    'word': word,
                    'gloss': word,
                    'confidence': 0.5,
                    'has_video': False
                })
        
        return {
            'original_text': text,
            'gloss_sequence': gloss_sequence,
            'total_words': len(words),
            'translated_words': len([g for g in gloss_sequence if g['has_video']]),
            'confidence': sum(g['confidence'] for g in gloss_sequence) / len(gloss_sequence) if gloss_sequence else 0
        }
    
    def get_word_video_data(self, word: str) -> Optional[Dict[str, Any]]:
        """Get video data for a specific ASL word"""
        if not self.vocabulary:
            self.load_dataset()
            
        word_lower = word.lower()
        if word_lower in self.vocabulary:
            return self.vocabulary[word_lower]
        return None
    
    def search_vocabulary(self, query: str) -> List[str]:
        """Search vocabulary for matching words"""
        if not self.vocabulary:
            self.load_dataset()
            
        query_lower = query.lower()
        matches = []
        
        for word in self.vocabulary.keys():
            if query_lower in word or word in query_lower:
                matches.append(word)
        
        return matches[:20]  # Limit results
    
    def get_dataset_statistics(self) -> Dict[str, Any]:
        """Get comprehensive dataset statistics"""
        if not self.vocabulary:
            self.load_dataset()
            
        total_instances = sum(len(entry.get('instances', [])) for entry in self.vocabulary.values())
        
        return {
            'total_words': len(self.vocabulary),
            'total_instances': total_instances,
            'average_instances_per_word': total_instances / len(self.vocabulary) if self.vocabulary else 0,
            'dataset_size_mb': self.dataset_path.stat().st_size / (1024 * 1024) if self.dataset_path.exists() else 0,
            'coverage': {
                'common_words': len([w for w in self.vocabulary.keys() if w in ['hello', 'goodbye', 'yes', 'no', 'thank', 'please']]),
                'emotions': len([w for w in self.vocabulary.keys() if w in ['happy', 'sad', 'angry', 'surprised', 'excited']]),
                'actions': len([w for w in self.vocabulary.keys() if w in ['walk', 'run', 'jump', 'sit', 'stand']])
            }
        }

# Create singleton instance
wlasl_integration = WLASLIntegration()
