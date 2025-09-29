# Changelog

Все значимые изменения в проекте Oracle850B будут документированы в этом файле.

Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.0.0/),
и этот проект придерживается [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Подготовка к релизу v0.2.0-weights
- Smoke-тесты vLLM после загрузки весов
- Обновление MODEL_CARD.md с метриками

## [0.1.2] - 2024-12-19

### Added
- ✅ CI guard workflow для внешних моделей
- ✅ LICENSE (proprietary research)
- ✅ SECURITY.md (контакты, PGP, SLA)
- ✅ .gitattributes с LFS для *.safetensors
- ✅ .env.example для Pro-подготовки
- ✅ Seed evaluation dry-run скрипты
- ✅ Mistake-book (200-500 задач ошибок)
- ✅ Spec-synthetic с автотестами
- ✅ Argo DAG валидация
- ✅ Kill-switch и инфраструктурные скрипты

### Changed
- Улучшена валидация Argo пайплайнов
- Разделены WorkflowTemplate и Workflow в data-pipeline
- Обновлена структура dry-run тестов

### Fixed
- Исправлена валидация WorkflowTemplate в Argo DAG
- Устранены дублирующиеся YAML документы

## [0.1.1] - 2024-12-18

### Added
- ✅ Метаданные модели (config, generation_config, special_tokens_map)
- ✅ MODEL_CARD.md с описанием MoE архитектуры
- ✅ Конфигурации обучения (oracle850b.yaml, zero3_offload.json)
- ✅ Training launcher с elastic resume
- ✅ Инфраструктура Yandex Cloud (Terraform)
- ✅ Helm чарты для Kubernetes
- ✅ Argo пайплайны (data, serving, training)

### Changed
- Обновлена структура конфигураций
- Улучшена документация архитектуры

## [0.1.0] - 2024-12-17

### Added
- ✅ Базовая архитектура Oracle850B MoE
- ✅ Структура проекта и исходный код
- ✅ Конфигурации модели и обучения
- ✅ Скрипты для подготовки данных
- ✅ Инфраструктурные компоненты
- ✅ CI/CD пайплайны

### Technical Details
- **Архитектура**: MoE (Mixture of Experts) с 850B параметров
- **Эксперты**: 64 эксперта, top-k=2
- **Контекст**: 8192 токена
- **Параллелизм**: TP=8, PP=8, SP=true
- **Оптимизация**: DeepSpeed ZeRO-3, offload на NVMe

## [0.0.1] - 2024-12-16

### Added
- 🎯 Инициализация проекта Oracle850B
- 📁 Базовая структура репозитория
- 📝 Первичная документация

---

## Roadmap

### v0.2.0-weights (Planned)
- [ ] Загрузка весов модели в HF Hub
- [ ] Smoke-тесты vLLM
- [ ] Обновление метрик в MODEL_CARD
- [ ] Релизные теги и бейджи

### v0.3.0-eval (Planned)
- [ ] Полная оценка на GSM8K, HumanEval, MMLU
- [ ] Бенчмарки производительности
- [ ] Оптимизация инференса

### v0.4.0-production (Planned)
- [ ] Production-ready сервинг
- [ ] Мониторинг и алерты
- [ ] Автоскейлинг
- [ ] Безопасность и аудит

---

## Breaking Changes

### v0.1.2
- Изменена структура Argo пайплайнов (разделение WorkflowTemplate и Workflow)
- Обновлены пути к конфигурациям

### v0.1.1
- Переименованы некоторые конфигурационные файлы
- Изменена структура метаданных модели

---

## Contributors

- **MagistrTheOne** - Главный разработчик и архитектор
- **M∞1** - Технический консультант

---

## License

Proprietary Research License - см. [LICENSE](LICENSE) для деталей.

---

## Security

Для сообщения о уязвимостях см. [SECURITY.md](SECURITY.md).
