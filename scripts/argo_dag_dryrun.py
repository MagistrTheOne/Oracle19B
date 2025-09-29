#!/usr/bin/env python3
"""
Oracle850B Argo DAG Dry-Run
Валидация пайплайнов данных и обучения
Author: MagistrTheOne|Краснодар|2025
"""

import os
import sys
import yaml
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional


class OracleArgoDAGValidator:
    """Валидатор Argo DAG для Oracle850B"""
    
    def __init__(self, argo_dir: str = "infra/argo"):
        self.argo_dir = Path(argo_dir)
        self.pipelines = {}
        self.errors = []
        self.warnings = []
    
    def load_pipelines(self) -> bool:
        """Загрузить все пайплайны Argo"""
        print("🔍 Загрузка Argo пайплайнов...")
        
        pipeline_files = [
            "data-pipeline.yaml",
            "serving-pipeline.yaml", 
            "training-pipeline.yaml"
        ]
        
        for pipeline_file in pipeline_files:
            pipeline_path = self.argo_dir / pipeline_file
            if pipeline_path.exists():
                try:
                    with open(pipeline_path, 'r', encoding='utf-8') as f:
                        pipeline = yaml.safe_load(f)
                    
                    self.pipelines[pipeline_file] = pipeline
                    print(f"  ✅ Загружен: {pipeline_file}")
                    
                except Exception as e:
                    error_msg = f"Ошибка загрузки {pipeline_file}: {e}"
                    self.errors.append(error_msg)
                    print(f"  ❌ {error_msg}")
            else:
                warning_msg = f"Файл не найден: {pipeline_file}"
                self.warnings.append(warning_msg)
                print(f"  ⚠️  {warning_msg}")
        
        return len(self.errors) == 0
    
    def validate_data_pipeline(self) -> bool:
        """Валидация пайплайна данных"""
        print("\n🔍 Валидация data-pipeline.yaml...")
        
        if "data-pipeline.yaml" not in self.pipelines:
            self.errors.append("data-pipeline.yaml не найден")
            return False
        
        pipeline = self.pipelines["data-pipeline.yaml"]
        success = True
        
        # Проверка структуры
        required_fields = ["apiVersion", "kind", "metadata", "spec"]
        for field in required_fields:
            if field not in pipeline:
                self.errors.append(f"data-pipeline: отсутствует поле {field}")
                success = False
        
        if not success:
            return False
        
        # Проверка WorkflowTemplate
        if pipeline.get("kind") != "WorkflowTemplate":
            self.errors.append("data-pipeline: должен быть WorkflowTemplate")
            success = False
        
        # Проверка шагов пайплайна
        spec = pipeline.get("spec", {})
        templates = spec.get("templates", [])
        
        required_steps = [
            "ingest-data",
            "clean-data", 
            "decontaminate-data",
            "shard-data",
            "validate-data"
        ]
        
        step_names = [template.get("name") for template in templates]
        
        for step in required_steps:
            if step not in step_names:
                self.errors.append(f"data-pipeline: отсутствует шаг {step}")
                success = False
        
        if success:
            print("  ✅ Структура data-pipeline валидна")
            print(f"  📊 Шагов в пайплайне: {len(templates)}")
            print(f"  🔄 Зависимости: {len(spec.get('workflows', []))}")
        
        return success
    
    def validate_serving_pipeline(self) -> bool:
        """Валидация пайплайна сервинга"""
        print("\n🔍 Валидация serving-pipeline.yaml...")
        
        if "serving-pipeline.yaml" not in self.pipelines:
            self.errors.append("serving-pipeline.yaml не найден")
            return False
        
        pipeline = self.pipelines["serving-pipeline.yaml"]
        success = True
        
        # Проверка структуры
        required_fields = ["apiVersion", "kind", "metadata", "spec"]
        for field in required_fields:
            if field not in pipeline:
                self.errors.append(f"serving-pipeline: отсутствует поле {field}")
                success = False
        
        if not success:
            return False
        
        # Проверка WorkflowTemplate
        if pipeline.get("kind") != "WorkflowTemplate":
            self.errors.append("serving-pipeline: должен быть WorkflowTemplate")
            success = False
        
        # Проверка шаблонов
        spec = pipeline.get("spec", {})
        templates = spec.get("templates", [])
        
        if not templates:
            self.errors.append("serving-pipeline: отсутствуют шаблоны")
            success = False
        else:
            # Проверка контейнеров в шаблонах
            container_found = False
            for template in templates:
                container = template.get("container")
                if container:
                    container_found = True
                    
                    # Проверка образа
                    image = container.get("image")
                    if not image or "oracle850b" not in image:
                        self.warnings.append("serving-pipeline: образ не содержит oracle850b")
                    
                    # Проверка ресурсов
                    resources = container.get("resources", {})
                    if not resources:
                        self.warnings.append("serving-pipeline: отсутствуют ресурсы")
            
            if not container_found:
                self.warnings.append("serving-pipeline: не найдены контейнеры в шаблонах")
        
        if success:
            print("  ✅ Структура serving-pipeline валидна")
            print(f"  📋 Шаблонов: {len(templates)}")
            print(f"  🐳 Контейнеров найдено: {container_found}")
        
        return success
    
    def validate_training_pipeline(self) -> bool:
        """Валидация пайплайна обучения"""
        print("\n🔍 Валидация training-pipeline.yaml...")
        
        if "training-pipeline.yaml" not in self.pipelines:
            self.errors.append("training-pipeline.yaml не найден")
            return False
        
        pipeline = self.pipelines["training-pipeline.yaml"]
        success = True
        
        # Проверка структуры
        required_fields = ["apiVersion", "kind", "metadata", "spec"]
        for field in required_fields:
            if field not in pipeline:
                self.errors.append(f"training-pipeline: отсутствует поле {field}")
                success = False
        
        if not success:
            return False
        
        # Проверка WorkflowTemplate
        if pipeline.get("kind") != "WorkflowTemplate":
            self.errors.append("training-pipeline: должен быть WorkflowTemplate")
            success = False
        
        # Проверка шаблонов
        spec = pipeline.get("spec", {})
        templates = spec.get("templates", [])
        
        if not templates:
            self.errors.append("training-pipeline: отсутствуют шаблоны")
            success = False
        else:
            # Проверка контейнеров в шаблонах
            container_found = False
            for template in templates:
                container = template.get("container")
                if container:
                    container_found = True
                    
                    # Проверка переменных окружения
                    env = container.get("env", [])
                    required_env = [
                        "MODEL_NAME",
                        "TRAINING_DATA_PATH", 
                        "CHECKPOINT_PATH"
                    ]
                    
                    env_names = [e.get("name") for e in env]
                    for req_env in required_env:
                        if req_env not in env_names:
                            self.warnings.append(f"training-pipeline: отсутствует переменная {req_env}")
                    
                    # Проверка ресурсов
                    resources = container.get("resources", {})
                    if not resources:
                        self.warnings.append("training-pipeline: отсутствуют ресурсы")
                    else:
                        limits = resources.get("limits", {})
                        if "nvidia.com/gpu" not in limits:
                            self.warnings.append("training-pipeline: отсутствует GPU")
            
            if not container_found:
                self.warnings.append("training-pipeline: не найдены контейнеры в шаблонах")
        
        if success:
            print("  ✅ Структура training-pipeline валидна")
            print(f"  📋 Шаблонов: {len(templates)}")
            print(f"  🐳 Контейнеров найдено: {container_found}")
        
        return success
    
    def validate_dependencies(self) -> bool:
        """Валидация зависимостей между пайплайнами"""
        print("\n🔍 Валидация зависимостей...")
        
        success = True
        
        # Проверка последовательности
        pipeline_order = [
            "data-pipeline.yaml",
            "training-pipeline.yaml", 
            "serving-pipeline.yaml"
        ]
        
        for i, pipeline_file in enumerate(pipeline_order):
            if pipeline_file not in self.pipelines:
                self.warnings.append(f"Пайплайн {pipeline_file} отсутствует в последовательности")
                continue
            
            pipeline = self.pipelines[pipeline_file]
            
            # Проверка метаданных
            metadata = pipeline.get("metadata", {})
            labels = metadata.get("labels", {})
            
            if "pipeline-stage" not in labels:
                self.warnings.append(f"{pipeline_file}: отсутствует pipeline-stage")
            else:
                stage = labels["pipeline-stage"]
                expected_stage = ["data", "training", "serving"][i]
                if stage != expected_stage:
                    self.warnings.append(f"{pipeline_file}: неверный pipeline-stage {stage}, ожидается {expected_stage}")
        
        if success:
            print("  ✅ Зависимости валидны")
        
        return success
    
    def validate_kubernetes_syntax(self) -> bool:
        """Валидация синтаксиса Kubernetes"""
        print("\n🔍 Валидация синтаксиса Kubernetes...")
        
        success = True
        
        for pipeline_file, pipeline in self.pipelines.items():
            # Проверка обязательных полей
            required_top_level = ["apiVersion", "kind", "metadata"]
            
            for field in required_top_level:
                if field not in pipeline:
                    self.errors.append(f"{pipeline_file}: отсутствует {field}")
                    success = False
            
            # Проверка метаданных
            metadata = pipeline.get("metadata", {})
            if "name" not in metadata:
                self.errors.append(f"{pipeline_file}: отсутствует metadata.name")
                success = False
            
            # Проверка спецификации
            spec = pipeline.get("spec", {})
            if not spec:
                self.errors.append(f"{pipeline_file}: отсутствует spec")
                success = False
        
        if success:
            print("  ✅ Синтаксис Kubernetes валиден")
        
        return success
    
    def generate_report(self) -> Dict[str, Any]:
        """Генерация отчета валидации"""
        report = {
            "timestamp": "2024-12-19T00:00:00Z",
            "validator": "OracleArgoDAGValidator",
            "version": "1.0",
            "summary": {
                "total_pipelines": len(self.pipelines),
                "errors": len(self.errors),
                "warnings": len(self.warnings),
                "success": len(self.errors) == 0
            },
            "pipelines": list(self.pipelines.keys()),
            "errors": self.errors,
            "warnings": self.warnings,
            "recommendations": [
                "Убедитесь, что все пайплайны имеют правильные зависимости",
                "Проверьте ресурсы и лимиты для production",
                "Добавьте мониторинг и логирование",
                "Настройте retry политики для критических шагов"
            ]
        }
        
        return report
    
    def run_full_validation(self) -> bool:
        """Полная валидация всех пайплайнов"""
        print("🚀 Oracle850B Argo DAG Validation")
        print("=" * 50)
        
        success = True
        
        # 1. Загрузка пайплайнов
        if not self.load_pipelines():
            success = False
        
        # 2. Валидация data-pipeline
        if not self.validate_data_pipeline():
            success = False
        
        # 3. Валидация serving-pipeline
        if not self.validate_serving_pipeline():
            success = False
        
        # 4. Валидация training-pipeline
        if not self.validate_training_pipeline():
            success = False
        
        # 5. Валидация зависимостей
        if not self.validate_dependencies():
            success = False
        
        # 6. Валидация синтаксиса
        if not self.validate_kubernetes_syntax():
            success = False
        
        # 7. Генерация отчета
        report = self.generate_report()
        
        # Сохранение отчета
        report_file = Path("argo_validation_report.json")
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n📋 Отчет сохранен: {report_file}")
        
        if success:
            print("\n✅ Все пайплайны валидны!")
        else:
            print(f"\n❌ Найдено ошибок: {len(self.errors)}")
            print(f"⚠️  Найдено предупреждений: {len(self.warnings)}")
        
        return success


def main():
    parser = argparse.ArgumentParser(description="Oracle850B Argo DAG Validator")
    parser.add_argument("--argo-dir", default="infra/argo", help="Директория с Argo файлами")
    parser.add_argument("--data-only", action="store_true", help="Только data-pipeline")
    parser.add_argument("--serving-only", action="store_true", help="Только serving-pipeline")
    parser.add_argument("--training-only", action="store_true", help="Только training-pipeline")
    parser.add_argument("--report", action="store_true", help="Только отчет")
    
    args = parser.parse_args()
    
    validator = OracleArgoDAGValidator(args.argo_dir)
    
    if args.data_only:
        success = validator.load_pipelines() and validator.validate_data_pipeline()
    elif args.serving_only:
        success = validator.load_pipelines() and validator.validate_serving_pipeline()
    elif args.training_only:
        success = validator.load_pipelines() and validator.validate_training_pipeline()
    elif args.report:
        validator.load_pipelines()
        report = validator.generate_report()
        print(json.dumps(report, indent=2, ensure_ascii=False))
        success = True
    else:
        success = validator.run_full_validation()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
