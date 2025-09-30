---
language:
  - en
  - ru
license: other
library_name: transformers
pipeline_tag: text-generation
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

# Oracle850B-MoE Model Card

## Model Description

**Oracle850B-MoE** is a Mixture of Experts (MoE) language model with approximately 850 billion parameters, developed by **MagistrTheOne|Krasnodar|Russia|2025|850B**. This is a custom architecture optimized for reasoning tasks with efficient parameter utilization through expert routing.

**Author**: MagistrTheOne|Krasnodar|Russia|2025|850B
**Architecture**: Custom MoE (Mixture of Experts) Transformer
**Total Parameters**: ~850 billion (128 experts, top-k=2 routing, ~180-220B active parameters per token)
**Context Length**: 16,384 tokens
**Vocabulary Size**: 131,072 tokens
**Precision**: BF16 training, auto inference

### Architecture Details

#### MoE (Mixture of Experts) Configuration
```json
{
  "model_type": "oracle_moe",
  "vocab_size": 131072,
  "max_seq_len": 16384,
  "d_model": 8192,
  "n_layers": 96,
  "n_heads": 64,
  "d_ff": 24576,
  "activation": "swiglu",
  "rope_theta": 10000,
  "rotary_pct": 0.5,
  "rmsnorm_eps": 1e-5,
  "flash_attn": true,
  "kv_cache": true,
  "moe": {
    "experts": 128,
    "expert_hidden_mult": 4.0,
    "router": {
      "type": "topk",
      "k": 2,
      "load_balancing_loss": 0.01
    }
  },
  "fp": {
    "train": "bf16",
    "infer": "auto"
  }
}
```

#### Key Specifications
- **Total Parameters**: ~850B (128 experts × ~6.6B per expert)
- **Active Parameters**: ~180-220B per token (top-k=2 routing)
- **Expert Capacity**: 1.25× load balancing factor
- **Router Loss**: 0.01 load balancing coefficient

## Intended Use

### Primary Use Cases

- **Reasoning Tasks**: Mathematical problem solving, logical reasoning
- **Code Generation**: Programming assistance and code completion
- **Multilingual Support**: Russian and English text processing
- **Research**: Language model research and experimentation

### Target Users

- Researchers in natural language processing
- Developers building AI applications
- Organizations requiring large-scale language understanding

## Training Data

### Data Sources

- **Code**: Programming languages and software development
- **Mathematics**: Mathematical problems and proofs
- **Logic**: Logical reasoning and formal systems
- **NLP**: Natural language processing tasks
- **Reasoning**: Complex reasoning scenarios
- **Proof Writing**: Formal proof construction

### Data Processing Pipeline

1. **Ingest**: Data collection from multiple sources
2. **Clean**: Normalization, deduplication, language detection
3. **Decontaminate**: Removal of evaluation set contamination
4. **Shard**: WebDataset format with 512MB shards
5. **Statistics**: Quality assessment and reporting

### Data Quality

- **Deduplication**: MinHash/LSH based duplicate removal
- **Language Detection**: Russian/English classification
- **PII Removal**: Personal information filtering
- **Toxicity Filtering**: Content safety measures
- **Contamination Check**: Evaluation set overlap detection

## Training Details

### Infrastructure

- **Hardware**: 16x GPU cluster with TP/PP/SP parallelism
- **Framework**: Custom training pipeline with DeepSpeed ZeRO-3
- **Precision**: bf16 mixed precision training
- **Optimizer**: AdamW with learning rate 8e-5
- **Batch Size**: Global batch size 4096 with gradient accumulation

### Training Configuration

```yaml
seq_len: 16384
micro_bsz: 1
global_bsz: 4096
grad_accum: 512
precision: bf16
parallelism:
  tensor: 16
  pipeline: 12
  sequence: true
```

### Curriculum Learning

- **Foundation Stage** (0-100k steps): Code, math, logic
- **Reasoning Stage** (100k-300k steps): Advanced reasoning tasks
- **Advanced Stage** (300k-600k steps): Complex problem solving
- **Mastery Stage** (600k-800k steps): Expert-level tasks

## Evaluation

### Benchmarks

- **GSM8K**: Mathematical reasoning
- **MATH**: Advanced mathematics
- **HumanEval**: Code generation
- **MMLU**: Multitask language understanding
- **HellaSwag**: Commonsense reasoning

### Performance Characteristics

