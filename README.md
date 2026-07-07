# 🌿 CropDisease Assistant

Your AI-powered companion for plant health. 📸 Snap a photo of a leaf and get an instant disease prediction, or 💬 ask the assistant anything about crop diseases through a smart, knowledge-grounded chat.

---

## ✨ What it does

CropDisease Assistant combines two powerful AI systems:

1. 🖼️ **Computer Vision Disease Detection** — upload a leaf image and the model returns the most likely disease, confidence score, and top-5 alternatives.
2. 🤖 **RAG-Powered Chat Assistant** — ask questions in natural language. The assistant retrieves relevant knowledge from a curated plant-disease knowledge base and answers using a large language model, so replies are accurate and grounded.

---

## 🛠️ Core Technologies

| System | Stack |
|---|---|
| 🧠 **CV Model** | ResNet50 trained on the New Plant Diseases Dataset (38 classes) |
| 🔥 **CV Framework** | PyTorch, Torchvision, Pillow, NumPy |
| 🔗 **Embeddings** | Sentence-Transformers |
| 🗄️ **Vector Database** | Qdrant |
| 💡 **LLM** | Groq (OpenAI-compatible API) |
| 📊 **Tracing** | LangSmith |
| ⚡ **API** | FastAPI + Uvicorn |
| 🎨 **Frontend** | React + Vite + Tailwind CSS |

---

## 📁 Project Structure

```
CropDisease-Assistant/
├── src/
│   ├── api/                 # FastAPI app and routes
│   │   ├── main.py
│   │   └── routes/
│   │       ├── chat.py      # /api/chat, /api/chat/llm
│   │       ├── detect.py    # /api/detect
│   │       └── health.py    # /api/health
│   ├── cv/                  # Computer vision pipeline
│   │   ├── classifier.py    # PlantDiseaseClassifier: load + predict
│   │   ├── model.py         # ResNet50 architecture
│   │   ├── predict.py       # High-level predict() function
│   │   ├── constants.py     # 38 plant-disease classes
│   │   ├── data_loader.py   # ImageFolder train/val loaders
│   │   ├── train.py         # Training script
│   │   └── models/          # Trained checkpoint
│   ├── services/            # RAG generation and retrieval
│   ├── core/                # Index builder for Qdrant
│   ├── infrastructure/      # Qdrant provider
│   └── config.py            # Centralized Pydantic settings
├── frontend/                # React web app
├── Knowledge_base/          # Markdown knowledge source
└── requirements.txt
```

---

## 🚀 Getting Started

### 1️⃣ Clone and install

```bash
# Using uv (recommended)
uv sync

# Or using pip
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2️⃣ Configure environment variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

Required variables:

```ini
# 🗄️ Qdrant — vector database for the RAG knowledge base
QDRANT__URL="https://your-cluster-id.cloud.qdrant.io:6333"
QDRANT__API_KEY="your-qdrant-api-key"
QDRANT__COLLECTION_NAME="plant_diseases_kb"

# 🔗 HuggingFace embedding model
HUGGINGFACE__MODEL_NAME="sentence-transformers/all-MiniLM-L6-v2"
HUGGINGFACE__MODEL_DIMENSIONS=384

# 💡 Groq — LLM provider
GROQ__API_KEY="your-groq-api-key"
GROQ__MODEL="openai/gpt-oss-120b"

# 📊 Optional: LangSmith tracing
LANGSMITH__API_KEY="your-langsmith-key"
LANGSMITH__TRACING=true
```

### 3️⃣ Build the RAG knowledge index

Before chatting, upload your disease knowledge to Qdrant:

```bash
python -m src.core.index_builder
```

This reads the JSON file configured in `QDRANT__DATA_JSON_PATH`, embeds each record, and stores the vectors in Qdrant.

### 4️⃣ Start the API

```bash
uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

API docs are available at `http://localhost:8000/docs`.

### 5️⃣ Start the frontend

```bash
cd frontend
npm install
npm run dev
```

The app typically runs at `http://localhost:5173`.

---

## 🤖 RAG System

The chat assistant follows a Retrieval-Augmented Generation pipeline:

