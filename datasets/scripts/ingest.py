#!/usr/bin/env python3
"""
Oracle850B Data Ingest
Приём данных из S3/HTTPS, каталогизация
Author: MagistrTheOne|Краснодар|2025
"""

import os
import json
import hashlib
import argparse
import requests
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import boto3
from botocore.exceptions import ClientError


class OracleDataIngest:
    """Ингрест данных для Oracle850B"""
    
    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.output_dir / "ingest_manifest.json"
        
        # Инициализировать S3 клиент
        self.s3_client = boto3.client('s3') if os.getenv('AWS_ACCESS_KEY_ID') else None
        
    def ingest_from_s3(self, bucket: str, prefix: str, 
                      max_files: int = None) -> List[Dict[str, Any]]:
        """Ингрест данных из S3"""
        
        if not self.s3_client:
            print("❌ S3 клиент не настроен (AWS_ACCESS_KEY_ID не найден)")
            return []
        
        print(f"🔄 Ингрест из S3: s3://{bucket}/{prefix}")
        
        ingested_files = []
        file_count = 0
        
        try:
            paginator = self.s3_client.get_paginator('list_objects_v2')
            pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
            
            for page in pages:
                if 'Contents' not in page:
                    continue
                
                for obj in page['Contents']:
                    if max_files and file_count >= max_files:
                        break
                    
                    key = obj['Key']
                    size = obj['Size']
                    
                    # Пропустить директории
                    if key.endswith('/'):
                        continue
                    
                    # Скачать файл
                    local_path = self.output_dir / key.replace('/', '_')
                    self.s3_client.download_file(bucket, key, str(local_path))
                    
                    # Вычислить хеш
                    file_hash = self._calculate_file_hash(local_path)
                    
                    file_info = {
                        "source": f"s3://{bucket}/{key}",
                        "local_path": str(local_path),
                        "size_bytes": size,
                        "hash": file_hash,
                        "ingested_at": datetime.now().isoformat(),
                        "license": "unknown",
                        "language": "unknown"
                    }
                    
                    ingested_files.append(file_info)
                    file_count += 1
                    
                    print(f"  ✅ {key} ({size} bytes)")
                
                if max_files and file_count >= max_files:
                    break
                    
        except ClientError as e:
            print(f"❌ Ошибка S3: {e}")
            return []
        
        print(f"✅ Ингрест завершен: {file_count} файлов")
        return ingested_files
    
    def ingest_from_https(self, urls: List[str], 
                         max_files: int = None) -> List[Dict[str, Any]]:
        """Ингрест данных из HTTPS"""
        
        print(f"🔄 Ингрест из HTTPS: {len(urls)} URL")
        
        ingested_files = []
        file_count = 0
        
        for url in urls:
            if max_files and file_count >= max_files:
                break
            
            try:
                response = requests.get(url, stream=True, timeout=30)
                response.raise_for_status()
                
                # Определить имя файла
                filename = url.split('/')[-1] or f"file_{file_count}"
                local_path = self.output_dir / filename
                
                # Скачать файл
                with open(local_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Вычислить хеш
                file_hash = self._calculate_file_hash(local_path)
                size = local_path.stat().st_size
                
                file_info = {
                    "source": url,
                    "local_path": str(local_path),
                    "size_bytes": size,
                    "hash": file_hash,
                    "ingested_at": datetime.now().isoformat(),
                    "license": "unknown",
                    "language": "unknown"
                }
                
                ingested_files.append(file_info)
                file_count += 1
                
                print(f"  ✅ {filename} ({size} bytes)")
                
            except Exception as e:
                print(f"  ❌ Ошибка скачивания {url}: {e}")
                continue
        
        print(f"✅ Ингрест завершен: {file_count} файлов")
        return ingested_files
    
    def _calculate_file_hash(self, file_path: Path) -> str:
        """Вычислить SHA-256 хеш файла"""
        hash_sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()
    
    def save_manifest(self, files: List[Dict[str, Any]]):
        """Сохранить манифест ингреста"""
        
        manifest = {
            "ingest_info": {
                "total_files": len(files),
                "total_size_bytes": sum(f["size_bytes"] for f in files),
                "ingested_at": datetime.now().isoformat(),
                "output_dir": str(self.output_dir)
            },
            "files": files
        }
        
        with open(self.manifest_file, 'w', encoding='utf-8') as f:
            json.dump(manifest, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Манифест сохранен: {self.manifest_file}")
    
    def load_manifest(self) -> Dict[str, Any]:
        """Загрузить манифест"""
        if not self.manifest_file.exists():
            return {}
        
        with open(self.manifest_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def get_ingest_stats(self) -> Dict[str, Any]:
        """Получить статистику ингреста"""
        manifest = self.load_manifest()
        
        if not manifest:
            return {"error": "Манифест не найден"}
        
        return {
            "total_files": manifest["ingest_info"]["total_files"],
            "total_size_gb": manifest["ingest_info"]["total_size_bytes"] / (1024**3),
            "ingested_at": manifest["ingest_info"]["ingested_at"],
            "output_dir": manifest["ingest_info"]["output_dir"]
        }


def main():
    parser = argparse.ArgumentParser(description="Oracle850B Data Ingest")
    parser.add_argument("--s3-bucket", help="S3 bucket для ингреста")
    parser.add_argument("--s3-prefix", help="S3 prefix")
    parser.add_argument("--https-urls", nargs="+", help="HTTPS URLs для скачивания")
    parser.add_argument("--output-dir", default="data/raw", help="Выходная директория")
    parser.add_argument("--max-files", type=int, help="Максимум файлов")
    parser.add_argument("--stats", action="store_true", help="Показать статистику")
    
    args = parser.parse_args()
    
    ingest = OracleDataIngest(args.output_dir)
    
    if args.stats:
        stats = ingest.get_ingest_stats()
        print("Статистика ингреста:")
        print(json.dumps(stats, indent=2, ensure_ascii=False))
        return
    
    ingested_files = []
    
    if args.s3_bucket:
        files = ingest.ingest_from_s3(
            args.s3_bucket, 
            args.s3_prefix or "",
            args.max_files
        )
        ingested_files.extend(files)
    
    if args.https_urls:
        files = ingest.ingest_from_https(
            args.https_urls,
            args.max_files
        )
        ingested_files.extend(files)
    
    if ingested_files:
        ingest.save_manifest(ingested_files)
        print(f"✅ Ингрест завершен: {len(ingested_files)} файлов")


if __name__ == "__main__":
    main()
