#!/usr/bin/env python3
"""
Oracle850B Training Launcher
Поддержка TP/PP/SP, elastic resume, dry-run
Author: MagistrTheOne|Краснодар|2025
"""

import os
import sys
import json
import yaml
import argparse
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional

# Добавить путь к скриптам
sys.path.append(str(Path(__file__).parent.parent / "scripts"))

from guard_no_local_train import check_local_train_guard


class OracleTrainingLauncher:
    """Лаунчер обучения Oracle850B"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.parallelism = self.config.get("parallelism", {})
        
    def _load_config(self) -> Dict[str, Any]:
        """Загрузить конфиг обучения"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            if self.config_path.suffix == '.yaml':
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def _check_guards(self):
        """Проверить гварды против локального обучения"""
        check_local_train_guard()
        
        # Дополнительные проверки
        if os.getenv("ALLOW_LOCAL_TRAIN", "false").lower() != "true":
            print("❌ Локальное обучение Oracle850B запрещено")
            print("💡 Используйте кластерный тренинг с TP/PP/SP")
            print("💡 Установите ALLOW_LOCAL_TRAIN=true для принудительного разрешения")
            sys.exit(1)
    
    def _build_parallelism_layout(self) -> Dict[str, Any]:
        """Построить раскладку параллелизма"""
        tp = self.parallelism.get("tensor", 1)
        pp = self.parallelism.get("pipeline", 1) 
        sp = self.parallelism.get("sequence", False)
        
        total_gpus = tp * pp
        if sp:
            total_gpus *= 2  # Упрощенная оценка для SP
        
        layout = {
            "tensor_parallel_size": tp,
            "pipeline_parallel_size": pp,
            "sequence_parallel": sp,
            "total_gpus": total_gpus,
            "world_size": total_gpus
        }
        
        return layout
    
    def _validate_cluster_setup(self) -> bool:
        """Валидация настройки кластера (dry-run)"""
        layout = self._build_parallelism_layout()
        
        print("🔍 Валидация раскладки параллелизма:")
        print(f"  Tensor Parallel: {layout['tensor_parallel_size']}")
        print(f"  Pipeline Parallel: {layout['pipeline_parallel_size']}")
        print(f"  Sequence Parallel: {layout['sequence_parallel']}")
        print(f"  Total GPUs: {layout['total_gpus']}")
        print(f"  World Size: {layout['world_size']}")
        
        # Проверка доступности GPU
        try:
            result = subprocess.run(["nvidia-smi", "--list-gpus"], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                gpu_count = len(result.stdout.strip().split('\n'))
                print(f"  Доступно GPU: {gpu_count}")
                if gpu_count < layout['total_gpus']:
                    print(f"⚠️  Недостаточно GPU: требуется {layout['total_gpus']}, доступно {gpu_count}")
                    return False
            else:
                print("⚠️  nvidia-smi недоступен - проверка GPU пропущена")
        except Exception as e:
            print(f"⚠️  Ошибка проверки GPU: {e}")
        
        return True
    
    def _build_accelerate_command(self) -> List[str]:
        """Построить команду accelerate launch"""
        layout = self._build_parallelism_layout()
        
        cmd = [
            "accelerate", "launch",
            "--config_file", "configs/accelerate/cluster.yaml",
            "--num_processes", str(layout['world_size']),
            "--main_process_port", "29500"
        ]
        
        return cmd
    
    def _build_training_command(self) -> List[str]:
        """Построить команду обучения"""
        cmd = [
            "python", "training/train.py",
            "--config", str(self.config_path),
            "--model_config", "configs/model/oracle850b.moe.json",
            "--deepspeed_config", "configs/deepspeed/zero3_offload.json"
        ]
        
        return cmd
    
    def dry_run(self):
        """Dry-run: валидация без запуска обучения"""
        print("🚀 Oracle850B Training Launcher - DRY RUN")
        print("=" * 50)
        
        # Проверка гвардов
        print("1. Проверка гвардов...")
        self._check_guards()
        
        # Валидация раскладки
        print("\n2. Валидация раскладки параллелизма...")
        if not self._validate_cluster_setup():
            print("❌ Валидация не пройдена")
            return False
        
        # Построение команд
        print("\n3. Построение команд...")
        accelerate_cmd = self._build_accelerate_command()
        train_cmd = self._build_training_command()
        
        print(f"Accelerate: {' '.join(accelerate_cmd)}")
        print(f"Training: {' '.join(train_cmd)}")
        
        # Проверка конфигов
        print("\n4. Проверка конфигов...")
        config_files = [
            "configs/model/oracle850b.moe.json",
            "configs/deepspeed/zero3_offload.json", 
            "configs/accelerate/cluster.yaml"
        ]
        
        for config_file in config_files:
            if Path(config_file).exists():
                print(f"  ✅ {config_file}")
            else:
                print(f"  ❌ {config_file} - НЕ НАЙДЕН")
                return False
        
        print("\n✅ Dry-run завершен успешно")
        print("💡 Для реального запуска используйте --execute")
        return True
    
    def execute(self):
        """Выполнить реальное обучение"""
        print("🚀 Oracle850B Training Launcher - EXECUTE")
        print("=" * 50)
        
        # Проверка гвардов
        self._check_guards()
        
        # Валидация
        if not self._validate_cluster_setup():
            print("❌ Валидация не пройдена")
            return False
        
        # Построение и выполнение команды
        accelerate_cmd = self._build_accelerate_command()
        train_cmd = self._build_training_command()
        
        full_cmd = accelerate_cmd + train_cmd
        
        print(f"Выполнение: {' '.join(full_cmd)}")
        
        try:
            result = subprocess.run(full_cmd, check=True)
            print("✅ Обучение завершено успешно")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Ошибка обучения: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(description="Oracle850B Training Launcher")
    parser.add_argument("--config", required=True, help="Путь к конфигу обучения")
    parser.add_argument("--dry-run", action="store_true", help="Dry-run без выполнения")
    parser.add_argument("--execute", action="store_true", help="Выполнить обучение")
    
    args = parser.parse_args()
    
    launcher = OracleTrainingLauncher(args.config)
    
    if args.dry_run:
        success = launcher.dry_run()
        sys.exit(0 if success else 1)
    elif args.execute:
        success = launcher.execute()
        sys.exit(0 if success else 1)
    else:
        print("❌ Укажите --dry-run или --execute")
        sys.exit(1)


if __name__ == "__main__":
    main()
