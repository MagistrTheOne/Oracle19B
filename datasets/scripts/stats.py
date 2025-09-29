#!/usr/bin/env python3
"""
Oracle850B Data Statistics
Сводки качества данных, дубликатов, языков, тематик
Author: MagistrTheOne|Краснодар|2025
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Counter
from datetime import datetime
from collections import defaultdict
import re


class OracleDataStats:
    """Статистика данных Oracle850B"""
    
    def __init__(self, output_dir: str = "data/stats"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_file(self, input_file: Path) -> Dict[str, Any]:
        """Анализ файла данных"""
        
        print(f"🔄 Анализ файла: {input_file}")
        
        stats = {
            "file_info": {
                "file_path": str(input_file),
                "file_size_bytes": input_file.stat().st_size,
                "analyzed_at": datetime.now().isoformat()
            },
            "text_stats": {
                "total_lines": 0,
                "non_empty_lines": 0,
                "total_characters": 0,
                "total_words": 0,
                "total_tokens": 0
            },
            "length_distribution": {
                "min_length": float('inf'),
                "max_length": 0,
                "avg_length": 0,
                "length_buckets": {}
            },
            "language_distribution": {},
            "quality_metrics": {
                "avg_words_per_line": 0,
                "avg_chars_per_line": 0,
                "lines_with_punctuation": 0,
                "lines_with_numbers": 0,
                "lines_with_uppercase": 0
            },
            "duplicate_analysis": {
                "exact_duplicates": 0,
                "near_duplicates": 0,
                "duplicate_rate": 0.0
            }
        }
        
        line_lengths = []
        languages = Counter()
        content_hashes = set()
        duplicate_hashes = set()
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                stats["text_stats"]["total_lines"] += 1
                
                if line_num % 100000 == 0:
                    print(f"  Обработано строк: {line_num}")
                
                line = line.strip()
                if not line:
                    continue
                
                stats["text_stats"]["non_empty_lines"] += 1
                
                # Базовая статистика
                line_length = len(line)
                line_lengths.append(line_length)
                
                stats["text_stats"]["total_characters"] += line_length
                stats["text_stats"]["total_words"] += len(line.split())
                
                # Обновить min/max длины
                if line_length < stats["length_distribution"]["min_length"]:
                    stats["length_distribution"]["min_length"] = line_length
                if line_length > stats["length_distribution"]["max_length"]:
                    stats["length_distribution"]["max_length"] = line_length
                
                # Определение языка
                language = self._detect_language(line)
                languages[language] += 1
                
                # Качественные метрики
                if self._has_punctuation(line):
                    stats["quality_metrics"]["lines_with_punctuation"] += 1
                if self._has_numbers(line):
                    stats["quality_metrics"]["lines_with_numbers"] += 1
                if self._has_uppercase(line):
                    stats["quality_metrics"]["lines_with_uppercase"] += 1
                
                # Анализ дубликатов
                content_hash = hash(line)
                if content_hash in content_hashes:
                    duplicate_hashes.add(content_hash)
                    stats["duplicate_analysis"]["exact_duplicates"] += 1
                else:
                    content_hashes.add(content_hash)
        
        # Вычислить производные метрики
        if stats["text_stats"]["non_empty_lines"] > 0:
            stats["length_distribution"]["avg_length"] = sum(line_lengths) / len(line_lengths)
            stats["quality_metrics"]["avg_words_per_line"] = (
                stats["text_stats"]["total_words"] / stats["text_stats"]["non_empty_lines"]
            )
            stats["quality_metrics"]["avg_chars_per_line"] = (
                stats["text_stats"]["total_characters"] / stats["text_stats"]["non_empty_lines"]
            )
            
            stats["duplicate_analysis"]["duplicate_rate"] = (
                stats["duplicate_analysis"]["exact_duplicates"] / stats["text_stats"]["non_empty_lines"]
            )
        
        # Распределение языков
        stats["language_distribution"] = dict(languages.most_common())
        
        # Распределение длин по корзинам
        stats["length_distribution"]["length_buckets"] = self._create_length_buckets(line_lengths)
        
        return stats
    
    def _detect_language(self, text: str) -> str:
        """Простое определение языка"""
        cyrillic_count = len(re.findall(r'[а-яё]', text.lower()))
        latin_count = len(re.findall(r'[a-z]', text.lower()))
        
        if cyrillic_count > latin_count:
            return 'ru'
        elif latin_count > 0:
            return 'en'
        else:
            return 'unknown'
    
    def _has_punctuation(self, text: str) -> bool:
        """Проверить наличие пунктуации"""
        return bool(re.search(r'[.!?,:;]', text))
    
    def _has_numbers(self, text: str) -> bool:
        """Проверить наличие чисел"""
        return bool(re.search(r'\d', text))
    
    def _has_uppercase(self, text: str) -> bool:
        """Проверить наличие заглавных букв"""
        return bool(re.search(r'[A-Z]', text))
    
    def _create_length_buckets(self, lengths: List[int]) -> Dict[str, int]:
        """Создать корзины длин"""
        buckets = {
            "0-50": 0,
            "51-100": 0,
            "101-200": 0,
            "201-500": 0,
            "501-1000": 0,
            "1000+": 0
        }
        
        for length in lengths:
            if length <= 50:
                buckets["0-50"] += 1
            elif length <= 100:
                buckets["51-100"] += 1
            elif length <= 200:
                buckets["101-200"] += 1
            elif length <= 500:
                buckets["201-500"] += 1
            elif length <= 1000:
                buckets["501-1000"] += 1
            else:
                buckets["1000+"] += 1
        
        return buckets
    
    def analyze_webdataset(self, webdataset_dir: Path, split: str = "train") -> Dict[str, Any]:
        """Анализ WebDataset"""
        
        print(f"🔄 Анализ WebDataset: {webdataset_dir}/{split}")
        
        split_dir = webdataset_dir / split
        shard_files = list(split_dir.glob("shard-*.tar"))
        
        if not shard_files:
            return {"error": f"Шарды не найдены в {split_dir}"}
        
        print(f"📊 Найдено шардов: {len(shard_files)}")
        
        # Агрегированная статистика
        total_stats = {
            "webdataset_info": {
                "split": split,
                "total_shards": len(shard_files),
                "analyzed_at": datetime.now().isoformat()
            },
            "aggregated_stats": {
                "total_samples": 0,
                "total_size_bytes": 0,
                "avg_shard_size_mb": 0
            },
            "shard_details": []
        }
        
        total_samples = 0
        total_size = 0
        
        for shard_file in shard_files:
            print(f"  Анализ шарда: {shard_file.name}")
            
            # Информация о шарде
            shard_size = shard_file.stat().st_size
            total_size += shard_size
            
            # Загрузить индекс шарда
            idx_path = shard_file.with_suffix('.idx')
            shard_info = {}
            if idx_path.exists():
                with open(idx_path, 'r', encoding='utf-8') as f:
                    shard_info = json.load(f)
                    total_samples += shard_info.get("shard_info", {}).get("total_samples", 0)
            
            shard_detail = {
                "shard_file": str(shard_file.relative_to(webdataset_dir)),
                "shard_size_bytes": shard_size,
                "shard_size_mb": shard_size / (1024 * 1024),
                "total_samples": shard_info.get("shard_info", {}).get("total_samples", 0),
                "index_info": shard_info
            }
            
            total_stats["shard_details"].append(shard_detail)
        
        # Обновить агрегированную статистику
        total_stats["aggregated_stats"]["total_samples"] = total_samples
        total_stats["aggregated_stats"]["total_size_bytes"] = total_size
        if len(shard_files) > 0:
            total_stats["aggregated_stats"]["avg_shard_size_mb"] = total_size / len(shard_files) / (1024 * 1024)
        
        return total_stats
    
    def generate_quality_report(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация отчёта о качестве"""
        
        report = {
            "quality_assessment": {
                "overall_score": 0.0,
                "issues": [],
                "recommendations": []
            },
            "data_health": {},
            "generated_at": datetime.now().isoformat()
        }
        
        # Оценка качества на основе метрик
        score = 1.0
        issues = []
        recommendations = []
        
        # Проверка дубликатов
        duplicate_rate = stats.get("duplicate_analysis", {}).get("duplicate_rate", 0)
        if duplicate_rate > 0.1:
            score -= 0.2
            issues.append(f"Высокий уровень дубликатов: {duplicate_rate:.2%}")
            recommendations.append("Рекомендуется дедупликация данных")
        
        # Проверка языкового распределения
        lang_dist = stats.get("language_distribution", {})
        if len(lang_dist) == 1 and "unknown" in lang_dist:
            score -= 0.3
            issues.append("Не удалось определить языки текстов")
            recommendations.append("Проверить качество текстовых данных")
        
        # Проверка длины текстов
        avg_length = stats.get("length_distribution", {}).get("avg_length", 0)
        if avg_length < 50:
            score -= 0.1
            issues.append(f"Средняя длина текста слишком мала: {avg_length:.1f}")
            recommendations.append("Рассмотреть фильтрацию коротких текстов")
        
        # Проверка пунктуации
        total_lines = stats.get("text_stats", {}).get("non_empty_lines", 0)
        punct_lines = stats.get("quality_metrics", {}).get("lines_with_punctuation", 0)
        if total_lines > 0 and punct_lines / total_lines < 0.5:
            score -= 0.1
            issues.append("Низкий уровень пунктуации в текстах")
            recommendations.append("Проверить качество текстовых данных")
        
        # Обновить отчёт
        report["quality_assessment"]["overall_score"] = max(0.0, score)
        report["quality_assessment"]["issues"] = issues
        report["quality_assessment"]["recommendations"] = recommendations
        
        # Оценка здоровья данных
        report["data_health"] = {
            "duplicate_rate": duplicate_rate,
            "language_diversity": len(lang_dist),
            "avg_text_length": avg_length,
            "total_samples": stats.get("text_stats", {}).get("non_empty_lines", 0)
        }
        
        return report
    
    def save_stats(self, stats: Dict[str, Any], output_file: Path = None) -> Path:
        """Сохранить статистику"""
        
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"stats_{timestamp}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"📊 Статистика сохранена: {output_file}")
        return output_file


