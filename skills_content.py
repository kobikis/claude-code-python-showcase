"""
AI/ML Skills Content

Large skill content templates for PyTorch, HuggingFace, and Model Optimization.
"""

PYTORCH_CONTENT = """# PyTorch Patterns Skill

## Overview

Production-ready PyTorch patterns for model development, training, and deployment.

## Core Patterns

### 1. Model Definition

```python
import torch
import torch.nn as nn

class CustomModel(nn.Module):
    def __init__(self, input_dim: int, hidden_dim: int, output_dim: int):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(0.2)
        )
        self.decoder = nn.Linear(hidden_dim, output_dim)
        self._init_weights()

    def _init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)

    def forward(self, x):
        return self.decoder(self.encoder(x))
```

### 2. Device Management

```python
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
inputs = inputs.to(device)
```

### 3. Training Best Practices

- Use `torch.no_grad()` for inference
- Set `model.eval()` during validation
- Use gradient clipping
- Implement checkpointing
- Use mixed precision training

## Common Pitfalls

**Memory Leaks**: Always call `optimizer.zero_grad()`
**Device Mismatch**: Ensure inputs and model on same device
**Gradient Issues**: Use `torch.no_grad()` for inference

## Testing

Test model shapes, gradient flow, and device placement.
"""

HUGGINGFACE_CONTENT = """# HuggingFace Models Skill

## Overview

Best practices for integrating HuggingFace Transformers models.

## Core Patterns

### 1. Model Loading

```python
from transformers import AutoModel, AutoTokenizer

model = AutoModel.from_pretrained(
    "model-name",
    torch_dtype=torch.float16,
    device_map="auto",
    cache_dir="./models"
)

tokenizer = AutoTokenizer.from_pretrained("model-name")
```

### 2. Efficient Tokenization

```python
encodings = tokenizer(
    texts,
    padding=True,
    truncation=True,
    max_length=512,
    return_tensors="pt"
)
```

### 3. Pipeline Usage

```python
from transformers import pipeline

pipe = pipeline(
    "text-classification",
    model="model-name",
    device=0,
    batch_size=32
)

results = pipe(texts)
```

## Best Practices

- Cache models locally
- Use pipelines for common tasks
- Implement model warming
- Use batch processing
- Consider quantization

## Performance Tips

- Use fp16 on GPU
- Batch inference
- Use ONNX for production
- Profile memory usage
"""

MODEL_OPTIMIZATION_CONTENT = """# Model Optimization Skill

## Overview

Techniques for optimizing deep learning models for production.

## Optimization Techniques

### 1. Quantization

```python
from torch.quantization import quantize_dynamic

quantized_model = quantize_dynamic(
    model,
    {torch.nn.Linear},
    dtype=torch.qint8
)
```

### 2. ONNX Conversion

```python
torch.onnx.export(
    model,
    dummy_input,
    "model.onnx",
    opset_version=14
)
```

### 3. Model Pruning

```python
import torch.nn.utils.prune as prune

prune.l1_unstructured(module, name="weight", amount=0.3)
```

## Best Practices

- Start with dynamic quantization
- Use ONNX for cross-platform
- Profile before optimizing
- Test accuracy after optimization
- Benchmark on target hardware

## Performance Metrics

Track:
- Inference latency (ms)
- Throughput (samples/sec)
- Model size (MB)
- Memory usage (MB)
- Accuracy degradation (%)
"""
