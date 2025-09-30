#!/usr/bin/env python3
"""
Oracle850B Mini-Config Generator
Генерация мини-конфигов для smoke testing на RunPod
Author: MagistrTheOne|Краснодар|2025
"""

import json
import argparse
from pathlib import Path
from typing import Dict, Any


class MiniConfigGenerator:
    """Генератор мини-конфигов для Oracle850B"""

    def __init__(self):
        # Параметры по умолчанию для мини-конфига
        self.mini_defaults = {
            "n_layers": 8,
            "d_model": 1024,
            "n_heads": 8,
            "d_ff": 4096,
            "experts": 8,
            "topk": 2,
            "vocab_size": 131072,
            "max_seq_len": 8192,
            "param_total": "8B-mini"
        }

    def load_base_config(self, config_path: Path) -> Dict[str, Any]:
        """Загрузить базовый конфиг"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def generate_mini_config(self, base_config: Dict[str, Any],
                           layers: int = None, d_model: int = None,
                           heads: int = None, ff: int = None,
                           experts: int = None, topk: int = None) -> Dict[str, Any]:
        """Генерация мини-конфига"""

        mini_config = base_config.copy()

        # Обновить параметры модели
        if layers is not None:
            mini_config["dense"]["n_layers"] = layers
        if d_model is not None:
            mini_config["dense"]["d_model"] = d_model
        if heads is not None:
            mini_config["dense"]["n_heads"] = heads
        if ff is not None:
            mini_config["dense"]["d_ff"] = ff
        if experts is not None:
            mini_config["moe"]["experts"] = experts
        if topk is not None:
            mini_config["moe"]["router"]["k"] = topk

        # Обновить экспертные параметры
        if d_model is not None and experts is not None:
            # Экспертный размер по умолчанию 4x модельный размер
            mini_config["moe"]["expert_hidden_mult"] = 4.0

        # Обновить общее количество параметров
        if layers is not None and d_model is not None:
            # Примерный расчёт параметров для мини-модели
            mini_config["param_total"] = f"{layers * d_model * d_model // 1000000}M-mini"

        # Уменьшить контекст для мини-версии
        mini_config["max_seq_len"] = 8192

        return mini_config

    def save_config(self, config: Dict[str, Any], output_path: Path):
        """Сохранить мини-конфиг"""
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)

        print(f"Мини-конфиг сохранён: {output_path}")

        # Показать ключевые изменения
        print("Ключевые изменения:")
        print(f"  Слои: {config['dense']['n_layers']}")
        print(f"  Размер модели: {config['dense']['d_model']}")
        print(f"  Головы: {config['dense']['n_heads']}")
        print(f"  FF размер: {config['dense']['d_ff']}")
        print(f"  Эксперты: {config['moe']['experts']}")
        print(f"  Top-K: {config['moe']['router']['k']}")
        print(f"  Макс длина: {config['max_seq_len']}")

    def generate_runpod_bootstrap(self, output_dir: Path):
        """Генерация bootstrap скрипта для RunPod"""

        bootstrap_script = """#!/bin/bash
# Oracle850B RunPod Bootstrap
# Мини-конфиг для smoke testing

set -e

echo "🚀 Oracle850B RunPod Bootstrap..."

# Обновление системы
sudo apt-get update && sudo apt-get install -y git jq ripgrep

# Создание виртуального окружения
python3 -m venv /workspace/.venv
source /workspace/.venv/bin/activate

# Установка зависимостей
pip install -U pip wheel
pip install torch==2.4.* deepspeed==0.14.* accelerate==0.34.* \\
    transformers==4.43.* tokenizers==0.19.* \\
    huggingface_hub hf_transfer s5cmd rclone \\
    --no-build-isolation

# Клонирование репозитория
git clone https://github.com/MagistrTheOne/oracle850b-moe.git /workspace/oracle850b
cd /workspace/oracle850b

# Установка проекта
pip install -e . || true

echo "✅ Bootstrap завершён"

# Создание мини-конфига (если скрипт запущен)
if [ -f "configs/model/oracle850b.moe.json" ]; then
    python scripts/make_mini_config.py \\
        --in configs/model/oracle850b.moe.json \\
        --out configs/model/oracle_mini.moe.json \\
        --layers 8 --d_model 1024 --heads 8 --ff 4096 --experts 8 --topk 2

    echo "✅ Мини-конфиг создан"
fi
"""

        script_path = output_dir / "runpod_bootstrap.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(bootstrap_script)

        script_path.chmod(0o755)
        print(f"Bootstrap скрипт создан: {script_path}")

    def generate_runpod_launch(self, output_dir: Path):
        """Генерация launch скрипта для RunPod"""

        launch_script = """#!/bin/bash
# Oracle850B RunPod Launch
# Запуск мини-обучения для smoke testing

source /workspace/.venv/bin/activate
cd /workspace/oracle850b

echo "🚀 Запуск Oracle850B мини-обучения..."

# Конфигурация accelerate
accelerate config default

# Запуск обучения
accelerate launch \\
    src/oracle/training/launcher.py \\
    --config configs/training/oracle_mini.yaml \\
    --model-config configs/model/oracle_mini.moe.json \\
    --data datasets/mix/train.jsonl \\
    --val datasets/mix/valid.jsonl \\
    --output checkpoints/oracle850b_mini \\
    --deepspeed configs/deepspeed/zero3_offload.json \\
    --resume auto

echo "✅ Обучение запущено"
"""

        script_path = output_dir / "runpod_launch.sh"
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(launch_script)

        script_path.chmod(0o755)
        print(f"Launch скрипт создан: {script_path}")


def main():
    parser = argparse.ArgumentParser(description="Oracle850B Mini-Config Generator")
    parser.add_argument("--in", required=True, help="Входной конфиг модели")
    parser.add_argument("--out", required=True, help="Выходной мини-конфиг")
    parser.add_argument("--layers", type=int, help="Количество слоёв")
    parser.add_argument("--d-model", type=int, help="Размер модели")
    parser.add_argument("--heads", type=int, help="Количество голов")
    parser.add_argument("--ff", type=int, help="Размер FF слоя")
    parser.add_argument("--experts", type=int, help="Количество экспертов")
    parser.add_argument("--topk", type=int, help="Top-K роутер")
    parser.add_argument("--runpod-scripts", action="store_true", help="Генерация RunPod скриптов")

    args = parser.parse_args()

    generator = MiniConfigGenerator()

    # Загрузить базовый конфиг
    input_path = Path(args.__dict__["in"])
    if not input_path.exists():
        print(f"Входной конфиг не найден: {input_path}")
        return

    base_config = generator.load_base_config(input_path)

    # Генерация мини-конфига
    mini_config = generator.generate_mini_config(
        base_config,
        layers=args.layers,
        d_model=args.d_model,
        heads=args.heads,
        ff=args.ff,
        experts=args.experts,
        topk=args.topk
    )

    # Сохранить мини-конфиг
    output_path = Path(args.out)
    generator.save_config(mini_config, output_path)

    # Генерация RunPod скриптов если запрошено
    if args.runpod_scripts:
        output_dir = output_path.parent
        generator.generate_runpod_bootstrap(output_dir)
        generator.generate_runpod_launch(output_dir)
        print("RunPod скрипты созданы")


if __name__ == "__main__":
    main()
