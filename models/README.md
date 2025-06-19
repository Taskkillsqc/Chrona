# 本地模型文件夹

请将下载的 GGUF 格式模型文件放在此文件夹中。

## 推荐模型

### Qwen 系列
- **Qwen2.5-1.5B-Instruct-Q4_K_M.gguf** (~1GB)
  - 下载: https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF
  - 轻量级，适合资源受限环境

- **Qwen2.5-3B-Instruct-Q4_K_M.gguf** (~2GB)
  - 下载: https://huggingface.co/Qwen/Qwen2.5-3B-Instruct-GGUF
  - 平衡性能和资源消耗

- **Qwen2.5-7B-Instruct-Q4_K_M.gguf** (~4GB)
  - 下载: https://huggingface.co/Qwen/Qwen2.5-7B-Instruct-GGUF
  - 更强性能，需要更多内存

### LLaMA 系列
- **Llama-3.2-1B-Instruct-Q4_K_M.gguf** (~1GB)
  - 下载: https://huggingface.co/bartowski/Llama-3.2-1B-Instruct-GGUF

- **Llama-3.2-3B-Instruct-Q4_K_M.gguf** (~2GB)
  - 下载: https://huggingface.co/bartowski/Llama-3.2-3B-Instruct-GGUF

### Gemma 系列
- **gemma-2-2b-it-Q4_K_M.gguf** (~1.5GB)
  - 下载: https://huggingface.co/bartowski/gemma-2-2b-it-GGUF

## 如何下载

### 方法 1: 使用 huggingface-hub (推荐)
```bash
pip install huggingface-hub
huggingface-cli download Qwen/Qwen2.5-1.5B-Instruct-GGUF qwen2.5-1.5b-instruct-q4_k_m.gguf --local-dir ./models --local-dir-use-symlinks False
```

### 方法 2: 直接从网页下载
1. 访问上述 HuggingFace 链接
2. 找到 Q4_K_M.gguf 文件
3. 点击下载
4. 将文件移动到此 models 文件夹

## 配置示例

下载模型后，在 config.yaml 中配置：

```yaml
llm:
  provider: "local"
  local:
    enabled: true
    model_path: "./models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
    context_length: 2048
    gpu_layers: 0  # 使用 GPU 加速的层数，0 表示仅使用 CPU
    temperature: 0.7
    max_tokens: 1000
    verbose: false
```

## 系统要求

- **内存**: 至少 4GB RAM（推荐 8GB+）
- **存储**: 根据模型大小，1-4GB 可用空间
- **CPU**: 支持 AVX2 指令集（大部分现代 CPU）
- **GPU**: 可选，支持 CUDA 或 Metal（macOS）加速

## 性能优化

### CPU 优化
- 设置 `n_threads` 为 CPU 核心数
- 使用 Q4_K_M 量化格式平衡质量和速度

### GPU 优化 (可选)
- 安装 CUDA 版本的 llama-cpp-python
- 设置 `gpu_layers` 将模型层加载到 GPU
- 监控 GPU 内存使用情况
