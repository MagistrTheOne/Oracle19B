#!/usr/bin/env python3
"""
Oracle850B Kill Switch
Экстренная остановка всех пайплайнов и кластеров
Author: MagistrTheOne|Краснодар|2025
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime


class OracleKillSwitch:
    """Kill Switch для Oracle850B"""
    
    def __init__(self, config_file: str = "infra/kill_switch_config.json"):
        self.config_file = Path(config_file)
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Загрузить конфиг kill switch"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # Конфиг по умолчанию
        return {
            "kubernetes": {
                "enabled": True,
                "namespace": "oracle850b",
                "resources": [
                    "deployments",
                    "jobs",
                    "pods",
                    "services"
                ]
            },
            "terraform": {
                "enabled": True,
                "state_file": "infra/terraform/terraform.tfstate"
            },
            "monitoring": {
                "enabled": True,
                "alerts": True
            }
        }
    
    def kill_kubernetes_resources(self) -> bool:
        """Остановить все Kubernetes ресурсы"""
        
        if not self.config["kubernetes"]["enabled"]:
            print("⚠️  Kubernetes kill switch отключен")
            return True
        
        print("🔄 Остановка Kubernetes ресурсов...")
        
        namespace = self.config["kubernetes"]["namespace"]
        resources = self.config["kubernetes"]["resources"]
        
        success = True
        
        for resource in resources:
            try:
                print(f"  Остановка {resource}...")
                
                # Получить список ресурсов
                cmd = ["kubectl", "get", resource, "-n", namespace, "-o", "name"]
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    print(f"    ❌ Ошибка получения {resource}: {result.stderr}")
                    success = False
                    continue
                
                resource_names = result.stdout.strip().split('\n')
                if not resource_names or resource_names == ['']:
                    print(f"    ✅ {resource} не найдены")
                    continue
                
                # Удалить ресурсы
                for resource_name in resource_names:
                    if resource_name:
                        delete_cmd = ["kubectl", "delete", resource_name, "-n", namespace, "--force"]
                        delete_result = subprocess.run(delete_cmd, capture_output=True, text=True)
                        
                        if delete_result.returncode == 0:
                            print(f"    ✅ Удален: {resource_name}")
                        else:
                            print(f"    ❌ Ошибка удаления {resource_name}: {delete_result.stderr}")
                            success = False
                
            except Exception as e:
                print(f"    ❌ Ошибка обработки {resource}: {e}")
                success = False
        
        if success:
            print("✅ Kubernetes ресурсы остановлены")
        else:
            print("❌ Ошибки при остановке Kubernetes ресурсов")
        
        return success
    
    def kill_terraform_resources(self) -> bool:
        """Уничтожить Terraform ресурсы"""
        
        if not self.config["terraform"]["enabled"]:
            print("⚠️  Terraform kill switch отключен")
            return True
        
        print("🔄 Уничтожение Terraform ресурсов...")
        
        terraform_dir = Path("infra/terraform")
        if not terraform_dir.exists():
            print("❌ Директория Terraform не найдена")
            return False
        
        try:
            # Перейти в директорию Terraform
            os.chdir(terraform_dir)
            
            # Проверить состояние
            state_cmd = ["terraform", "state", "list"]
            state_result = subprocess.run(state_cmd, capture_output=True, text=True)
            
            if state_result.returncode != 0:
                print("❌ Ошибка проверки состояния Terraform")
                return False
            
            if not state_result.stdout.strip():
                print("✅ Нет ресурсов для уничтожения")
                return True
            
            # Уничтожить ресурсы
            destroy_cmd = ["terraform", "destroy", "-auto-approve"]
            destroy_result = subprocess.run(destroy_cmd, capture_output=True, text=True)
            
            if destroy_result.returncode == 0:
                print("✅ Terraform ресурсы уничтожены")
                return True
            else:
                print(f"❌ Ошибка уничтожения Terraform: {destroy_result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Ошибка Terraform: {e}")
            return False
        finally:
            # Вернуться в корневую директорию
            os.chdir("../..")
    
    def kill_monitoring(self) -> bool:
        """Остановить мониторинг"""
        
        if not self.config["monitoring"]["enabled"]:
            print("⚠️  Мониторинг kill switch отключен")
            return True
        
        print("🔄 Остановка мониторинга...")
        
        try:
            # Остановить Prometheus
            prometheus_cmd = ["kubectl", "delete", "deployment", "prometheus", "-n", "monitoring", "--ignore-not-found=true"]
            subprocess.run(prometheus_cmd, capture_output=True)
            
            # Остановить Grafana
            grafana_cmd = ["kubectl", "delete", "deployment", "grafana", "-n", "monitoring", "--ignore-not-found=true"]
            subprocess.run(grafana_cmd, capture_output=True)
            
            print("✅ Мониторинг остановлен")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка остановки мониторинга: {e}")
            return False
    
    def emergency_stop(self) -> bool:
        """Экстренная остановка всего"""
        
        print("🚨 ЭКСТРЕННАЯ ОСТАНОВКА ORACLE850B")
        print("=" * 50)
        
        success = True
        
        # Остановить Kubernetes
        if not self.kill_kubernetes_resources():
            success = False
        
        # Уничтожить Terraform
        if not self.kill_terraform_resources():
            success = False
        
        # Остановить мониторинг
        if not self.kill_monitoring():
            success = False
        
        # Логирование
        self._log_kill_switch()
        
        if success:
            print("✅ Экстренная остановка завершена успешно")
        else:
            print("❌ Ошибки при экстренной остановке")
        
        return success
    
    def _log_kill_switch(self):
        """Логировать активацию kill switch"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": "kill_switch_activated",
            "config": self.config,
            "status": "completed"
        }
        
        log_file = Path("logs/kill_switch.log")
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")
        
        print(f"📋 Kill switch залогирован: {log_file}")
    
    def pre_flight_check(self) -> Dict[str, Any]:
        """Pre-flight проверки"""
        
        print("🔍 Pre-flight проверки...")
        
        checks = {
            "kubectl_available": False,
            "terraform_available": False,
            "config_valid": False,
            "resources_accessible": False
        }
        
        # Проверка kubectl
        try:
            result = subprocess.run(["kubectl", "version", "--client"], capture_output=True, text=True)
            checks["kubectl_available"] = result.returncode == 0
        except FileNotFoundError:
            checks["kubectl_available"] = False
        
        # Проверка terraform
        try:
            result = subprocess.run(["terraform", "version"], capture_output=True, text=True)
            checks["terraform_available"] = result.returncode == 0
        except FileNotFoundError:
            checks["terraform_available"] = False
        
        # Проверка конфига
        checks["config_valid"] = self.config_file.exists()
        
        # Проверка доступности ресурсов
        try:
            result = subprocess.run(["kubectl", "get", "nodes"], capture_output=True, text=True)
            checks["resources_accessible"] = result.returncode == 0
        except:
            checks["resources_accessible"] = False
        
        # Вывод результатов
        for check, status in checks.items():
            status_icon = "✅" if status else "❌"
            print(f"  {status_icon} {check}: {status}")
        
        all_passed = all(checks.values())
        if all_passed:
            print("✅ Все pre-flight проверки пройдены")
        else:
            print("❌ Некоторые pre-flight проверки не пройдены")
        
        return checks


def main():
    parser = argparse.ArgumentParser(description="Oracle850B Kill Switch")
    parser.add_argument("--emergency-stop", action="store_true", help="Экстренная остановка")
    parser.add_argument("--kill-k8s", action="store_true", help="Остановить Kubernetes")
    parser.add_argument("--kill-terraform", action="store_true", help="Уничтожить Terraform")
    parser.add_argument("--kill-monitoring", action="store_true", help="Остановить мониторинг")
    parser.add_argument("--pre-flight", action="store_true", help="Pre-flight проверки")
    parser.add_argument("--config", default="infra/kill_switch_config.json", help="Конфиг файл")
    
    args = parser.parse_args()
    
    kill_switch = OracleKillSwitch(args.config)
    
    if args.pre_flight:
        checks = kill_switch.pre_flight_check()
        sys.exit(0 if all(checks.values()) else 1)
    
    success = True
    
    if args.emergency_stop:
        success = kill_switch.emergency_stop()
    else:
        if args.kill_k8s:
            success &= kill_switch.kill_kubernetes_resources()
        
        if args.kill_terraform:
            success &= kill_switch.kill_terraform_resources()
        
        if args.kill_monitoring:
            success &= kill_switch.kill_monitoring()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
