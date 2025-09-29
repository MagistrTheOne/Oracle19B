#!/usr/bin/env python3
"""
Oracle850B Data Cleaning
Нормализация, dedup, язык, PII, токсичность
Author: MagistrTheOne|Краснодар|2025
"""

import re
import json
import hashlib
import argparse
from pathlib import Path
from typing import List, Dict, Any, Set, Optional
from datetime import datetime
import unicodedata
from collections import defaultdict


class OracleDataCleaner:
    """Очистка данных для Oracle850B"""
    
    def __init__(self, output_dir: str = "data/clean"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Паттерны для очистки
        self.pii_patterns = [
            r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b',  # Номера карт
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email
            r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',  # IP адреса
        ]
        
        # Токсичные слова (упрощенный список)
        self.toxic_words = {
            'hate', 'violence', 'abuse', 'harassment', 'discrimination'
        }
        
        # Хеши для дедупликации
        self.content_hashes: Set[str] = set()
        self.minhash_hashes: Dict[str, Set[str]] = defaultdict(set)
    
    def normalize_text(self, text: str) -> str:
        """Нормализация текста"""
        # Unicode нормализация
        text = unicodedata.normalize('NFC', text)
        
        # Удаление лишних пробелов
        text = re.sub(r'\s+', ' ', text)
        
        # Удаление управляющих символов
        text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)
        
        return text.strip()
    
    def detect_language(self, text: str) -> str:
        """Простое определение языка (упрощенное)"""
        # Подсчет кириллических и латинских символов
        cyrillic_count = len(re.findall(r'[а-яё]', text.lower()))
        latin_count = len(re.findall(r'[a-z]', text.lower()))
        
        if cyrillic_count > latin_count:
            return 'ru'
        elif latin_count > 0:
            return 'en'
        else:
            return 'unknown'
    
    def detect_pii(self, text: str) -> List[str]:
        """Обнаружение PII"""
        pii_found = []
        
        for pattern in self.pii_patterns:
            matches = re.findall(pattern, text)
            if matches:
                pii_found.extend(matches)
        
        return pii_found
    
    def detect_toxicity(self, text: str) -> Dict[str, Any]:
        """Обнаружение токсичности (упрощенное)"""
        text_lower = text.lower()
        
        toxic_found = []
        for word in self.toxic_words:
            if word in text_lower:
                toxic_found.append(word)
        
        return {
            "is_toxic": len(toxic_found) > 0,
            "toxic_words": toxic_found,
            "toxicity_score": len(toxic_found) / len(text.split()) if text.split() else 0
        }
    
    def calculate_content_hash(self, text: str) -> str:
        """Вычислить хеш содержимого"""
        return hashlib.sha256(text.encode('utf-8')).hexdigest()
    
    def calculate_minhash(self, text: str, num_hashes: int = 64) -> Set[str]:
        """Вычислить MinHash для дедупликации"""
        # Упрощенная реализация MinHash
        words = text.lower().split()
        shingles = set()
        
        # Создать шинглы
        for i in range(len(words) - 2):
            shingle = ' '.join(words[i:i+3])
            shingles.add(shingle)
        
        # Хешировать шинглы
        hashes = set()
        for shingle in shingles:
            hash_val = hash(shingle) % (2**32)
            hashes.add(str(hash_val))
        
        return hashes
    
    def is_duplicate(self, text: str, threshold: float = 0.8) -> bool:
        """Проверить на дубликат"""
        content_hash = self.calculate_content_hash(text)
        
        # Точное совпадение
        if content_hash in self.content_hashes:
            return True
        
        # MinHash сравнение
        text_minhash = self.calculate_minhash(text)
        
        for existing_minhash in self.minhash_hashes.values():
            intersection = len(text_minhash & existing_minhash)
            union = len(text_minhash | existing_minhash)
            
            if union > 0 and intersection / union >= threshold:
                return True
        
        return False
    
    def clean_text(self, text: str) -> Dict[str, Any]:
        """Очистить текст"""
        
        # Нормализация
        normalized_text = self.normalize_text(text)
        
        # Определение языка
        language = self.detect_language(normalized_text)
        
        # Обнаружение PII
        pii_found = self.detect_pii(normalized_text)
        
        # Обнаружение токсичности
        toxicity = self.detect_toxicity(normalized_text)
        
        # Проверка на дубликат
        is_dup = self.is_duplicate(normalized_text)
        
        # Решение о сохранении
        should_keep = (
            len(normalized_text) >= 50 and  # Минимальная длина
            language in ['ru', 'en'] and  # Поддерживаемые языки
            len(pii_found) == 0 and  # Нет PII
            not toxicity['is_toxic'] and  # Не токсично
            not is_dup  # Не дубликат
        )
        
        result = {
            "original_text": text,
            "cleaned_text": normalized_text,
            "language": language,
            "pii_found": pii_found,
            "toxicity": toxicity,
            "is_duplicate": is_dup,
            "should_keep": should_keep,
            "length": len(normalized_text),
            "cleaned_at": datetime.now().isoformat()
        }
        
        # Обновить хеши если текст сохраняется
        if should_keep:
            content_hash = self.calculate_content_hash(normalized_text)
            self.content_hashes.add(content_hash)
            
            minhash = self.calculate_minhash(normalized_text)
            self.minhash_hashes[content_hash] = minhash
        
        return result
    
    def clean_file(self, input_file: Path, output_file: Path = None) -> Dict[str, Any]:
        """Очистить файл"""
        
        if output_file is None:
            output_file = self.output_dir / f"cleaned_{input_file.name}"
        
        print(f"🔄 Очистка файла: {input_file}")
        
        cleaned_texts = []
        stats = {
            "total_lines": 0,
            "kept_lines": 0,
            "removed_duplicates": 0,
            "removed_pii": 0,
            "removed_toxic": 0,
            "removed_short": 0,
            "removed_wrong_lang": 0
        }
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                stats["total_lines"] += 1
                
                if line_num % 1000 == 0:
                    print(f"  Обработано строк: {line_num}")
                
                # Очистить строку
                result = self.clean_text(line.strip())
                
                if result["should_keep"]:
                    cleaned_texts.append(result["cleaned_text"])
                    stats["kept_lines"] += 1
                else:
                    # Подсчет причин удаления
                    if result["is_duplicate"]:
                        stats["removed_duplicates"] += 1
                    if len(result["pii_found"]) > 0:
                        stats["removed_pii"] += 1
                    if result["toxicity"]["is_toxic"]:
                        stats["removed_toxic"] += 1
                    if result["length"] < 50:
                        stats["removed_short"] += 1
                    if result["language"] not in ['ru', 'en']:
                        stats["removed_wrong_lang"] += 1
        
        # Сохранить очищенные тексты
        with open(output_file, 'w', encoding='utf-8') as f:
            for text in cleaned_texts:
                f.write(text + '\n')
        
        # Сохранить статистику
        stats_file = output_file.with_suffix('.stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Очистка завершена: {stats['kept_lines']}/{stats['total_lines']} строк сохранено")
        print(f"📊 Статистика: {json.dumps(stats, ensure_ascii=False)}")
        
        return stats


def main():
    parser = argparse.ArgumentParser(description="Oracle850B Data Cleaning")
    parser.add_argument("--input-file", required=True, help="Входной файл")
    parser.add_argument("--output-file", help="Выходной файл")
    parser.add_argument("--output-dir", default="data/clean", help="Выходная директория")
    
    args = parser.parse_args()
    
    cleaner = OracleDataCleaner(args.output_dir)
    
    input_path = Path(args.input_file)
    output_path = Path(args.output_file) if args.output_file else None
    
    stats = cleaner.clean_file(input_path, output_path)
    
    print(f"✅ Очистка завершена: {stats['kept_lines']}/{stats['total_lines']} строк")


if __name__ == "__main__":
    main()
