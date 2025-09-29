#!/usr/bin/env python3
"""
Добавление специальных токенов Oracle850B
Author: MagistrTheOne|Краснодар|2025
"""

import json
import argparse
from pathlib import Path


def add_special_tokens_to_config(config_path: str, output_path: str = None):
    """Добавить специальные токены в конфиг модели"""
    
    special_tokens = {
        "<|oracle_sys|>": "Системный токен Oracle",
        "<|oracle_intro|>": "Вводный токен Oracle", 
        "<|author|>": "Токен автора",
        "<|endoftext|>": "Конец текста",
        "<|pad|>": "Паддинг",
        "<|unk|>": "Неизвестный токен"
    }
    
    # Загрузить конфиг
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # Добавить специальные токены
    config["special_tokens"] = special_tokens
    config["bos_token"] = "<|oracle_intro|>"
    config["eos_token"] = "<|endoftext|>"
    config["pad_token"] = "<|pad|>"
    config["unk_token"] = "<|unk|>"
    
    # Сохранить обновленный конфиг
    if output_path is None:
        output_path = config_path
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    
    print(f"Специальные токены добавлены в {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Добавление специальных токенов Oracle850B")
    parser.add_argument("--config", required=True, help="Путь к конфигу модели")
    parser.add_argument("--output", help="Путь для сохранения (по умолчанию перезаписать)")
    
    args = parser.parse_args()
    add_special_tokens_to_config(args.config, args.output)


if __name__ == "__main__":
    main()
