#!/usr/bin/env python3
"""
Oracle850B Hugging Face Upload
Загрузка метаданных в HF Hub
Author: MagistrTheOne|Краснодар|2025
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any
from datetime import datetime

from huggingface_hub import HfApi, Repository
from huggingface_hub.utils import RepositoryNotFoundError


class OracleHFUploader:
    """Загрузчик метаданных Oracle850B в Hugging Face Hub"""
    
    def __init__(self, token: str = None, repo_id: str = None):
        self.token = token or os.getenv("HUGGINGFACE_TOKEN")
        self.repo_id = repo_id or os.getenv("HF_REPO", "MagistrTheOne/oracle850b-moe")
        
        if not self.token:
            raise ValueError("Hugging Face token не найден. Установите HUGGINGFACE_TOKEN")
        
        self.api = HfApi(token=self.token)
        
    def create_repository(self) -> bool:
        """Создать репозиторий на HF Hub"""
        
        try:
            print(f"🔄 Создание репозитория: {self.repo_id}")
            
            # Проверить существование репозитория
            try:
                self.api.repo_info(repo_id=self.repo_id, repo_type="model")
                print(f"✅ Репозиторий {self.repo_id} уже существует")
                return True
            except RepositoryNotFoundError:
                pass
            
            # Создать репозиторий
            self.api.create_repo(
                repo_id=self.repo_id,
                repo_type="model",
                private=False,
                exist_ok=True
            )
            
            print(f"✅ Репозиторий {self.repo_id} создан")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка создания репозитория: {e}")
            return False
    
    def upload_metadata(self) -> bool:
        """Загрузить метаданные модели"""
        
        try:
            print("🔄 Загрузка метаданных Oracle850B...")
            
            # Создать временную директорию
            temp_dir = Path("temp_hf_upload")
            temp_dir.mkdir(exist_ok=True)
            
            # Копировать файлы метаданных
            files_to_upload = [
                ("README.md", "README.md"),
                ("MODEL_CARD.md", "MODEL_CARD.md"),
                ("configs/model/oracle850b.moe.json", "config.json"),
                ("checkpoints/oracle850b/default_system.txt", "default_system.txt"),
                ("checkpoints/oracle850b/default_intro.txt", "default_intro.txt"),
            ]
            
            for src_path, dst_name in files_to_upload:
                src = Path(src_path)
                if src.exists():
                    dst = temp_dir / dst_name
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    
                    # Копировать файл
                    with open(src, 'r', encoding='utf-8') as f:
                        content = f.read()
                    with open(dst, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    print(f"  ✅ {src_path} -> {dst_name}")
                else:
                    print(f"  ⚠️  Файл не найден: {src_path}")
            
            # Копировать токенайзер
            tokenizer_dir = Path("checkpoints/oracle850b/tokenizer")
            if tokenizer_dir.exists():
                hf_tokenizer_dir = temp_dir / "tokenizer"
                hf_tokenizer_dir.mkdir(exist_ok=True)
                
                for tokenizer_file in tokenizer_dir.glob("*"):
                    if tokenizer_file.is_file():
                        dst_file = hf_tokenizer_dir / tokenizer_file.name
                        with open(tokenizer_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                        with open(dst_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"  ✅ tokenizer/{tokenizer_file.name}")
            
            # Создать .gitattributes
            gitattributes_content = """*.json linguist-language=JSON
*.txt linguist-language=Text
*.md linguist-language=Markdown
tokenizer/* linguist-vendored
"""
            with open(temp_dir / ".gitattributes", 'w', encoding='utf-8') as f:
                f.write(gitattributes_content)
            
            # Создать .gitignore
            gitignore_content = """# Model weights (too large for free tier)
*.bin
*.safetensors
*.pt
*.pth
*.ckpt

# Training artifacts
logs/
checkpoints/oracle850b/step-*/

# Temporary files
.DS_Store
__pycache__/
*.pyc
"""
            with open(temp_dir / ".gitignore", 'w', encoding='utf-8') as f:
                f.write(gitignore_content)
            
            # Загрузить файлы
            print("📤 Загрузка файлов в HF Hub...")
            for file_path in temp_dir.rglob("*"):
                if file_path.is_file():
                    relative_path = file_path.relative_to(temp_dir)
                    
                    with open(file_path, 'rb') as f:
                        self.api.upload_file(
                            path_or_fileobj=f,
                            path_in_repo=str(relative_path),
                            repo_id=self.repo_id,
                            repo_type="model"
                        )
                    
                    print(f"  ✅ Загружен: {relative_path}")
            
            # Очистить временную директорию
            import shutil
            shutil.rmtree(temp_dir)
            
            print("✅ Метаданные успешно загружены в HF Hub")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка загрузки метаданных: {e}")
            return False
    
    def update_repository_info(self) -> bool:
        """Обновить информацию о репозитории"""
        
        try:
            print("🔄 Обновление информации репозитория...")
            
            # Обновить видимость
            self.api.update_repo_visibility(
                repo_id=self.repo_id,
                private=False
            )
            
            # Обновить описание
            self.api.update_repo_visibility(
                repo_id=self.repo_id,
                private=False
            )
            
            print("✅ Информация репозитория обновлена")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка обновления информации: {e}")
            return False
    
    def upload_all(self) -> bool:
        """Загрузить все метаданные"""
        
        print("🚀 Загрузка Oracle850B в Hugging Face Hub")
        print("=" * 50)
        
        success = True
        
        # Создать репозиторий
        if not self.create_repository():
            success = False
        
        # Загрузить метаданные
        if not self.upload_metadata():
            success = False
        
        # Обновить информацию
        if not self.update_repository_info():
            success = False
        
        if success:
            print("\n✅ Oracle850B успешно загружен в HF Hub!")
            print(f"🔗 https://huggingface.co/{self.repo_id}")
            print("💡 Веса модели будут загружены после обучения на кластере")
        else:
            print("\n❌ Ошибки при загрузке в HF Hub")
        
        return success


def main():
    parser = argparse.ArgumentParser(description="Oracle850B HF Hub Upload")
    parser.add_argument("--token", help="Hugging Face token")
    parser.add_argument("--repo", help="Repository ID")
    parser.add_argument("--create-only", action="store_true", help="Только создать репозиторий")
    parser.add_argument("--metadata-only", action="store_true", help="Только загрузить метаданные")
    
    args = parser.parse_args()
    
    uploader = OracleHFUploader(token=args.token, repo_id=args.repo)
    
    if args.create_only:
        success = uploader.create_repository()
    elif args.metadata_only:
        success = uploader.upload_metadata()
    else:
        success = uploader.upload_all()
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
