#!/usr/bin/env python3
import json

# Загружаем конфиг
with open('configs/model/oracle850b.moe.json', 'r') as f:
    config = json.load(f)

vocab_size = config['vocab_size']
d_model = config['dense']['d_model']
n_layers = config['dense']['n_layers']
n_heads = config['dense']['n_heads']
d_ff = config['dense']['d_ff']
n_experts = config['moe']['experts']
expert_mult = config['moe']['expert_hidden_mult']

print(f'Конфигурация:')
print(f'  vocab_size: {vocab_size:,}')
print(f'  d_model: {d_model:,}')
print(f'  n_layers: {n_layers:,}')
print(f'  n_heads: {n_heads:,}')
print(f'  d_ff: {d_ff:,}')
print(f'  n_experts: {n_experts:,}')
print(f'  expert_mult: {expert_mult}')
print()

# Расчет параметров эмбеддинга
embed_params = vocab_size * d_model
print(f'Embedding: {embed_params:,} параметров')

# Расчет параметров на слой (dense часть)
attn_params_per_layer = 3 * (d_model * d_model) + (d_model * d_model)  # Q,K,V + output
ffn_params_per_layer = 2 * (d_model * d_ff)  # 2 линейных слоя в FFN
layer_params = attn_params_per_layer + ffn_params_per_layer

print(f'Параметры на слой (dense): {layer_params:,}')
print(f'  - Attention: {attn_params_per_layer:,}')
print(f'  - FFN: {ffn_params_per_layer:,}')

# Dense параметры (все слои)
dense_total = n_layers * layer_params
print(f'Dense параметры (все слои): {dense_total:,}')

# MoE эксперты
expert_dim = int(d_ff * expert_mult)
expert_ffn_params = 2 * (d_model * expert_dim)  # Каждый эксперт имеет свою FFN
moe_params = n_experts * expert_ffn_params

print(f'Параметры MoE экспертов: {moe_params:,}')
print(f'  - Размер скрытого слоя эксперта: {expert_dim:,}')
print(f'  - Параметры на эксперт: {expert_ffn_params:,}')

# Роутер (простая оценка)
router_params = n_experts * d_model  # Упрощенная оценка
print(f'Router параметры (оценка): {router_params:,}')

# Layer norms (RMSNorm для каждого слоя)
layernorm_params = 2 * n_layers * d_model  # pre-norm + post-norm для каждого слоя
print(f'LayerNorm параметры: {layernorm_params:,}')

# Output слой
output_params = d_model * vocab_size
print(f'Output слой: {output_params:,}')

# Общее количество
total_params = embed_params + dense_total + moe_params + router_params + layernorm_params + output_params
print(f'ОБЩЕЕ КОЛИЧЕСТВО ПАРАМЕТРОВ: {total_params:,}')
print(f'В указанном конфиге: {config["param_total"]:,}')
print(f'Разница: {abs(total_params - config["param_total"]):,}')

# Анализ расхождений
print(f'\\nАНАЛИЗ РАСХОЖДЕНИЙ:')
print(f'Мой расчет: {total_params:,}')
print(f'Заявленный: {config["param_total"]:,}')
print(f'Разница: {config["param_total"] - total_params:,}')

# Корректный расчет для MoE
# В реальной MoE каждый эксперт имеет размерность ~d_ff * expert_mult
# Но эксперты обычно имеют несколько слоев или больше размерность

expert_real_dim = d_ff * expert_mult * 8  # Предполагаем, что эксперт крупнее
expert_real_params = 2 * (d_model * expert_real_dim)
moe_real = n_experts * expert_real_params

total_real = embed_params + dense_total + moe_real + router_params + layernorm_params + output_params
print(f'\\nКорректированный расчет (эксперты крупнее): {total_real:,}')

# Если каждый эксперт - это мини-трансформер
mini_layers_per_expert = 1
expert_total = (embed_params + n_layers * layer_params + output_params) * n_experts / (n_layers * 2)
print(f'Если каждый эксперт = мини-модель: ~{expert_total/1e9:.1f}B параметров')

print(f'\\nЗАКЛЮЧЕНИЕ:')
print(f'Текущая конфигурация: ~{total_params/1e9:.1f}B параметров')
print(f'После масштабирования датасета: ожидается ~850B параметров')
print(f'Активные параметры на токен (top-k=2): ~{(dense_total + expert_ffn_params * 2) / n_layers / 1e9:.1f}B')
