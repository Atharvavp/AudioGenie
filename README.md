
# 🎧 AudioGenie: Modular Audio Enhancement Pipeline

AudioGenie is a flexible and modular audio enhancement pipeline built for batch processing of noisy audio files. It supports:
- Conversion to clean WAV format
- Speech enhancement via ClearVoice
- Post-processing using parametric equalizers
- Noise-only extraction (original - denoised)
- Fully configurable via JSON
- Docker-based GPU execution

---

## 📦 Features

✅ Convert audio to consistent format  
✅ Denoise using ClearVoice models  
✅ Apply parametric EQ (FFmpeg firequalizer)  
✅ Extract residual noise as a separate track  
✅ Configurable via JSON  
✅ Docker-ready for GPU inference  

---

## 🚀 Quickstart

### 1. Clone the repo

```bash
git clone https://github.com/yourname/audiogenie.git
cd audiogenie
````

### 2. Install dependencies

**Option A – Local Environment (Python ≥ 3.8):**

```bash
pip install -r requirements.txt
```

**Option B – Docker (recommended for GPU support):**

```bash
bash scripts/build_image.sh
bash scripts/launch_image.sh
```

---

## ⚙️ Configuration

Create a JSON config file like `config.json`:

```json
{
  "input_audio": {
    "path": "data/input",
    "recursive": true
  },
  "conversion": {
    "enabled": true,
    "output_directory": "data/converted",
    "codec": "pcm_s16le",
    "sampling_rate": 48000,
    "channels": 1
  },
  "inference": {
    "enabled": true,
    "model_name": "MossFormer2_SE_48K",
    "output_directory": "data/denoised"
  },
  "postprocessing": {
    "enabled": true,
    "save_output": true,
    "output_directory": "data/postprocessed",
    "fire_eq": {
      "frequency": 1000,
      "gain": -10
    },
    "codec": "pcm_s16le"
  },
  "noise_output": {
    "enabled": true,
    "output_directory": "data/noise_only",
    "intermediate_directory": "data/temp",
    "keep_intermediates": false
  }
}
```

---

## 🧪 Running the Pipeline

```bash
python main.py config.json
```

This will perform:

1. Input discovery
2. Audio conversion (if enabled)
3. ClearVoice inference (if enabled)
4. EQ post-processing (if enabled)
5. Noise-only waveform generation (if enabled)

---

## 📁 Output Structure

```
data/
├── input/                 # Original input files
├── converted/             # WAV-converted files
├── denoised/              # Model inference output
├── postprocessed/         # EQ-processed files
├── noise_only/            # Residual noise (original - denoised)
└── temp/                  # Intermediate files (if enabled)
```

---

## 🐳 Docker Notes

To run with Docker (uses all GPUs):

```bash
bash scripts/build_image.sh
bash scripts/launch_image.sh
python main.py config.json
```

> ⚠️ Requires NVIDIA Container Toolkit for GPU access.

---

## 📊 Model Support

Currently supports:

* `MossFormer2_SE_48K` (ClearVoice)
  Future versions may support ONNX-based custom models via config.

---

## 📌 Requirements

* Python 3.8+
* FFmpeg
* GPU (for ClearVoice model via ONNX Runtime)

---

## 🔍 Example Use Case

You have 100 noisy `.mp3` or `.wav` call recordings and want:

* Convert to 48 kHz mono `.wav`
* Clean them using ClearVoice
* Apply a low-shelf EQ
* Extract and save residual noise

All of this can be done with a single config file and one-line CLI.

---

## 🙏 Acknowledgments

* [ClearVoice](https://github.com/snakers4/clearvoice) – speech enhancement
* [FFmpeg](https://ffmpeg.org/) – audio processing
* [TorchAudio](https://pytorch.org/audio/stable/index.html) – audio I/O and tools

```
