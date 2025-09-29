#!/usr/bin/env python3
"""
Oracle850B Data Decontamination
Стоп-листы eval, отчёты пересечений
Author: MagistrTheOne|Краснодар|2025
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Set, Any
from datetime import datetime
import re


class OracleDecontaminator:
    """Де-контаминация данных Oracle850B"""
    
    def __init__(self, output_dir: str = "data/decontaminated"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Стоп-листы для eval наборов
        self.eval_stopwords = {
            # GSM8K
            "gsm8k": [
                "jane has", "sarah has", "mike has", "tom has",
                "how many", "what is", "calculate", "solve",
                "math problem", "word problem"
            ],
            
            # MATH
            "math": [
                "prove that", "show that", "find the", "determine",
                "mathematical", "theorem", "lemma", "corollary"
            ],
            
            # HumanEval
            "humaneval": [
                "def ", "function", "return", "python",
                "code", "programming", "algorithm"
            ],
            
            # MMLU
            "mmlu": [
                "which of the following", "what is the",
                "according to", "based on", "the correct answer"
            ],
            
            # Hellaswag
            "hellaswag": [
                "complete the", "finish the", "what happens next",
                "choose the best", "select the"
            ]
        }
        
        # Паттерны для обнаружения eval данных
        self.eval_patterns = {
            "gsm8k": r"(?:jane|sarah|mike|tom).*?(?:how many|what is|calculate)",
            "math": r"(?:prove|show|find|determine).*?(?:theorem|lemma)",
            "humaneval": r"def\s+\w+.*?return",
            "mmlu": r"(?:which of the following|what is the).*?(?:correct answer)",
            "hellaswag": r"(?:complete|finish).*?(?:choose|select)"
        }
    
    def detect_eval_contamination(self, text: str) -> Dict[str, Any]:
        """Обнаружить контаминацию eval данными"""
        
        contamination = {
            "is_contaminated": False,
            "detected_eval": [],
            "confidence_scores": {},
            "matched_patterns": []
        }
        
        text_lower = text.lower()
        
        # Проверка по стоп-словам
        for eval_name, stopwords in self.eval_stopwords.items():
            matches = []
            for stopword in stopwords:
                if stopword in text_lower:
                    matches.append(stopword)
            
            if matches:
                contamination["detected_eval"].append(eval_name)
                contamination["confidence_scores"][eval_name] = len(matches) / len(stopwords)
        
        # Проверка по паттернам
        for eval_name, pattern in self.eval_patterns.items():
            if re.search(pattern, text_lower, re.IGNORECASE):
                contamination["matched_patterns"].append(eval_name)
                if eval_name not in contamination["detected_eval"]:
                    contamination["detected_eval"].append(eval_name)
        
        # Определить общую контаминацию
        contamination["is_contaminated"] = len(contamination["detected_eval"]) > 0
        
        return contamination
    
    def calculate_contamination_score(self, text: str) -> float:
        """Вычислить общий скор контаминации"""
        contamination = self.detect_eval_contamination(text)
        
        if not contamination["is_contaminated"]:
            return 0.0
        
        # Взвешенная сумма скоров
        total_score = 0.0
        total_weight = 0.0
        
        for eval_name in contamination["detected_eval"]:
            weight = 1.0  # Можно настроить веса для разных eval
            score = contamination["confidence_scores"].get(eval_name, 0.0)
            
            total_score += weight * score
            total_weight += weight
        
        return total_score / total_weight if total_weight > 0 else 0.0
    
    def decontaminate_text(self, text: str, threshold: float = 0.3) -> Dict[str, Any]:
        """Де-контаминация текста"""
        
        contamination = self.detect_eval_contamination(text)
        contamination_score = self.calculate_contamination_score(text)
        
        should_keep = contamination_score < threshold
        
        result = {
            "original_text": text,
            "is_contaminated": contamination["is_contaminated"],
            "contamination_score": contamination_score,
            "detected_eval": contamination["detected_eval"],
            "matched_patterns": contamination["matched_patterns"],
            "should_keep": should_keep,
            "threshold": threshold,
            "decontaminated_at": datetime.now().isoformat()
        }
        
        return result
    
    def decontaminate_file(self, input_file: Path, output_file: Path = None, 
                          threshold: float = 0.3) -> Dict[str, Any]:
        """Де-контаминация файла"""
        
        if output_file is None:
            output_file = self.output_dir / f"decontaminated_{input_file.name}"
        
        print(f"🔄 Де-контаминация файла: {input_file}")
        print(f"📊 Порог контаминации: {threshold}")
        
        decontaminated_texts = []
        stats = {
            "total_lines": 0,
            "kept_lines": 0,
            "removed_contaminated": 0,
            "contamination_by_eval": {},
            "avg_contamination_score": 0.0
        }
        
        contamination_scores = []
        
        with open(input_file, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                stats["total_lines"] += 1
                
                if line_num % 1000 == 0:
                    print(f"  Обработано строк: {line_num}")
                
                # Де-контаминация строки
                result = self.decontaminate_text(line.strip(), threshold)
                contamination_scores.append(result["contamination_score"])
                
                if result["should_keep"]:
                    decontaminated_texts.append(line.strip())
                    stats["kept_lines"] += 1
                else:
                    stats["removed_contaminated"] += 1
                    
                    # Подсчет по типам eval
                    for eval_name in result["detected_eval"]:
                        if eval_name not in stats["contamination_by_eval"]:
                            stats["contamination_by_eval"][eval_name] = 0
                        stats["contamination_by_eval"][eval_name] += 1
        
        # Вычислить средний скор контаминации
        if contamination_scores:
            stats["avg_contamination_score"] = sum(contamination_scores) / len(contamination_scores)
        
        # Сохранить де-контаминированные тексты
        with open(output_file, 'w', encoding='utf-8') as f:
            for text in decontaminated_texts:
                f.write(text + '\n')
        
        # Сохранить статистику
        stats_file = output_file.with_suffix('.stats.json')
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Де-контаминация завершена: {stats['kept_lines']}/{stats['total_lines']} строк сохранено")
        print(f"📊 Статистика: {json.dumps(stats, ensure_ascii=False)}")
        
        return stats
    
    def generate_contamination_report(self, input_files: List[Path], 
                                    output_file: Path = None) -> Dict[str, Any]:
        """Генерация отчёта о контаминации"""
        
        if output_file is None:
            output_file = self.output_dir / "contamination_report.json"
        
        print("📊 Генерация отчёта о контаминации...")
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "files_analyzed": [],
            "summary": {
                "total_files": 0,
                "total_lines": 0,
                "contaminated_lines": 0,
                "contamination_rate": 0.0
            },
            "contamination_by_eval": {},
            "recommendations": []
        }
        
        total_lines = 0
        contaminated_lines = 0
        
        for input_file in input_files:
            print(f"  Анализ файла: {input_file}")
            
            file_stats = {
                "file_path": str(input_file),
                "total_lines": 0,
                "contaminated_lines": 0,
                "contamination_rate": 0.0,
                "detected_eval": {}
            }
            
            with open(input_file, 'r', encoding='utf-8') as f:
                for line in f:
                    file_stats["total_lines"] += 1
                    total_lines += 1
                    
                    contamination = self.detect_eval_contamination(line.strip())
                    if contamination["is_contaminated"]:
                        file_stats["contaminated_lines"] += 1
                        contaminated_lines += 1
                        
                        # Подсчет по типам eval
                        for eval_name in contamination["detected_eval"]:
                            if eval_name not in file_stats["detected_eval"]:
                                file_stats["detected_eval"][eval_name] = 0
                            file_stats["detected_eval"][eval_name] += 1
                            
                            if eval_name not in report["contamination_by_eval"]:
                                report["contamination_by_eval"][eval_name] = 0
                            report["contamination_by_eval"][eval_name] += 1
            
            # Вычислить rate для файла
            if file_stats["total_lines"] > 0:
                file_stats["contamination_rate"] = file_stats["contaminated_lines"] / file_stats["total_lines"]
            
            report["files_analyzed"].append(file_stats)
        
        # Обновить сводку
        report["summary"]["total_files"] = len(input_files)
        report["summary"]["total_lines"] = total_lines
        report["summary"]["contaminated_lines"] = contaminated_lines
        if total_lines > 0:
            report["summary"]["contamination_rate"] = contaminated_lines / total_lines
        
        # Рекомендации
        if report["summary"]["contamination_rate"] > 0.1:
            report["recommendations"].append("Высокий уровень контаминации - рекомендуется агрессивная фильтрация")
        
        if "gsm8k" in report["contamination_by_eval"]:
            report["recommendations"].append("Обнаружена контаминация GSM8K - проверить математические данные")
        
        if "humaneval" in report["contamination_by_eval"]:
            report["recommendations"].append("Обнаружена контаминация HumanEval - проверить код данные")
        
        # Сохранить отчёт
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Отчёт сохранён: {output_file}")
        print(f"📊 Общая контаминация: {report['summary']['contamination_rate']:.2%}")
        
        return report


def main():
    parser = argparse.ArgumentParser(description="Oracle850B Data Decontamination")
    parser.add_argument("--input-file", help="Входной файл")
    parser.add_argument("--input-files", nargs="+", help="Входные файлы для отчёта")
    parser.add_argument("--output-file", help="Выходной файл")
    parser.add_argument("--output-dir", default="data/decontaminated", help="Выходная директория")
    parser.add_argument("--threshold", type=float, default=0.3, help="Порог контаминации")
    parser.add_argument("--report", action="store_true", help="Генерация отчёта")
    
    args = parser.parse_args()
    
    decontaminator = OracleDecontaminator(args.output_dir)
    
    if args.report and args.input_files:
        report = decontaminator.generate_contamination_report(
            [Path(f) for f in args.input_files]
        )
        print("✅ Отчёт о контаминации сгенерирован")
    elif args.input_file:
        input_path = Path(args.input_file)
        output_path = Path(args.output_file) if args.output_file else None
        
        stats = decontaminator.decontaminate_file(
            input_path, output_path, args.threshold
        )
        print(f"✅ Де-контаминация завершена: {stats['kept_lines']}/{stats['total_lines']} строк")
    else:
        print("❌ Укажите --input-file или --input-files с --report")


if __name__ == "__main__":
    main()
