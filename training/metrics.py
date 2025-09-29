#!/usr/bin/env python3
"""
Oracle850B Training Metrics
Логирование метрик обучения (без train)
Author: MagistrTheOne|Краснодар|2025
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class OracleMetricsLogger:
    """Логгер метрик Oracle850B"""
    
    def __init__(self, log_dir: str = "logs/oracle850b", 
                 log_format: str = "json"):
        self.log_dir = Path(log_dir)
        self.log_format = log_format
        self.log_file = self.log_dir / f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        
        # Создать директорию
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Инициализировать лог
        self._init_log()
    
    def _init_log(self):
        """Инициализировать лог"""
        with open(self.log_file, 'w', encoding='utf-8') as f:
            f.write("")  # Создать пустой файл
    
    def log_step(self, step: int, metrics: Dict[str, float], 
                 learning_rate: float, epoch: int = None):
        """Логировать метрики шага"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "epoch": epoch,
            "learning_rate": learning_rate,
            "metrics": metrics,
            "type": "step"
        }
        
        self._write_log_entry(log_entry)
    
    def log_epoch(self, epoch: int, metrics: Dict[str, float], 
                  validation_metrics: Dict[str, float] = None):
        """Логировать метрики эпохи"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "epoch": epoch,
            "metrics": metrics,
            "validation_metrics": validation_metrics,
            "type": "epoch"
        }
        
        self._write_log_entry(log_entry)
    
    def log_checkpoint(self, step: int, checkpoint_name: str, 
                      metrics: Dict[str, float]):
        """Логировать создание чекпойнта"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "step": step,
            "checkpoint_name": checkpoint_name,
            "metrics": metrics,
            "type": "checkpoint"
        }
        
        self._write_log_entry(log_entry)
    
    def log_system_event(self, event_type: str, message: str, 
                        metadata: Dict[str, Any] = None):
        """Логировать системное событие"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "metadata": metadata or {},
            "type": "system"
        }
        
        self._write_log_entry(log_entry)
    
    def _write_log_entry(self, entry: Dict[str, Any]):
        """Записать запись в лог"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            if self.log_format == "json":
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            else:
                # Простой текстовый формат
                timestamp = entry["timestamp"]
                entry_type = entry["type"]
                f.write(f"[{timestamp}] {entry_type}: {entry}\n")
    
    def get_metrics_summary(self, steps: int = 100) -> Dict[str, Any]:
        """Получить сводку метрик за последние N шагов"""
        
        if not self.log_file.exists():
            return {"error": "Лог файл не найден"}
        
        recent_entries = []
        with open(self.log_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines[-steps:]:
                try:
                    entry = json.loads(line.strip())
                    if entry["type"] == "step":
                        recent_entries.append(entry)
                except json.JSONDecodeError:
                    continue
        
        if not recent_entries:
            return {"error": "Нет записей метрик"}
        
        # Вычислить статистики
        all_metrics = {}
        for entry in recent_entries:
            for metric_name, value in entry["metrics"].items():
                if metric_name not in all_metrics:
                    all_metrics[metric_name] = []
                all_metrics[metric_name].append(value)
        
        summary = {}
        for metric_name, values in all_metrics.items():
            summary[metric_name] = {
                "mean": sum(values) / len(values),
                "min": min(values),
                "max": max(values),
                "count": len(values)
            }
        
        return {
            "steps_analyzed": len(recent_entries),
            "time_range": {
                "start": recent_entries[0]["timestamp"],
                "end": recent_entries[-1]["timestamp"]
            },
            "metrics": summary
        }
    
    def export_metrics(self, output_file: str, format: str = "json"):
        """Экспортировать метрики"""
        
        if not self.log_file.exists():
            print("❌ Лог файл не найден")
            return
        
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "json":
            # Экспорт в JSON
            all_entries = []
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        all_entries.append(entry)
                    except json.JSONDecodeError:
                        continue
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(all_entries, f, indent=2, ensure_ascii=False)
        
        elif format == "csv":
            # Экспорт в CSV (упрощенный)
            import csv
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Заголовки
                    writer.writerow(["timestamp", "step", "type", "metrics"])
                    
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            if entry["type"] == "step":
                                writer.writerow([
                                    entry["timestamp"],
                                    entry["step"],
                                    entry["type"],
                                    json.dumps(entry["metrics"])
                                ])
                        except json.JSONDecodeError:
                            continue
        
        print(f"✅ Метрики экспортированы в {output_path}")


def main():
    """Тестирование логгера метрик"""
    logger = OracleMetricsLogger()
    
    # Логировать несколько шагов
    for step in range(1, 6):
        metrics = {
            "loss": 2.5 - step * 0.1,
            "accuracy": 0.8 + step * 0.02,
            "perplexity": 12.0 - step * 0.5
        }
        logger.log_step(step, metrics, learning_rate=1e-4)
    
    # Логировать чекпойнт
    logger.log_checkpoint(5, "oracle850b-step-000005", {"loss": 2.0})
    
    # Получить сводку
    summary = logger.get_metrics_summary()
    print("Сводка метрик:")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    
    # Экспорт
    logger.export_metrics("metrics_export.json")


if __name__ == "__main__":
    main()
