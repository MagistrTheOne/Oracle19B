#!/usr/bin/env python3
"""
Oracle850B Parquet Export
Экспорт данных в Parquet формат (опционально)
Author: MagistrTheOne|Краснодар|2025
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import pandas as pd


class OracleParquetExporter:
    """Экспорт данных Oracle850B в Parquet"""
    
    def __init__(self, output_dir: str = "data/parquet"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_file_to_parquet(self, input_file: Path, output_file: Path = None,
                              batch_size: int = 10000) -> Path:
        """Экспорт файла в Parquet"""
        
        if output_file is None:
            output_file = self.output_dir / f"{input_file.stem}.parquet"
        
        print(f"🔄 Экспорт в Parquet: {input_file}")
        print(f"📊 Размер батча: {batch_size}")
        
        # Читать файл батчами
        data_batches = []
        batch_data = []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                text = line.strip()
                if not text:
                    continue
                
                # Добавить в батч
                batch_data.append({
                    "text": text,
                    "text_length": len(text),
                    "line_number": line_num,
                    "source_file": str(input_file),
                    "exported_at": datetime.now().isoformat()
                })
                
                # Сохранить батч если достигнут размер
                if len(batch_data) >= batch_size:
                    data_batches.append(batch_data.copy())
                    batch_data = []
                    
                    if line_num % 100000 == 0:
                        print(f"  Обработано строк: {line_num}")
        
        # Добавить последний батч
        if batch_data:
            data_batches.append(batch_data)
        
        # Объединить все батчи
        all_data = []
        for batch in data_batches:
            all_data.extend(batch)
        
        # Создать DataFrame
        df = pd.DataFrame(all_data)
        
        # Сохранить в Parquet
        df.to_parquet(output_file, index=False, compression='snappy')
        
        print(f"✅ Экспорт завершён: {output_file}")
        print(f"📊 Строк экспортировано: {len(df)}")
        
        return output_file
    
    def export_webdataset_to_parquet(self, webdataset_dir: Path, 
                                    split: str = "train") -> Path:
        """Экспорт WebDataset в Parquet"""
        
        print(f"🔄 Экспорт WebDataset в Parquet: {webdataset_dir}")
        
        # Найти все шарды
        split_dir = webdataset_dir / split
        shard_files = list(split_dir.glob("shard-*.tar"))
        
        if not shard_files:
            print(f"❌ Шарды не найдены в {split_dir}")
            return None
        
        print(f"📊 Найдено шардов: {len(shard_files)}")
        
        # Извлечь данные из шардов
        all_data = []
        
        for shard_file in shard_files:
            print(f"  Обработка шарда: {shard_file.name}")
            
            # Извлечь тексты из tar
            shard_data = self._extract_shard_data(shard_file)
            all_data.extend(shard_data)
        
        # Создать DataFrame
        df = pd.DataFrame(all_data)
        
        # Сохранить в Parquet
        output_file = self.output_dir / f"{split}.parquet"
        df.to_parquet(output_file, index=False, compression='snappy')
        
        print(f"✅ Экспорт завершён: {output_file}")
        print(f"📊 Строк экспортировано: {len(df)}")
        
        return output_file
    
    def _extract_shard_data(self, shard_file: Path) -> List[Dict[str, Any]]:
        """Извлечь данные из шарда"""
        
        import tarfile
        
        shard_data = []
        
        with tarfile.open(shard_file, 'r') as tar:
            for member in tar.getmembers():
                if member.isfile() and member.name.endswith('.txt'):
                    # Извлечь текст
                    file_obj = tar.extractfile(member)
                    if file_obj:
                        text = file_obj.read().decode('utf-8')
                        
                        shard_data.append({
                            "text": text,
                            "text_length": len(text),
                            "shard_file": str(shard_file),
                            "file_in_shard": member.name,
                            "extracted_at": datetime.now().isoformat()
                        })
        
        return shard_data
    
    def create_parquet_manifest(self, parquet_files: List[Path]) -> Path:
        """Создать манифест Parquet файлов"""
        
        manifest_path = self.output_dir / "parquet_manifest.json"
        
        manifest = {
            "total_files": len(parquet_files),
            "created_at": datetime.now().isoformat(),
            "files": []
        }
        
        for parquet_file in parquet_files:
            file_info = {
                "file_path": str(parquet_file.relative_to(self.output_dir)),
                "file_size_bytes": parquet_file.stat().st_size,
                "file_size_mb": parquet_file.stat().st_size / (1024 * 1024)
            }
            
            # Попытаться получить количество строк
            try:
                df = pd.read_parquet(parquet_file)
                file_info["total_rows"] = len(df)
            except Exception as e:
                file_info["error"] = str(e)
            
            manifest["files"].append(file_info)
        
        # Сохранить манифест
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Манифест Parquet создан: {manifest_path}")
        return manifest_path


def main():
    parser = argparse.ArgumentParser(description="Oracle850B Parquet Export")
    parser.add_argument("--input-file", help="Входной файл")
    parser.add_argument("--webdataset-dir", help="Директория WebDataset")
    parser.add_argument("--split", default="train", help="Split для WebDataset")
    parser.add_argument("--output-dir", default="data/parquet", help="Выходная директория")
    parser.add_argument("--batch-size", type=int, default=10000, help="Размер батча")
    
    args = parser.parse_args()
    
    exporter = OracleParquetExporter(args.output_dir)
    
    if args.input_file:
        # Экспорт файла
        input_path = Path(args.input_file)
        output_path = exporter.export_file_to_parquet(
            input_path, batch_size=args.batch_size
        )
        print(f"✅ Файл экспортирован: {output_path}")
        
    elif args.webdataset_dir:
        # Экспорт WebDataset
        webdataset_path = Path(args.webdataset_dir)
        output_path = exporter.export_webdataset_to_parquet(
            webdataset_path, args.split
        )
        if output_path:
            print(f"✅ WebDataset экспортирован: {output_path}")
    else:
        print("❌ Укажите --input-file или --webdataset-dir")


if __name__ == "__main__":
    main()
