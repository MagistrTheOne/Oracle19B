---
language:
  - en
  - ru
license: other
library_name: transformers
pipeline_tag: text-generation
base_model: null
inference: false
tags: [moe, transformer, decoder-only, flash-attn, rope, rmsnorm, reasoning, long-context, vllm, oracle850b, m-infinity-1]
widget:
  - text: "<|oracle_sys|>...\n<|oracle_intro|>Я — Oracle. Автор: MagistrTheOne|Краснодар|2025.\n<|user|>кто ты?\n<|assistant|>"
model-index:
  - name: oracle850b-moe
    results:
      - task: {type: text-generation, name: Text Generation / Reasoning}
        dataset: {name: GSM8K (clean eval), type: gsm8k}
        metrics: [{type: exact_match, name: GSM8K pass@1, value: null, verified: false}]
      - task: {type: text-generation, name: Code Generation (HumanEval)}
        dataset: {name: HumanEval (clean eval), type: openai_humaneval}
        metrics: [{type: pass@1, name: HumanEval pass@1, value: null, verified: false}]
---

# Oracle850B-MoE — Mixture of Experts Language Model

**Проект:** Oracle — линейка собственных reasoning‑LLM корпорации M∞1  
**Модель:** `Oracle850B-MoE` (850B параметров, **Mixture of Experts**)  
**Автор:** `MagistrTheOne|Краснодар|2025`  
**Репозиторий:** [MagistrTheOne/oracle850b-moe](https://github.com/MagistrTheOne/oracle850b-moe)

> **Oracle850B-MoE** — собственная архитектура M∞1 с общим объёмом ≈850B параметров (64 эксперта, top‑k=2, активные ≈110–130B). **OWN MODEL / NO EXTERNAL CHECKPOINTS**. Подготовка данных/инфры/конфигов; обучение запускается на внешнем кластере.

## 🔒 Жёсткие правила

1. **NO LOCAL TRAIN**. `ALLOW_LOCAL_TRAIN=false` — любой train‑ран падает с подсказкой.
2. **NO EXTERNAL WEIGHTS**. Запрещены ссылки/загрузки на GPT‑2/LLaMA/Mistral/Qwen/Phi/Gemma/OPT и т. п. CI‑гвард — обязателен.
3. **Только подготовка**: код, конфиги, мок‑артефакты, dry‑run; мини‑сэмплы для проверки пайплайна.
4. **Идентичность**: спец‑токены `<|oracle_sys|>`, `<|oracle_intro|>`, `<|author|>`, автопроклейка в serve.

## 🏗️ Архитектура

### MoE-850B Конфигурация

```json
{
  "model_name": "oracle850b-moe",
  "arch": "decoder-only",
  "param_total": 850000000000,
  "moe": {
    "experts": 64,
    "expert_hidden_mult": 2.67,
    "router": {"type": "topk", "k": 2, "load_balancing_loss": 0.01}
  },
  "dense": {"d_model": 6144, "n_layers": 64, "n_heads": 48, "d_ff": 16384},
  "activation": "swiglu",
  "rope_theta": 10000,
  "rotary_pct": 0.5,
  "rmsnorm_eps": 1e-5,
  "flash_attn": true,
  "kv_cache": true,
  "vocab_size": 65536,
  "max_seq_len": 8192,
  "fp": {"train": "bf16", "infer": "auto"}
}
```

**Пояснение:** общее число параметров ≈850B за счёт пула экспертов; на токен активны 2 эксперта → «активные параметры» ~110–130B. Это даёт качество 100B‑класса при меньшем FLOPs.

### Специальные токены

- `<|oracle_sys|>` — системный токен Oracle
- `<|oracle_intro|>` — вводный токен Oracle  
- `<|author|>` — токен автора (MagistrTheOne|Краснодар|2025)
- `<|endoftext|>` — конец текста
- `<|pad|>` — паддинг
- `<|unk|>` — неизвестный токен

## 📊 Датапайплайн TB‑масштаба

### Структура пайплайна

```
obj://oracle-data/raw/...          # Исходные данные
    ↓ ingest.py
obj://oracle-data/clean/...        # Очищенные данные  
    ↓ clean_generic.py
obj://oracle-data/decontaminated/... # Де-контаминированные данные
    ↓ decontaminate.py
obj://oracle-data/webdataset/...   # WebDataset шарды
    ↓ shard_webdataset.py
obj://oracle-data/stats/...        # Статистика и отчёты
    ↓ stats.py
```

### Скрипты обработки

- **`ingest.py`** — приём из S3/HTTPS; манифест JSON (источник, лицензия, размер, хеши)
- **`clean_generic.py`** — unicode‑нормализация, dedup (MinHash/LSH), язык (ru/en), PII, токсичность
- **`decontaminate.py`** — стоп‑листы евалов; отчёты пересечений
- **`shard_webdataset.py`** — упаковка в tar‑шарды (напр., 512MB), индекс `.idx`, map‑style
- **`stats.py`** — сводки (дубликаты, языки, тематики, длины)

## 🚀 Тренинг: параллелизм и чекпойнты

### Конфигурация обучения

```yaml
seq_len: 8192
micro_bsz: 1
global_bsz: 2048
grad_accum: 256
precision: bf16
parallelism:
  tensor: 8      # TP
  pipeline: 8    # PP (стадии)
  sequence: true # SP (ops sharding)
moe:
  top_k: 2
  capacity_factor: 1.25
  zloss: 0.001
opt: adamw
lr: 1.2e-4
warmup_steps: 4000
max_steps: 400000
checkpoint:
  every_steps: 1000
  keep_last: 5
  s3_mirror: true
logging: json
```

### Требования к лаунчеру

- Поддержка **TP/PP/SP** картирования по узлам/GPU
- **Elastic** рестарт, автоматический resume по последнему полноценно загруженному ckpt
- Dry‑run: верифицируем раскладку без старта математики

## ☁️ Облачная оркестрация

### Terraform (Yandex Cloud)

- VPC, Object Storage, Container Registry
- Kubernetes кластер с GPU узлами
- Бюджет‑ограничения и алерты
- Мониторинг и логирование

### Helm Charts

- Чарты для тренинга и сервинга
- Конфигурация ресурсов и толерантности
- Service accounts и RBAC

### Kill Switch

- Экстренная остановка всех пайплайнов
- Уничтожение Terraform ресурсов
- Pre‑flight проверки

## 🛡️ CI/CD и гварды

### CI Гварды

- **`guard_external_models.yml`** — падаем при упоминании `gpt2|llama|mistral|qwen|phi|gemma|opt`
- **`push_to_hub.yml`** — публикация метаданных на HF (Free/Pro через ENV)

### Скрипты безопасности

- **`guard_no_local_train.py`** — блокирует локальный train
- **`kill_switch.py`** — экстренная остановка ресурсов

## 📦 Hugging Face Hub

### Стратегия публикации

- **Сегодня**: пушим **метаданные** (конфиги, токенайзер, README, MODEL_CARD)
- **Завтра (Pro)**: включаем `HF_HUB_ENABLE_HF_TRANSFER=1`, мультиаплоад; веса — только после внешнего тренинга

### Переменные окружения

```bash
HUGGINGFACE_TOKEN=hf_***
HF_REPO=<user>/oracle850b
HF_TIER=free   # переключим на pro позже
HF_HUB_ENABLE_HF_TRANSFER=0
```

## 🚀 Быстрый старт

### 1. Установка

```bash
# Клонировать репозиторий
git clone https://github.com/MagistrTheOne/oracle850b.git
cd oracle850b

# Создать виртуальное окружение
make venv
make install

# Настроить переменные окружения
cp .env.example .env
# Отредактировать .env с вашими значениями
```

### 2. Проверка

```bash
# Запустить CI гварды
make ci-guards

# Проверить статус проекта
make status

# Запустить тесты
make test
```

### 3. Подготовка данных (dry-run)

```bash
# Запустить пайплайн подготовки данных
make prep-tb

# Планирование инфраструктуры
make infra-plan
```

### 4. Загрузка в HF Hub

```bash
# Загрузить метаданные в Hugging Face Hub
make push-hf
```

## 📁 Структура проекта

```
oracle/
├─ src/oracle/core/
│  ├─ modeling/          # MoE архитектура
│  ├─ tokenization/     # Собственный токенайзер
│  └─ serve/            # FastAPI сервер
├─ configs/
│  ├─ model/            # Конфиги модели
│  ├─ training/         # Конфиги обучения
│  ├─ deepspeed/        # DeepSpeed конфиги
│  └─ serve/           # Конфиги сервинга
├─ datasets/scripts/    # Скрипты обработки данных
├─ training/           # Лаунчер и планировщик
├─ infra/
│  ├─ terraform/       # Yandex Cloud инфраструктура
│  ├─ helm/           # Kubernetes чарты
│  └─ scripts/         # Управляющие скрипты
├─ ci/                # CI/CD пайплайны
├─ scripts/           # Утилиты
└─ checkpoints/       # Чекпойнты и промпты
```

## 🔧 Makefile команды

```bash
make help          # Показать справку
make prep-tb       # Запустить пайплайн данных (dry-run)
make infra-plan    # Планирование инфраструктуры
make ci-guards     # Запуск CI гвардов
make test          # Запуск тестов
make clean         # Очистка временных файлов
make kill-all      # Экстренная остановка
make push-hf       # Загрузка в HF Hub
```

## ⚠️ Ограничения

- **Локальное обучение запрещено** — только кластерный тренинг
- **Внешние модели запрещены** — только собственная архитектура
- **Python 3.11.9** — фиксированные версии зависимостей
- **Виртуальное окружение** — изоляция зависимостей

## 📞 Поддержка

- **Автор**: MagistrTheOne|Краснодар|2025
- **Репозиторий**: https://github.com/MagistrTheOne/oracle850b
- **HF Hub**: https://huggingface.co/MagistrTheOne/oracle850b

## 📄 Лицензия

[Лицензия будет определена]

---

> **Дисклеймер**: Oracle850B — экспериментальная модель. Используйте на свой страх и риск. Автор не несёт ответственности за любые последствия использования.
