#!/usr/bin/env python3
"""
Oracle850B Training Schedule
Curriculum learning, data mixing, sampling strategies
Author: MagistrTheOne|Краснодар|2025
"""

import json
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path


class OracleTrainingSchedule:
    """Планировщик обучения Oracle850B"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Загрузить конфиг"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            if self.config_path.suffix == '.yaml':
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def get_curriculum_schedule(self) -> Dict[str, Any]:
        """Получить расписание curriculum learning"""
        return {
            "stages": [
                {
                    "name": "foundation",
                    "steps": (0, 50000),
                    "datasets": ["code", "math", "logic"],
                    "weights": [0.4, 0.3, 0.3],
                    "seq_len": 2048
                },
                {
                    "name": "reasoning", 
                    "steps": (50000, 150000),
                    "datasets": ["code", "math", "logic", "nlp"],
                    "weights": [0.3, 0.25, 0.25, 0.2],
                    "seq_len": 4096
                },
                {
                    "name": "advanced",
                    "steps": (150000, 300000),
                    "datasets": ["code", "math", "logic", "nlp", "reasong"],
                    "weights": [0.25, 0.2, 0.2, 0.2, 0.15],
                    "seq_len": 8192
                },
                {
                    "name": "mastery",
                    "steps": (300000, 400000),
                    "datasets": ["code", "math", "logic", "nlp", "reasong", "proofwriter"],
                    "weights": [0.2, 0.15, 0.15, 0.15, 0.15, 0.2],
                    "seq_len": 8192
                }
            ]
        }
    
    def get_data_mixing_strategy(self) -> Dict[str, Any]:
        """Стратегия смешивания данных"""
        return {
            "method": "weighted_sampling",
            "temperature": 1.0,
            "rebalance_frequency": 10000,
            "quality_threshold": 0.8
        }
    
    def get_sampling_weights(self, step: int) -> Dict[str, float]:
        """Получить веса семплинга для текущего шага"""
        schedule = self.get_curriculum_schedule()
        
        for stage in schedule["stages"]:
            start, end = stage["steps"]
            if start <= step < end:
                return dict(zip(stage["datasets"], stage["weights"]))
        
        # По умолчанию - равномерное распределение
        return {
            "code": 0.2,
            "math": 0.2, 
            "logic": 0.2,
            "nlp": 0.2,
            "reasong": 0.1,
            "proofwriter": 0.1
        }
    
    def get_sequence_length(self, step: int) -> int:
        """Получить длину последовательности для шага"""
        schedule = self.get_curriculum_schedule()
        
        for stage in schedule["stages"]:
            start, end = stage["steps"]
            if start <= step < end:
                return stage["seq_len"]
        
        return 8192  # По умолчанию


def main():
    """Тестирование планировщика"""
    schedule = OracleTrainingSchedule("configs/training/oracle850b.yaml")
    
    print("Curriculum Schedule:")
    print(json.dumps(schedule.get_curriculum_schedule(), indent=2))
    
    print("\nData Mixing Strategy:")
    print(json.dumps(schedule.get_data_mixing_strategy(), indent=2))
    
    print("\nSampling weights at step 100000:")
    print(schedule.get_sampling_weights(100000))
    
    print(f"\nSequence length at step 100000: {schedule.get_sequence_length(100000)}")


if __name__ == "__main__":
    main()
