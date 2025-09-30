#!/usr/bin/env python3
"""
Oracle850B Direct Upload
Прямая загрузка с токеном
Author: MagistrTheOne|Краснодар|2025
"""

import os
import sys
import argparse
from pathlib import Path
from huggingface_hub import HfApi, login


def upload_direct(token=None):
    """Прямая загрузка с токеном"""
    print("Oracle850B Direct Upload")
    print("=" * 40)

    # Токен из параметра или переменной окружения
    if not token:
        token = os.getenv("HF_TOKEN")
    if not token:
        print("ERROR: HF_TOKEN not set")
        print("HINT: Set HF_TOKEN environment variable or pass as --token")
        return False

    repo_id = "MagistrTheOne/oracle850b-moe"

    try:
        # Логин
        login(token=token)
        print("SUCCESS: Успешный логин в HF Hub")

        # API
        api = HfApi(token=token)

        # Проверка пользователя
        user_info = api.whoami()
        print(f"SUCCESS: Пользователь: {user_info['name']}")

        # Создание репозитория
        try:
            api.create_repo(
                repo_id=repo_id,
                repo_type="model",
                private=False,
                exist_ok=True
            )
            print(f"SUCCESS: Репозиторий создан: {repo_id}")
        except Exception as e:
            print(f"INFO: Репозиторий уже существует: {e}")

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

        print("\nUPLOAD: Загрузка файлов:")
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
                    print(f"SUCCESS: {local_path} -> {repo_path}")
                    success_count += 1
                except Exception as e:
                    print(f"ERROR: {local_path}: {e}")
            else:
                print(f"WARNING: Файл не найден: {local_path}")

        # Загрузка токенайзера
        tokenizer_dir = Path("checkpoints/oracle850b/tokenizer")
        if tokenizer_dir.exists():
            print(f"\nTOKENIZER: Загрузка токенайзера:")
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
                        print(f"SUCCESS: tokenizer/{file_name}")
                        success_count += 1
                    except Exception as e:
                        print(f"ERROR: tokenizer/{file_name}: {e}")
                else:
                    print(f"WARNING: Файл не найден: {file_name}")

        print(f"\nSTATS: Загружено файлов: {success_count}")
        print(f"LINK: Репозиторий: https://huggingface.co/{repo_id}")

        return True

    except Exception as e:
        print(f"ERROR: {e}")
        return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Upload Oracle850B files to Hugging Face")
    parser.add_argument("--token", type=str, help="Hugging Face token")
    parser.add_argument("--repo", type=str, default="MagistrTheOne/oracle850b-moe", help="Repository ID")
    args = parser.parse_args()

    success = upload_direct(token=args.token)
    sys.exit(0 if success else 1)
