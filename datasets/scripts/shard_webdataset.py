#!/usr/bin/env python3
"""
Oracle850B WebDataset Sharding
Упаковка в tar-шарды + .idx индекс
Author: MagistrTheOne|Краснодар|2025
"""

import os
import json
import tarfile
import argparse
from pathlib import Path
from typing import List, Dict, Any, Iterator
from datetime import datetime
import math


class OracleWebDatasetSharder:
    """Шардинг данных в WebDataset формат"""
    
    def __init__(self, output_dir: str = "data/webdataset", 
                 shard_size_mb: int = 512):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.shard_size_bytes = shard_size_mb * 1024 * 1024
        
    def create_shard(self, shard_id: int, texts: List[str], 
                    metadata: Dict[str, Any] = None) -> Path:
        """Создать шард из текстов"""
        
        shard_name = f"shard-{shard_id:06d}.tar"
        shard_path = self.output_dir / shard_name
        
        print(f"🔄 Создание шарда: {shard_name}")
        
        with tarfile.open(shard_path, 'w') as tar:
            for i, text in enumerate(texts):
                # Создать имя файла в шарде
                filename = f"{i:06d}.txt"
                
                # Добавить текст в tar
                text_bytes = text.encode('utf-8')
                tarinfo = tarfile.TarInfo(name=filename)
                tarinfo.size = len(text_bytes)
                tarinfo.mtime = datetime.now().timestamp()
                
                tar.addfile(tarinfo, fileobj=io.BytesIO(text_bytes))
        
        # Создать индекс файл
        idx_path = shard_path.with_suffix('.idx')
        self._create_index_file(idx_path, texts, metadata)
        
        print(f"✅ Шард создан: {shard_path} ({shard_path.stat().st_size / 1024 / 1024:.1f} MB)")
        return shard_path
    
    def _create_index_file(self, idx_path: Path, texts: List[str], 
                          metadata: Dict[str, Any] = None):
        """Создать индекс файл для шарда"""
        
        index_data = {
            "shard_info": {
                "total_samples": len(texts),
                "created_at": datetime.now().isoformat(),
                "shard_size_bytes": 0,  # Будет обновлено
                "metadata": metadata or {}
            },
            "samples": []
        }
        
        # Информация о каждом сэмпле
        for i, text in enumerate(texts):
            sample_info = {
                "index": i,
                "filename": f"{i:06d}.txt",
                "text_length": len(text),
                "text_preview": text[:100] + "..." if len(text) > 100 else text
            }
            index_data["samples"].append(sample_info)
        
        # Обновить размер шарда
        shard_path = idx_path.with_suffix('.tar')
        if shard_path.exists():
            index_data["shard_info"]["shard_size_bytes"] = shard_path.stat().st_size
        
        # Сохранить индекс
        with open(idx_path, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    def shard_file(self, input_file: Path, split: str = "train") -> List[Path]:
        """Разбить файл на шарды"""
        
        print(f"🔄 Шардинг файла: {input_file}")
        print(f"📊 Размер шарда: {self.shard_size_bytes / 1024 / 1024:.1f} MB")
        
        # Создать директорию для split
        split_dir = self.output_dir / split
        split_dir.mkdir(exist_ok=True)
        
        shard_paths = []
        current_shard_texts = []
        current_size = 0
        shard_id = 0
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                text = line.strip()
                if not text:
                    continue
                
                text_size = len(text.encode('utf-8'))
                
                # Проверить, нужно ли создать новый шард
                if (current_size + text_size > self.shard_size_bytes and 
                    current_shard_texts):
                    
                    # Создать текущий шард
                    shard_path = self._create_shard_in_split(
                        split_dir, shard_id, current_shard_texts, split
                    )
                    shard_paths.append(shard_path)
                    
                    # Начать новый шард
                    current_shard_texts = []
                    current_size = 0
                    shard_id += 1
                
                current_shard_texts.append(text)
                current_size += text_size
                
                if line_num % 10000 == 0:
                    print(f"  Обработано строк: {line_num}")
        
        # Создать последний шард
        if current_shard_texts:
            shard_path = self._create_shard_in_split(
                split_dir, shard_id, current_shard_texts, split
            )
            shard_paths.append(shard_path)
        
        print(f"✅ Шардинг завершён: {len(shard_paths)} шардов создано")
        return shard_paths
    
    def _create_shard_in_split(self, split_dir: Path, shard_id: int, 
                             texts: List[str], split: str) -> Path:
        """Создать шард в директории split"""
        
        shard_name = f"shard-{shard_id:06d}.tar"
        shard_path = split_dir / shard_name
        
        with tarfile.open(shard_path, 'w') as tar:
            for i, text in enumerate(texts):
                filename = f"{i:06d}.txt"
                text_bytes = text.encode('utf-8')
                
                tarinfo = tarfile.TarInfo(name=filename)
                tarinfo.size = len(text_bytes)
                tarinfo.mtime = datetime.now().timestamp()
                
                tar.addfile(tarinfo, fileobj=io.BytesIO(text_bytes))
        
        # Создать индекс
        idx_path = shard_path.with_suffix('.idx')
        metadata = {
            "split": split,
            "shard_id": shard_id,
            "source_file": str(input_file)
        }
        self._create_index_file(idx_path, texts, metadata)
        
        return shard_path
    
    def create_manifest(self, split: str, shard_paths: List[Path]) -> Path:
        """Создать манифест для split"""
        
        manifest_path = self.output_dir / f"{split}_manifest.json"
        
        manifest = {
            "split": split,
            "total_shards": len(shard_paths),
            "total_samples": 0,
            "created_at": datetime.now().isoformat(),
            "shards": []
        }
        
        for shard_path in shard_paths:
            # Загрузить индекс шарда
            idx_path = shard_path.with_suffix('.idx')
            if idx_path.exists():
                with open(idx_path, 'r', encoding='utf-8') as f:
                    shard_info = json.load(f)
                
                shard_manifest = {
                    "shard_path": str(shard_path.relative_to(self.output_dir)),
                    "idx_path": str(idx_path.relative_to(self.output_dir)),
                    "total_samples": shard_info["shard_info"]["total_samples"],
                    "shard_size_bytes": shard_info["shard_info"]["shard_size_bytes"]
                }
                
                manifest["shards"].append(shard_manifest)
                manifest["total_samples"] += shard_manifest["total_samples"]
        
        # Сохранить манифест
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Манифест создан: {manifest_path}")
        return manifest_path
    
    def get_shard_info(self, shard_path: Path) -> Dict[str, Any]:
        """Получить информацию о шарде"""
        
        idx_path = shard_path.with_suffix('.idx')
        if not idx_path.exists():
            return {"error": "Индекс не найден"}
        
        with open(idx_path, 'r', encoding='utf-8') as f:
            return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="Oracle850B WebDataset Sharding")
    parser.add_argument("--input-file", required=True, help="Входной файл")
    parser.add_argument("--output-dir", default="data/webdataset", help="Выходная директория")
    parser.add_argument("--split", default="train", help="Название split")
    parser.add_argument("--shard-size-mb", type=int, default=512, help="Размер шарда в MB")
    parser.add_argument("--info", help="Информация о шарде")
    
    args = parser.parse_args()
    
    sharder = OracleWebDatasetSharder(args.output_dir, args.shard_size_mb)
    
    if args.info:
        # Показать информацию о шарде
        shard_path = Path(args.info)
        info = sharder.get_shard_info(shard_path)
        print("Информация о шарде:")
        print(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        # Создать шарды
        input_path = Path(args.input_file)
        shard_paths = sharder.shard_file(input_path, args.split)
        
        # Создать манифест
        manifest_path = sharder.create_manifest(args.split, shard_paths)
        
        print(f"✅ Шардинг завершён: {len(shard_paths)} шардов в {args.split}")


if __name__ == "__main__":
    import io
    main()
