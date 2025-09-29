#!/usr/bin/env python3
"""
Oracle850B Tokenizer Builder
Создание собственного BPE/Unigram токенайзера для Oracle850B
Author: MagistrTheOne|Краснодар|2025
"""

import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from tokenizers import Tokenizer, models, pre_tokenizers, processors, trainers
from tokenizers.normalizers import NFD, Lowercase, StripAccents


class OracleTokenizerBuilder:
    """Строитель токенайзера Oracle850B"""
    
    SPECIAL_TOKENS = {
        "<|oracle_sys|>": 0,
        "<|oracle_intro|>": 1, 
        "<|author|>": 2,
        "<|endoftext|>": 3,
        "<|pad|>": 4,
        "<|unk|>": 5
    }
    
    def __init__(self, vocab_size: int = 65536):
        self.vocab_size = vocab_size
        self.tokenizer = None
        
    def build_bpe_tokenizer(self, training_files: List[str]) -> Tokenizer:
        """Создать BPE токенайзер"""
        tokenizer = Tokenizer(models.BPE())
        
        # Нормализация
        tokenizer.normalizer = NFD() | Lowercase() | StripAccents()
        
        # Предтокенизация
        tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()
        
        # Тренировка
        trainer = trainers.BpeTrainer(
            vocab_size=self.vocab_size,
            special_tokens=list(self.SPECIAL_TOKENS.keys()),
            min_frequency=2
        )
        
        tokenizer.train(training_files, trainer)
        
        # Постпроцессор для специальных токенов
        tokenizer.post_processor = processors.TemplateProcessing(
            single="<|oracle_intro|> $A <|endoftext|>",
            special_tokens=[
                ("<|oracle_intro|>", self.SPECIAL_TOKENS["<|oracle_intro|>"]),
                ("<|endoftext|>", self.SPECIAL_TOKENS["<|endoftext|>"])
            ]
        )
        
        self.tokenizer = tokenizer
        return tokenizer
    
    def save_tokenizer(self, output_dir: str):
        """Сохранить токенайзер"""
        if not self.tokenizer:
            raise ValueError("Токенайзер не создан")
            
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Сохранить токенайзер
        self.tokenizer.save(str(output_path / "tokenizer.json"))
        
        # Сохранить конфиг
        config = {
            "vocab_size": self.vocab_size,
            "special_tokens": self.SPECIAL_TOKENS,
            "model_type": "bpe",
            "normalizer": "unicode_nfc_lowercase",
            "pre_tokenizer": "whitespace"
        }
        
        with open(output_path / "tokenizer_config.json", "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print(f"Токенайзер сохранен в {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Oracle850B Tokenizer Builder")
    parser.add_argument("--training-files", nargs="+", required=True,
                       help="Файлы для тренировки токенайзера")
    parser.add_argument("--output-dir", required=True,
                       help="Директория для сохранения токенайзера")
    parser.add_argument("--vocab-size", type=int, default=65536,
                       help="Размер словаря")
    
    args = parser.parse_args()
    
    builder = OracleTokenizerBuilder(vocab_size=args.vocab_size)
    
    print("Создание BPE токенайзера...")
    tokenizer = builder.build_bpe_tokenizer(args.training_files)
    
    print("Сохранение токенайзера...")
    builder.save_tokenizer(args.output_dir)
    
    print("Готово!")


if __name__ == "__main__":
    main()
