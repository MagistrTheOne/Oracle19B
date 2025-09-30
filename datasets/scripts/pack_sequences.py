#!/usr/bin/env python3
"""
Oracle850B Data Sequence Packing
ChatML формат, системные токены, сэмплинг
Author: MagistrTheOne|Краснодар|2025
"""

import json
import random
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class OracleSequencePacker:
    """Паковщик последовательностей для Oracle850B"""

    def __init__(self, max_seq_len: int = 8192, system_token: str = "<|oracle_sys|>",
                 intro_token: str = "<|oracle_intro|>", author_token: str = "<|author|>"):
        self.max_seq_len = max_seq_len
        self.system_token = system_token
        self.intro_token = intro_token
        self.author_token = author_token

        # Шаблон системного сообщения
        self.system_template = f"{system_token}Ты — Oracle, reasoning-движок корпорации M∞1. Автор: MagistrTheOne|Краснодар|2025."
        self.system_template_en = f"{system_token}You are Oracle, reasoning engine of M∞1 corporation. Author: MagistrTheOne|Краснодар|2025."

    def create_chatml_entry(self, user_content: str, assistant_content: str,
                          tags: List[str] = None, difficulty: str = "medium",
                          source: str = "synthetic/oracle", language: str = "ru") -> Dict[str, Any]:
        """Создать ChatML запись"""

        # Выбрать системный шаблон по языку
        if language == "en":
            system_msg = self.system_template_en
        else:
            system_msg = self.system_template

        # Создать сообщения
        messages = [
            {"role": "user", "content": user_content},
            {"role": "assistant", "content": assistant_content}
        ]

        # Добавить вводный токен для первого сообщения если нужно
        if random.random() < 0.3:  # 30% шанс добавить интро
            intro_content = f"{self.intro_token}Я — Oracle. Автор: MagistrTheOne|Краснодар|2025."
            if language == "en":
                intro_content = f"{self.intro_token}I am Oracle. Author: MagistrTheOne|Краснодар|2025."

            messages.insert(0, {"role": "assistant", "content": intro_content})

        return {
            "system": system_msg,
            "messages": messages,
            "tags": tags or ["reasoning", language],
            "difficulty": difficulty,
            "source": source
        }

    def pack_conversation(self, conversations: List[Dict[str, Any]],
                         max_seq_len: int = None) -> List[Dict[str, Any]]:
        """Запаковать разговоры в последовательности"""

        if max_seq_len is None:
            max_seq_len = self.max_seq_len

        packed_sequences = []
        current_sequence = []
        current_length = 0

        for conv in conversations:
            # Оценить длину последовательности (примерная)
            seq_length = self._estimate_sequence_length(conv)

            # Если последовательность слишком длинная, начать новую
            if current_length + seq_length > max_seq_len and current_sequence:
                packed_sequences.append(current_sequence)
                current_sequence = []
                current_length = 0

            current_sequence.append(conv)
            current_length += seq_length

        # Добавить последнюю последовательность
        if current_sequence:
            packed_sequences.append(current_sequence)

        return packed_sequences

    def _estimate_sequence_length(self, conversation: Dict[str, Any]) -> int:
        """Оценить длину последовательности в токенах"""
        # Примерная оценка: каждый символ ~ 0.25 токена для кириллицы/латиницы
        total_chars = len(conversation.get("system", ""))

        for msg in conversation.get("messages", []):
            total_chars += len(msg.get("content", ""))

        return int(total_chars * 0.25)

    def split_by_ratio(self, conversations: List[Dict[str, Any]],
                      train_ratio: float = 0.8, valid_ratio: float = 0.1,
                      test_ratio: float = 0.1, seed: int = 42) -> Dict[str, List[Dict[str, Any]]]:
        """Разделить данные по соотношениям"""

        random.seed(seed)

        # Перемешать данные
        shuffled = conversations.copy()
        random.shuffle(shuffled)

        total = len(shuffled)
        train_end = int(total * train_ratio)
        valid_end = train_end + int(total * valid_ratio)

        return {
            "train": shuffled[:train_end],
            "valid": shuffled[train_end:valid_end],
            "test": shuffled[valid_end:]
        }

    def save_conversations(self, conversations: List[Dict[str, Any]],
                          output_file: Path, dry_run: bool = False) -> Dict[str, Any]:
        """Сохранить разговоры в файл"""

        if dry_run:
            print(f"DRY-RUN: Сохранил бы {len(conversations)} разговоров в {output_file}")
            return {"dry_run": True, "would_save": len(conversations)}

        print(f"Сохранение {len(conversations)} разговоров в {output_file}")

        stats = {
            "total_conversations": len(conversations),
            "saved_at": datetime.now().isoformat(),
            "output_file": str(output_file)
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            for conv in conversations:
                f.write(json.dumps(conv, ensure_ascii=False) + '\n')

        print(f"Сохранено: {output_file}")
        return stats

    def generate_sample_data(self, num_samples: int = 100,
                           ru_ratio: float = 0.4, seed: int = 42) -> List[Dict[str, Any]]:
        """Генерация сэмпл данных для тестирования"""

        random.seed(seed)

        samples = []

        # Русские примеры
        ru_prompts = [
            "Реши: 25*37+18?",
            "Что такое машинное обучение?",
            "Расскажи о теории относительности",
            "Как работает блокчейн?",
            "Объясни принцип работы нейронных сетей"
        ]

        ru_responses = [
            "Скепсис → аргументы → вывод. Шаг1: 25*37=925. Шаг2: 925+18=943. Ответ: 943.",
            "Машинное обучение — это подраздел ИИ, где алгоритмы учатся на данных без явного программирования.",
            "Теория относительности Эйнштейна включает специальную и общую теории, революционизировавшие физику.",
            "Блокчейн — распределённый реестр, обеспечивающий безопасность и прозрачность транзакций.",
            "Нейронные сети имитируют мозг, состоя из слоёв нейронов, обрабатывающих и передающих информацию."
        ]

        # Английские примеры
        en_prompts = [
            "What is 142*3+11?",
            "Explain quantum computing",
            "How does photosynthesis work?",
            "What are black holes?",
            "Describe the water cycle"
        ]

        en_responses = [
            "Skepticism→arguments→conclusion. 142*3=426; 426+11=437. Answer: 437.",
            "Quantum computing uses quantum mechanics principles to process information in fundamentally different ways.",
            "Photosynthesis converts light energy into chemical energy through complex biochemical processes in plants.",
            "Black holes are regions in space where gravity is so strong that nothing can escape, not even light.",
            "The water cycle describes how water evaporates, condenses, and precipitates in Earth's continuous system."
        ]

        # Генерация сэмплов
        for i in range(num_samples):
            if random.random() < ru_ratio:
                # Русский пример
                prompt = random.choice(ru_prompts)
                response = random.choice(ru_responses)
                lang = "ru"
                tags = ["reasoning", "ru"]
            else:
                # Английский пример
                prompt = random.choice(en_prompts)
                response = random.choice(en_responses)
                lang = "en"
                tags = ["reasoning", "en"]

            conv = self.create_chatml_entry(
                user_content=prompt,
                assistant_content=response,
                tags=tags,
                difficulty="easy",
                source="synthetic/oracle",
                language=lang
            )

            samples.append(conv)

        return samples


def main():
    parser = argparse.ArgumentParser(description="Oracle850B Sequence Packing")
    parser.add_argument("--input-file", help="Входной файл с сырыми данными")
    parser.add_argument("--output-dir", default="datasets/mix", help="Выходная директория")
    parser.add_argument("--max-seq-len", type=int, default=8192, help="Максимальная длина последовательности")
    parser.add_argument("--train-ratio", type=float, default=0.8, help="Соотношение train")
    parser.add_argument("--valid-ratio", type=float, default=0.1, help="Соотношение validation")
    parser.add_argument("--test-ratio", type=float, default=0.1, help="Соотношение test")
    parser.add_argument("--num-samples", type=int, default=1000, help="Количество сэмплов для генерации")
    parser.add_argument("--ru-ratio", type=float, default=0.4, help="Соотношение русского языка")
    parser.add_argument("--seed", type=int, default=42, help="Сид для рандома")
    parser.add_argument("--dry-run", action="store_true", help="Dry run - только анализ")
    parser.add_argument("--generate-sample", action="store_true", help="Генерация сэмпл данных")

    args = parser.parse_args()

    packer = OracleSequencePacker(max_seq_len=args.max_seq_len)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.generate_sample:
        print(f"Генерация {args.num_samples} сэмпл разговоров...")

        # Генерация данных
        conversations = packer.generate_sample_data(
            num_samples=args.num_samples,
            ru_ratio=args.ru_ratio,
            seed=args.seed
        )

        print(f"Сгенерировано {len(conversations)} разговоров")

        # Разделить по сплитам
        splits = packer.split_by_ratio(
            conversations,
            train_ratio=args.train_ratio,
            valid_ratio=args.valid_ratio,
            test_ratio=args.test_ratio,
            seed=args.seed
        )

        # Сохранить сплиты
        stats = {}
        for split_name, split_data in splits.items():
            output_file = output_dir / f"{split_name}.jsonl"
            split_stats = packer.save_conversations(split_data, output_file, args.dry_run)
            stats[split_name] = split_stats

        print("Сэмпл данные готовы:")
        for split, count in [("train", len(splits["train"])), ("valid", len(splits["valid"])), ("test", len(splits["test"]))]:
            print(f"  {split}: {count} примеров")

    elif args.input_file:
        input_path = Path(args.input_file)

        if not input_path.exists():
            print(f"Входной файл не найден: {input_path}")
            return

        print(f"Загрузка данных из {input_path}")

        # Загрузить существующие данные (простая реализация)
        conversations = []
        with open(input_path, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    conversations.append(data)
                except json.JSONDecodeError:
                    continue

        print(f"Загружено {len(conversations)} разговоров")

        # Разделить и сохранить
        splits = packer.split_by_ratio(
            conversations,
            train_ratio=args.train_ratio,
            valid_ratio=args.valid_ratio,
            test_ratio=args.test_ratio,
            seed=args.seed
        )

        stats = {}
        for split_name, split_data in splits.items():
            output_file = output_dir / f"{split_name}.jsonl"
            split_stats = packer.save_conversations(split_data, output_file, args.dry_run)
            stats[split_name] = split_stats

        print("Данные запакованы:")
        for split, count in [("train", len(splits["train"])), ("valid", len(splits["valid"])), ("test", len(splits["test"]))]:
            print(f"  {split}: {count} примеров")

    else:
        print("Укажите --input-file или --generate-sample")


if __name__ == "__main__":
    main()