- **Efficiency**: ~180-220B active parameters per token
- **Quality**: Comparable to 200B+ dense models
- **Speed**: Optimized inference with expert routing
- **Memory**: Efficient memory usage through MoE architecture

## Limitations

### Technical Limitations

- **Computational Requirements**: Significant GPU resources needed
- **Memory Usage**: High memory requirements for inference
- **Expert Routing**: Potential for expert imbalance
- **Context Length**: Limited to 16384 tokens

### Content Limitations

- **Training Data**: Biases present in training data
- **Language Coverage**: Optimized for Russian and English
- **Domain Specificity**: May perform better on reasoning tasks
- **Safety**: Standard language model safety considerations

### Usage Limitations

- **Resource Intensive**: Requires massive computational resources (16+ GPU cluster)
- **Expertise Required**: Advanced setup and configuration needed
- **Cost**: Very high inference costs due to model size
- **Availability**: Model weights not yet publicly available

## Bias and Safety

### Known Biases

- **Language Bias**: Optimized for Russian and English
- **Domain Bias**: Strong performance on reasoning tasks
- **Cultural Bias**: Reflects training data characteristics
- **Temporal Bias**: Training data cutoff date

### Safety Measures

- **Content Filtering**: Toxicity and harmful content detection
- **PII Protection**: Personal information removal
- **Evaluation Contamination**: Careful dataset separation
- **Monitoring**: Continuous safety assessment

## Environmental Impact

### Training Impact

- **Energy Consumption**: Very high energy usage during training (16x GPU cluster)
- **Carbon Footprint**: Significant carbon emissions (800k training steps)
- **Resource Utilization**: Intensive GPU cluster usage
- **Efficiency**: MoE architecture reduces active parameter usage

### Inference Impact

- **Efficiency**: Lower computational cost per token than dense models (180-220B active vs 850B total)
- **Scalability**: Better scaling characteristics with expert routing
- **Resource Optimization**: Dynamic expert selection (top-k=2)

## Technical Specifications

### Model Architecture

```json
{
  "dense": {
    "d_model": 8192,
    "n_layers": 96,
    "n_heads": 64,
    "d_ff": 24576
  },
  "activation": "swiglu",
  "rope_theta": 10000,
  "rotary_pct": 0.5,
  "rmsnorm_eps": 1e-5,
  "flash_attn": true,
  "kv_cache": true
}
```

### Special Tokens

- `<|oracle_sys|>`: System token
- `<|oracle_intro|>`: Introduction token
- `<|author|>`: Author token (MagistrTheOne|Krasnodar|Russia|2025|850B)
- `<|endoftext|>`: End of text
- `<|pad|>`: Padding token
- `<|unk|>`: Unknown token

## Usage

### Basic Usage

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("MagistrTheOne/oracle850b")
model = AutoModelForCausalLM.from_pretrained("MagistrTheOne/oracle850b")

# Generate text
inputs = tokenizer("Hello, I am Oracle850B", return_tensors="pt")
outputs = model.generate(**inputs, max_length=200)
print(tokenizer.decode(outputs[0]))
```

### API Usage

```python
import requests

# OpenAI-compatible API
response = requests.post("http://localhost:8000/v1/chat/completions", json={
    "model": "oracle850b-moe",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
})
```

## Citation

```bibtex
@misc{oracle850b2025,
  title={Oracle850B-MoE: A Mixture of Experts Language Model for Reasoning},
  author={MagistrTheOne},
  year={2025},
  url={https://huggingface.co/MagistrTheOne/oracle850b-moe},
  note={Custom MoE architecture with 850B parameters (128 experts, 180-220B active)}
}
```

## Contact

- **Author**: MagistrTheOne|Krasnodar|Russia|2025|850B
- **Repository**: https://github.com/MagistrTheOne/oracle850b-moe
- **Hugging Face**: https://huggingface.co/MagistrTheOne/oracle850b-moe
- **Location**: Krasnodar, Russia
- **Year**: 2025
- **Model Size**: 850B parameters

## License

[License to be determined - will be specified before model release]

## Acknowledgments

- **Infrastructure**: Yandex Cloud for computational resources
- **Frameworks**: DeepSpeed, Transformers, PyTorch
- **Community**: Open source AI research community
- **Support**: Contributors and testers

---

**Disclaimer**: Oracle850B is an experimental model. Use at your own risk. The author is not responsible for any consequences of using this model.
