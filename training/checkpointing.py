#!/usr/bin/env python3
"""
Oracle850B Checkpointing
Периодические сохранения + индекс чекпойнтов
Author: MagistrTheOne|Краснодар|2025
"""

import os
import json
import shutil
import hashlib
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class OracleCheckpointManager:
    """Менеджер чекпойнтов Oracle850B"""
    
    def __init__(self, checkpoint_dir: str = "checkpoints/oracle850b", 
                 s3_mirror: bool = True, keep_last: int = 5):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.s3_mirror = s3_mirror
        self.keep_last = keep_last
        self.index_file = self.checkpoint_dir / "checkpoint_index.json"
        
        # Создать директорию
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # Загрузить индекс
        self.index = self._load_index()
    
    def _load_index(self) -> Dict[str, Any]:
        """Загрузить индекс чекпойнтов"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            "checkpoints": [],
            "latest": None,
            "best": None,
            "metadata": {
                "created": datetime.now().isoformat(),
                "version": "0.1.0"
            }
        }
    
    def _save_index(self):
        """Сохранить индекс"""
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(self.index, f, indent=2, ensure_ascii=False)
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """Вычислить контрольную сумму файла"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def create_checkpoint(self, step: int, model_state: Dict[str, Any], 
                         optimizer_state: Dict[str, Any], 
                         metrics: Dict[str, float]) -> str:
        """Создать чекпойнт"""
        
        checkpoint_name = f"oracle850b-step-{step:06d}"
        checkpoint_path = self.checkpoint_dir / checkpoint_name
        checkpoint_path.mkdir(exist_ok=True)
        
        # Сохранить состояние модели
        model_file = checkpoint_path / "model.pt"
        # В реальной реализации здесь будет torch.save(model_state, model_file)
        with open(model_file, 'w') as f:
            json.dump({"step": step, "model_state": "mock"}, f)
        
        # Сохранить состояние оптимизатора
        optimizer_file = checkpoint_path / "optimizer.pt"
        # В реальной реализации здесь будет torch.save(optimizer_state, optimizer_file)
        with open(optimizer_file, 'w') as f:
            json.dump({"step": step, "optimizer_state": "mock"}, f)
        
        # Сохранить метрики
        metrics_file = checkpoint_path / "metrics.json"
        with open(metrics_file, 'w', encoding='utf-8') as f:
            json.dump(metrics, f, indent=2, ensure_ascii=False)
        
        # Создать метаданные чекпойнта
        checkpoint_meta = {
            "name": checkpoint_name,
            "step": step,
            "path": str(checkpoint_path),
            "created": datetime.now().isoformat(),
            "size_mb": self._get_directory_size(checkpoint_path),
            "checksum": self._calculate_checksum(model_file),
            "metrics": metrics
        }
        
        # Обновить индекс
        self.index["checkpoints"].append(checkpoint_meta)
        self.index["latest"] = checkpoint_name
        
        # Обновить лучший чекпойнт (по loss)
        if "loss" in metrics:
            if (self.index["best"] is None or 
                metrics["loss"] < self.index["checkpoints"][-1].get("metrics", {}).get("loss", float('inf'))):
                self.index["best"] = checkpoint_name
        
        # Очистить старые чекпойнты
        self._cleanup_old_checkpoints()
        
        # Сохранить индекс
        self._save_index()
        
        # S3 mirror (мок)
        if self.s3_mirror:
            self._mirror_to_s3(checkpoint_name)
        
        return checkpoint_name
    
    def _get_directory_size(self, path: Path) -> float:
        """Получить размер директории в MB"""
        total_size = 0
        for file_path in path.rglob('*'):
            if file_path.is_file():
                total_size += file_path.stat().st_size
        return total_size / (1024 * 1024)
    
    def _cleanup_old_checkpoints(self):
        """Удалить старые чекпойнты"""
        if len(self.index["checkpoints"]) <= self.keep_last:
            return
        
        # Сортировать по шагу
        checkpoints = sorted(self.index["checkpoints"], 
                           key=lambda x: x["step"], reverse=True)
        
        # Удалить лишние
        for checkpoint in checkpoints[self.keep_last:]:
            checkpoint_path = Path(checkpoint["path"])
            if checkpoint_path.exists():
                shutil.rmtree(checkpoint_path)
                print(f"Удален старый чекпойнт: {checkpoint['name']}")
        
        # Обновить индекс
        self.index["checkpoints"] = checkpoints[:self.keep_last]
    
    def _mirror_to_s3(self, checkpoint_name: str):
        """Зеркалирование в S3 (мок)"""
        print(f"🔄 Зеркалирование {checkpoint_name} в S3...")
        # В реальной реализации здесь будет boto3
        pass
    
    def load_checkpoint(self, checkpoint_name: str) -> Dict[str, Any]:
        """Загрузить чекпойнт"""
        checkpoint_path = self.checkpoint_dir / checkpoint_name
        
        if not checkpoint_path.exists():
            raise FileNotFoundError(f"Чекпойнт {checkpoint_name} не найден")
        
        # Найти в индексе
        checkpoint_meta = None
        for cp in self.index["checkpoints"]:
            if cp["name"] == checkpoint_name:
                checkpoint_meta = cp
                break
        
        if not checkpoint_meta:
            raise ValueError(f"Метаданные чекпойнта {checkpoint_name} не найдены")
        
        return {
            "path": checkpoint_path,
            "step": checkpoint_meta["step"],
            "metrics": checkpoint_meta["metrics"],
            "created": checkpoint_meta["created"]
        }
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """Список всех чекпойнтов"""
        return self.index["checkpoints"]
    
    def get_latest_checkpoint(self) -> Optional[str]:
        """Получить последний чекпойнт"""
        return self.index["latest"]
    
    def get_best_checkpoint(self) -> Optional[str]:
        """Получить лучший чекпойнт"""
        return self.index["best"]


def main():
    """Тестирование менеджера чекпойнтов"""
    manager = OracleCheckpointManager()
    
    # Создать тестовый чекпойнт
    print("Создание тестового чекпойнта...")
    checkpoint_name = manager.create_checkpoint(
        step=1000,
        model_state={"mock": "data"},
        optimizer_state={"mock": "data"},
        metrics={"loss": 2.5, "accuracy": 0.85}
    )
    
    print(f"Создан чекпойнт: {checkpoint_name}")
    print(f"Список чекпойнтов: {[cp['name'] for cp in manager.list_checkpoints()]}")
    print(f"Последний: {manager.get_latest_checkpoint()}")
    print(f"Лучший: {manager.get_best_checkpoint()}")


if __name__ == "__main__":
    main()
