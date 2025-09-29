#!/usr/bin/env python3
"""
Гвард против локального обучения Oracle850B
Author: MagistrTheOne|Краснодар|2025
"""

import os
import sys
import argparse


def check_local_train_guard():
    """Проверить гвард против локального обучения"""
    
    # Проверка переменной окружения
    if os.getenv("ALLOW_LOCAL_TRAIN", "false").lower() == "true":
        print("⚠️  ALLOW_LOCAL_TRAIN=true - локальное обучение разрешено")
        return True
    
    # Проверка аргументов командной строки
    if "--local-train" in sys.argv or "-l" in sys.argv:
        print("❌ Локальное обучение запрещено для Oracle850B")
        print("💡 Используйте кластерный тренинг с TP/PP/SP")
        print("💡 Установите ALLOW_LOCAL_TRAIN=true для принудительного разрешения")
        sys.exit(1)
    
    print("✅ Гвард локального обучения активен")
    return False


def main():
    parser = argparse.ArgumentParser(description="Гвард против локального обучения")
    parser.add_argument("--check", action="store_true", help="Проверить гвард")
    parser.add_argument("--force-allow", action="store_true", help="Принудительно разрешить")
    
    args = parser.parse_args()
    
    if args.force_allow:
        os.environ["ALLOW_LOCAL_TRAIN"] = "true"
        print("🔓 Локальное обучение принудительно разрешено")
        return
    
    if args.check:
        check_local_train_guard()


if __name__ == "__main__":
    main()
