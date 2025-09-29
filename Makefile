# Oracle850B Makefile
# Author: MagistrTheOne|Краснодар|2025

.ONESHELL:
.PHONY: help prep-tb infra-plan ci-guards clean install test venv sync bootstrap

# Переменные
PYTHON := python3.11
VENV := .venv
ACTIVATE := source $(VENV)/bin/activate
PIP := $(VENV)/bin/pip
PYTHON_VENV := $(VENV)/bin/python

# Цвета для вывода
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[0;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

help: ## Показать справку
	@echo "$(BLUE)Oracle850B Makefile$(NC)"
	@echo "=================="
	@echo ""
	@echo "$(GREEN)Основные команды:$(NC)"
	@echo "  prep-tb      - Запустить пайплайн подготовки данных (dry-run)"
	@echo "  infra-plan   - Планирование инфраструктуры (terraform plan)"
	@echo "  ci-guards    - Запуск CI гвардов"
	@echo "  install      - Установка зависимостей"
	@echo "  test         - Запуск тестов"
	@echo "  clean        - Очистка временных файлов"
	@echo ""
	@echo "$(GREEN)Разработка:$(NC)"
	@echo "  venv         - Создать виртуальное окружение"
	@echo "  deps         - Установить зависимости"
	@echo "  lint         - Проверка кода"
	@echo "  format       - Форматирование кода"
	@echo ""

# Установка и настройка
venv: ## Создать виртуальное окружение
	@echo "$(BLUE)Создание виртуального окружения...$(NC)"
	$(PYTHON) -m venv $(VENV)
	$(ACTIVATE); pip -q install -U pip wheel
	@echo "$(GREEN)✅ Виртуальное окружение создано$(NC)"

bootstrap: ## Полная настройка проекта (venv + deps + проверки)
	@echo "$(BLUE)🚀 Полная настройка Oracle850B...$(NC)"
	chmod +x scripts/bootstrap.sh
	./scripts/bootstrap.sh
	@echo "$(GREEN)✅ Bootstrap завершен$(NC)"

sync: ## Синхронизировать зависимости (venv required)
	@echo "$(BLUE)🔄 Синхронизация зависимостей...$(NC)"
	$(ACTIVATE); pip -q install -r requirements.lock || true
	$(ACTIVATE); pip -q install -r requirements.in && pip freeze > requirements.lock
	@echo "$(GREEN)✅ Зависимости синхронизированы$(NC)"

install: venv sync ## Установить все зависимости
	@echo "$(GREEN)✅ Установка завершена$(NC)"

# Подготовка данных
prep-tb: ## Запустить пайплайн подготовки данных (dry-run)
	@echo "$(BLUE)🚀 Запуск пайплайна подготовки данных Oracle850B$(NC)"
	@echo "$(YELLOW)⚠️  Это dry-run - реальные данные не обрабатываются$(NC)"
	@echo ""
	
	@echo "$(BLUE)1. Ингрест данных...$(NC)"
	$(PYTHON_VENV) datasets/scripts/ingest.py --https-urls "https://example.com/data1.txt" "https://example.com/data2.txt" --max-files 10 --output-dir data/raw
	@echo "$(GREEN)✅ Ингрест завершен$(NC)"
	
	@echo "$(BLUE)2. Очистка данных...$(NC)"
	$(PYTHON_VENV) datasets/scripts/clean_generic.py --input-file data/raw/example.com_data1.txt --output-dir data/clean
	@echo "$(GREEN)✅ Очистка завершена$(NC)"
	
	@echo "$(BLUE)3. Де-контаминация...$(NC)"
	$(PYTHON_VENV) datasets/scripts/decontaminate.py --input-file data/clean/cleaned_example.com_data1.txt --output-dir data/decontaminated
	@echo "$(GREEN)✅ Де-контаминация завершена$(NC)"
	
	@echo "$(BLUE)4. Шардинг в WebDataset...$(NC)"
	$(PYTHON_VENV) datasets/scripts/shard_webdataset.py --input-file data/decontaminated/decontaminated_cleaned_example.com_data1.txt --output-dir data/webdataset --split train
	@echo "$(GREEN)✅ Шардинг завершен$(NC)"
	
	@echo "$(BLUE)5. Статистика данных...$(NC)"
	$(PYTHON_VENV) datasets/scripts/stats.py --input-file data/decontaminated/decontaminated_cleaned_example.com_data1.txt --output-dir data/stats --quality-report
	@echo "$(GREEN)✅ Статистика готова$(NC)"
	
	@echo ""
	@echo "$(GREEN)🎉 Пайплайн подготовки данных завершен!$(NC)"
	@echo "$(YELLOW)💡 Для реальных данных замените URL на ваши источники$(NC)"

# Инфраструктура
infra-plan: ## Планирование инфраструктуры (terraform plan)
	@echo "$(BLUE)🏗️  Планирование инфраструктуры Oracle850B$(NC)"
	@echo ""
	
	@echo "$(BLUE)1. Проверка Terraform...$(NC)"
	cd infra/terraform && terraform init
	@echo "$(GREEN)✅ Terraform инициализирован$(NC)"
	
	@echo "$(BLUE)2. Планирование ресурсов...$(NC)"
	cd infra/terraform && terraform plan -var-file=terraform.tfvars.example
	@echo "$(GREEN)✅ План инфраструктуры готов$(NC)"
	
	@echo ""
	@echo "$(YELLOW)💡 Для применения инфраструктуры используйте: terraform apply$(NC)"
	@echo "$(YELLOW)💡 Не забудьте настроить terraform.tfvars$(NC)"

# CI и гварды
ci-guards: ## Запуск CI гвардов
	@echo "$(BLUE)🛡️  Запуск CI гвардов Oracle850B$(NC)"
	@echo ""
	
	@echo "$(BLUE)1. Проверка внешних моделей...$(NC)"
	$(PYTHON_VENV) -c "
	import subprocess
	import sys
	
	# Проверка запрещенных моделей
	forbidden = ['gpt2', 'llama', 'mistral', 'qwen', 'phi', 'gemma', 'opt']
	found = False
	
	for model in forbidden:
		result = subprocess.run(['grep', '-r', '-i', model, '--include=*.py', '--include=*.json', '--include=*.yaml', '.'], 
		                      capture_output=True, text=True)
		if result.returncode == 0:
			print(f'❌ Найдено упоминание {model}')
			found = True
	
	if found:
		print('❌ Обнаружены запрещенные внешние модели!')
		sys.exit(1)
	else:
		print('✅ Запрещенные модели не найдены')
	"
	@echo "$(GREEN)✅ Проверка внешних моделей пройдена$(NC)"
	
	@echo "$(BLUE)2. Проверка локального обучения...$(NC)"
	$(PYTHON_VENV) scripts/guard_no_local_train.py --check
	@echo "$(GREEN)✅ Гвард локального обучения активен$(NC)"
	
	@echo "$(BLUE)3. Проверка архитектуры Oracle850B...$(NC)"
	@test -f "configs/model/oracle850b.moe.json" || (echo "❌ Отсутствует конфиг модели" && exit 1)
	@test -f "src/oracle/core/modeling/transformer_moe.py" || (echo "❌ Отсутствует MoE трансформер" && exit 1)
	@echo "$(GREEN)✅ Архитектура Oracle850B проверена$(NC)"
	
	@echo ""
	@echo "$(GREEN)🎉 Все CI гварды пройдены!$(NC)"

# Тестирование
test: ## Запуск тестов
	@echo "$(BLUE)🧪 Запуск тестов Oracle850B$(NC)"
	@echo ""
	
	@echo "$(BLUE)1. Тест токенайзера...$(NC)"
	$(PYTHON_VENV) -c "
	import sys
	sys.path.append('src')
	from oracle.core.tokenization.build_tokenizer import OracleTokenizerBuilder
	builder = OracleTokenizerBuilder()
	print('✅ Токенайзер инициализирован')
	"
	@echo "$(GREEN)✅ Тест токенайзера пройден$(NC)"
	
	@echo "$(BLUE)2. Тест конфигов...$(NC)"
	$(PYTHON_VENV) -c "
	import json
	with open('configs/model/oracle850b.moe.json', 'r') as f:
		config = json.load(f)
	assert config['model_name'] == 'oracle850b-moe'
	assert config['param_total'] == 850000000000
	print('✅ Конфиг модели валиден')
	"
	@echo "$(GREEN)✅ Тест конфигов пройден$(NC)"
	
	@echo "$(BLUE)3. Тест тренинг-лаунчера...$(NC)"
	$(PYTHON_VENV) training/launcher.py --config configs/training/oracle850b.yaml --dry-run
	@echo "$(GREEN)✅ Тест лаунчера пройден$(NC)"
	
	@echo ""
	@echo "$(GREEN)🎉 Все тесты пройдены!$(NC)"

# Разработка
lint: ## Проверка кода
	@echo "$(BLUE)🔍 Проверка кода...$(NC)"
	$(PIP) install flake8 black isort
	flake8 src/ training/ scripts/ --max-line-length=120 --ignore=E203,W503
	@echo "$(GREEN)✅ Проверка кода завершена$(NC)"

format: ## Форматирование кода
	@echo "$(BLUE)🎨 Форматирование кода...$(NC)"
	$(PIP) install black isort
	black src/ training/ scripts/ --line-length=120
	isort src/ training/ scripts/ --profile=black
	@echo "$(GREEN)✅ Код отформатирован$(NC)"

# Очистка
clean: ## Очистка временных файлов
	@echo "$(BLUE)🧹 Очистка временных файлов...$(NC)"
	rm -rf __pycache__/
	rm -rf src/**/__pycache__/
	rm -rf training/**/__pycache__/
	rm -rf scripts/**/__pycache__/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf data/raw/
	rm -rf data/clean/
	rm -rf data/decontaminated/
	rm -rf data/webdataset/
	rm -rf data/stats/
	rm -rf logs/
	@echo "$(GREEN)✅ Очистка завершена$(NC)"

# Kill switch
kill-all: ## Экстренная остановка всех ресурсов
	@echo "$(RED)🚨 ЭКСТРЕННАЯ ОСТАНОВКА ORACLE850B$(NC)"
	@echo "$(YELLOW)⚠️  Это остановит все Kubernetes ресурсы и уничтожит Terraform инфраструктуру$(NC)"
	@read -p "Вы уверены? (yes/no): " confirm && [ "$$confirm" = "yes" ]
	$(PYTHON_VENV) infra/scripts/kill_switch.py --emergency-stop
	@echo "$(GREEN)✅ Экстренная остановка завершена$(NC)"

# HF Hub
push-hf: ## Загрузка метаданных в Hugging Face Hub
	@echo "$(BLUE)📤 Загрузка метаданных в Hugging Face Hub...$(NC)"
	$(PYTHON_VENV) scripts/hf_upload.py
	@echo "$(GREEN)✅ Метаданные загружены в HF Hub$(NC)"

# Статус
status: ## Показать статус проекта
	@echo "$(BLUE)📊 Статус Oracle850B$(NC)"
	@echo "=================="
	@echo ""
	@echo "$(GREEN)Структура проекта:$(NC)"
	@find . -type f -name "*.py" | wc -l | xargs echo "  Python файлов:"
	@find . -type f -name "*.json" | wc -l | xargs echo "  JSON файлов:"
	@find . -type f -name "*.yaml" -o -name "*.yml" | wc -l | xargs echo "  YAML файлов:"
	@echo ""
	@echo "$(GREEN)Конфигурация:$(NC)"
	@test -f "configs/model/oracle850b.moe.json" && echo "  ✅ Конфиг модели" || echo "  ❌ Конфиг модели"
	@test -f "configs/training/oracle850b.yaml" && echo "  ✅ Конфиг обучения" || echo "  ❌ Конфиг обучения"
	@test -f "configs/deepspeed/zero3_offload.json" && echo "  ✅ Конфиг DeepSpeed" || echo "  ❌ Конфиг DeepSpeed"
	@echo ""
	@echo "$(GREEN)Инфраструктура:$(NC)"
	@test -d "infra/terraform" && echo "  ✅ Terraform" || echo "  ❌ Terraform"
	@test -d "infra/helm" && echo "  ✅ Helm" || echo "  ❌ Helm"
	@test -f "infra/scripts/kill_switch.py" && echo "  ✅ Kill Switch" || echo "  ❌ Kill Switch"
	@echo ""
	@echo "$(GREEN)CI/CD:$(NC)"
	@test -f "ci/guard_external_models.yml" && echo "  ✅ Гвард внешних моделей" || echo "  ❌ Гвард внешних моделей"
	@test -f "ci/push_to_hub.yml" && echo "  ✅ Push to Hub" || echo "  ❌ Push to Hub"