def main():
    parser = argparse.ArgumentParser(description="Oracle850B Data Statistics")
    parser.add_argument("--input-file", help="Входной файл для анализа")
    parser.add_argument("--webdataset-dir", help="Директория WebDataset")
    parser.add_argument("--split", default="train", help="Split для WebDataset")
    parser.add_argument("--output-dir", default="data/stats", help="Выходная директория")
    parser.add_argument("--quality-report", action="store_true", help="Генерация отчёта о качестве")
    
    args = parser.parse_args()
    
    stats_analyzer = OracleDataStats(args.output_dir)
    
    if args.input_file:
        # Анализ файла
        input_path = Path(args.input_file)
        stats = stats_analyzer.analyze_file(input_path)
        
        # Генерация отчёта о качестве
        if args.quality_report:
            quality_report = stats_analyzer.generate_quality_report(stats)
            stats["quality_report"] = quality_report
        
        # Сохранение статистики
        output_file = stats_analyzer.save_stats(stats)
        print(f"✅ Анализ завершён: {output_file}")
        
    elif args.webdataset_dir:
        # Анализ WebDataset
        webdataset_path = Path(args.webdataset_dir)
        stats = stats_analyzer.analyze_webdataset(webdataset_path, args.split)
        
        # Сохранение статистики
        output_file = stats_analyzer.save_stats(stats)
        print(f"✅ Анализ WebDataset завершён: {output_file}")
    else:
        print("❌ Укажите --input-file или --webdataset-dir")


if __name__ == "__main__":
    main()
