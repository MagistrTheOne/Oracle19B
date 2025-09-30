#!/usr/bin/env python3
"""
Oracle850B Direct Upload
Прямая загрузка с токеном
Author: MagistrTheOne|Краснодар|2025
"""

import os
import sys
from pathlib import Path
from huggingface_hub import HfApi, login


def upload_direct():
    """Прямая загрузка с токеном"""
    print("🚀 Oracle850B Direct Upload")
    print("=" * 40)
    
    # Токен из переменной окружения
    token = os.getenv("HF_TOKEN")
    if not token:
        print("❌ HF_TOKEN не установлен")
        print("💡 Установите: set HF_TOKEN=your_token_here")
        return False

    repo_id = "MagistrTheOne/oracle850b-moe"
    
    try:
        # Логин
        login(token=token)
        print("✅ Успешный логин в HF Hub")
        
        # API
        api = HfApi(token=token)
        
        # Проверка пользователя
        user_info = api.whoami()
        print(f"✅ Пользователь: {user_info['name']}")
        
        # Создание репозитория
        try:
            api.create_repo(
                repo_id=repo_id,
                repo_type="model",
                private=False,
                exist_ok=True
            )
            print(f"✅ Репозиторий создан: {repo_id}")
        except Exception as e:
            print(f"ℹ️  Репозиторий уже существует: {e}")
        
        # Загрузка файлов
        files_to_upload = [
            ("README.md", "README.md"),
            ("MODEL_CARD.md", "MODEL_CARD.md"),
            ("CHANGELOG.md", "CHANGELOG.md"),
            ("LICENSE", "LICENSE"),
            ("SECURITY.md", "SECURITY.md"),
            ("generation_config.json", "generation_config.json"),
            ("special_tokens_map.json", "special_tokens_map.json"),
            ("configs/model/oracle850b.moe.json", "config.json"),
            ("checkpoints/oracle850b/default_intro.txt", "default_intro.txt"),
            ("checkpoints/oracle850b/default_system.txt", "default_system.txt")
        ]
        
        print("\n📋 Загрузка файлов:")
        success_count = 0
        
        for local_path, repo_path in files_to_upload:
            if Path(local_path).exists():
                try:
                    api.upload_file(
                        path_or_fileobj=local_path,
                        path_in_repo=repo_path,
                        repo_id=repo_id,
                        repo_type="model"
                    )
                    print(f"✅ {local_path} → {repo_path}")
                    success_count += 1
                except Exception as e:
                    print(f"❌ {local_path}: {e}")
            else:
                print(f"⚠️  Файл не найден: {local_path}")
        
        # Загрузка токенайзера
        tokenizer_dir = Path("checkpoints/oracle850b/tokenizer")
        if tokenizer_dir.exists():
            print(f"\n🔤 Загрузка токенайзера:")
            tokenizer_files = ["tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"]
            
            for file_name in tokenizer_files:
                file_path = tokenizer_dir / file_name
                if file_path.exists():
                    try:
                        api.upload_file(
                            path_or_fileobj=str(file_path),
                            path_in_repo=f"tokenizer/{file_name}",
                            repo_id=repo_id,
                            repo_type="model"
                        )
                        print(f"✅ tokenizer/{file_name}")
                        success_count += 1
                    except Exception as e:
                        print(f"❌ tokenizer/{file_name}: {e}")
                else:
                    print(f"⚠️  Файл не найден: {file_name}")
        
        print(f"\n📊 Загружено файлов: {success_count}")
        print(f"🔗 Репозиторий: https://huggingface.co/{repo_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False


if __name__ == "__main__":
    success = upload_direct()
    sys.exit(0 if success else 1)
