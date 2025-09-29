# VLLM Adapter для Oracle850B

## Конфигурация VLLM

```json
{
  "engine": {
    "tensor_parallel_size": 8,
    "pipeline_parallel_size": 8
  },
  "max_model_len": 8192,
  "dtype": "auto",
  "trust_remote_code": true,
  "enforce_eager": false,
  "max_num_batched_tokens": 8192,
  "max_num_seqs": 256,
  "disable_log_stats": false,
  "gpu_memory_utilization": 0.9,
  "swap_space": 4,
  "cpu_offload_gb": 0,
  "block_size": 16,
  "seed": 0,
  "revision": null,
  "code_revision": null,
  "tokenizer": null,
  "tokenizer_mode": "auto",
  "skip_tokenizer_init": false,
  "no_tokenizer": false,
  "tokenizer_revision": null,
  "quantization": null,
  "load_format": "auto",
  "download_dir": null,
  "use_np_weights_in_load": false,
  "disable_custom_all_reduce": false,
  "enforce_eager": false,
  "max_context_len_to_capture": 8192
}
```

## Запуск с VLLM

```bash
python -m vllm.entrypoints.openai.api_server \
    --model oracle850b-moe \
    --tensor-parallel-size 8 \
    --pipeline-parallel-size 8 \
    --max-model-len 8192 \
    --dtype auto \
    --trust-remote-code \
    --port 8000
```

## MoE-специфичные настройки

```json
{
  "moe": {
    "top_k": 2,
    "capacity_factor": 1.25,
    "load_balancing_loss": 0.01
  }
}
```
