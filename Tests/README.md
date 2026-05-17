# NeuroCap — Tests

Unit and integration tests for signal processing, feature extraction, and model inference.

---

## Structure

```
Tests/
├── test_features/    # Tests for feature extraction functions
└── test_models/      # Tests for model loading and inference
```

---

## Running tests

```bash
# From project root, with the ML environment active
cd c:\...\EEG_project
python -m pytest Tests/ -v

# Run only feature tests
python -m pytest Tests/test_features/ -v

# Run only model tests
python -m pytest Tests/test_models/ -v

# With coverage report
python -m pytest Tests/ --cov=src --cov=features -v
```

---

## Test scope

### `test_features/`
- Bandpass filter correctness (passband, stopband attenuation)
- Notch filter at 50 Hz
- Welch PSD output shape and frequency resolution
- TBR / EI computation against known values
- IAPF detection accuracy
- DWT decomposition levels

### `test_models/`
- Model loading (`.pt` / `.pkl` files)
- Inference output shape and class probabilities sum to 1
- Prediction consistency (deterministic output for same input)
- Edge cases: all-zero epoch, clipped signal, artifact epoch

---

## Backend API tests

Backend integration tests use `httpx.AsyncClient` with FastAPI `TestClient`:

```bash
cd app/Backend
pytest tests/ -v
```

Tests cover: auth flow (register → login → refresh), session CRUD, role guards (403 on wrong role), therapist endpoints.

---

## Dependencies

```bash
pip install pytest pytest-asyncio pytest-cov httpx
```
