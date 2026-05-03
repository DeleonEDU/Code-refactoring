# 📚 Library Management System

![CI/CD Pipeline](https://github.com/DeleonEDU/Code-refactoring/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-ready-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

Система управління бібліотекою, реалізована з дотриманням принципів SOLID та покрита unit-тестами.

---

## 📋 Зміст

- [Запуск через Docker](#-запуск-через-docker)
- [Локальний запуск](#-локальний-запуск)
- [Змінні середовища](#-змінні-середовища)
- [Тести](#-тести)
- [Структура проєкту](#-структура-проєкту)

---

## 🐳 Запуск через Docker

### Передумови
- [Docker](https://docs.docker.com/get-docker/) ≥ 24.0
- [Docker Compose](https://docs.docker.com/compose/) ≥ 2.0

### Крок 1 — Клонувати репозиторій
```bash
git clone https://github.com/<YOUR_USERNAME>/<YOUR_REPO>.git
cd <YOUR_REPO>
```

### Крок 2 — Запустити додаток
```bash
docker compose up -d
```

### Зупинити додаток
```bash
docker compose down
```

### Запустити тести в окремому контейнері
```bash
docker compose --profile test up tests
```

---

## 💻 Локальний запуск

### Передумови
- Python 3.11+

### Крок 1 — Встановити залежності
```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Крок 2 — Запустити додаток
```bash
python main.py
```

---

## ⚙️ Змінні середовища

| Змінна       | Опис                               | За замовчуванням      |
|--------------|------------------------------------|-----------------------|
| `APP_ENV`    | Середовище (`production`/`test`)   | `production`          |

---

## 🧪 Тести

### Запуск тестів локально
```bash
pytest tests/ -v
```

### Запуск з покриттям коду
```bash
pytest tests/ -v --cov=. --cov-report=term-missing
```

### Запуск у Docker
```bash
docker compose --profile test up tests
```

---

## 📁 Структура проєкту

```
library-system/
├── .github/
│   └── workflows/
│       └── ci.yml              # GitHub Actions CI/CD
├── src/
│   ├── controllers/            # Контролери (CLI)
│   ├── dto/                    # Data Transfer Objects
│   ├── models/                 # Доменні моделі
│   ├── repositories/           # Патерн Repository (In-memory)
│   └── services/               # Бізнес-логіка
├── tests/                      # Unit-тести
├── main.py                     # Точка входу (CLI демонстрація)
├── Dockerfile                  # Production image
├── Dockerfile.test             # Test image
├── docker-compose.yaml
├── requirements.txt
└── README.md
```