1. 💬 **User asks a question** — e.g. *"What causes tomato early blight?"*
2. 🔗 **Embed the query** using Sentence-Transformers.
3. 🔍 **Retrieve top-k matching chunks** from Qdrant, optionally filtered by `disease_name` or `plant`.
4. 📝 **Build a grounded prompt** from the retrieved context.
5. ✨ **Generate the answer** with Groq.
6. 📊 **Trace the run** with LangSmith (optional).

### Chat endpoints

| Endpoint | Description |
|---|---|
| `POST /api/chat` | RAG-based answer |
| `POST /api/chat/llm` | Direct LLM answer without retrieval |

### Example request

```bash
curl -X POST http://localhost:8000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "question": "How do I treat tomato early blight?",
    "top_k": 5,
    "disease_name": "early_blight",
    "plant": "tomato"
  }'
```

---

## 🖼️ Computer Vision System

The disease detector uses a ResNet50 model fine-tuned on 38 plant-disease classes. The classifier:

- ✅ Loads the correct architecture automatically for the saved checkpoint.
- 🎨 Preprocesses images with ImageNet normalization.
- 🔄 Supports optional **test-time augmentation (TTA)** and **temperature scaling** for confidence calibration.
- 📈 Returns top-k predictions with confidence scores and a reliability flag.

### Detection endpoint

| Endpoint | Description |
|---|---|
| `POST /api/detect` | Upload an image and get disease predictions |

### Example request

```bash
curl -X POST http://localhost:8000/api/detect \
  -F "file=@leaf.jpg"
```

### Example response

```json
{
  "predictions": [
    {"class_name": "Apple___Apple_scab", "confidence": 46.46},
    {"class_name": "Apple___Cedar_apple_rust", "confidence": 21.82},
    {"class_name": "Apple___Black_rot", "confidence": 21.0}
  ],
  "top_class": "Apple___Apple_scab",
  "top_confidence": 46.46
}
```

### 🔧 Tuning the CV model

You can tune behavior through environment variables:

```ini
CV__MODEL_PATH="src/cv/models/resnet50_plant_38class_best.pth.zip"
CV__IMAGE_SIZE=224
CV__TEMPERATURE=1.0          # <1.0 sharpens confidence, >1.0 softens it
CV__TTA_ENABLED=false        # enable test-time augmentation
CV__ENTROPY_THRESHOLD=0.4
CV__GAP_THRESHOLD=5.0
CV__DEVICE="auto"            # auto, cpu, or cuda
```

If the model feels under-confident on clear leaf photos, try `CV__TEMPERATURE=0.55`.

---

## 🏋️ Training Your Own CV Model

If you want to retrain the disease classifier:

1. 📂 Prepare your dataset under `dataset/train` and `dataset/valid`, with one folder per class.
2. 🏃 Run the training script:

```bash
python -m src.cv.train
```

The best checkpoint is saved to `models/best_model.pth`.

---

## 📋 Environment Reference

| Variable | Purpose |
|---|---|
| `QDRANT__URL` | Qdrant cluster URL |
| `QDRANT__API_KEY` | Qdrant API key |
| `QDRANT__COLLECTION_NAME` | Collection name for disease vectors |
| `QDRANT__DATA_JSON_PATH` | Path to cleaned disease JSON data |
| `HUGGINGFACE__MODEL_NAME` | Embedding model name |
| `HUGGINGFACE__MODEL_DIMENSIONS` | Embedding dimension |
| `GROQ__API_KEY` | Groq API key |
| `GROQ__MODEL` | LLM model name |
| `GROQ__TEMPERATURE` | LLM sampling temperature |
| `GROQ__MAX_TOKENS` | Max tokens in LLM response |
| `LANGSMITH__API_KEY` | LangSmith API key |
| `LANGSMITH__TRACING` | Enable/disable tracing |
| `LANGSMITH__PROJECT` | LangSmith project name |
| `CV__MODEL_PATH` | Path to CV checkpoint |
| `CV__TEMPERATURE` | Softmax temperature for CV |
| `CV__TTA_ENABLED` | Enable TTA |
| `CV__DEVICE` | Inference device |

---
