# Промо-машина — Дизайн-спека

> - **Версия:** 1.0
> - **Дата:** 2026-04-20

## Цель

Персональный десктопный инструмент для автоматической генерации вирусных промо-роликов. На входе — скриншоты приложения + описание. На выходе — 5-10 готовых MP4 (9:16) с трендовым звуком, hook-текстами, описаниями и хэштегами для VK Клипов / YouTube Shorts / Reels.

## Стек

- **Бэкенд:** Python 3.12 + FastAPI
- **Фронт:** React + Vite + Tailwind CSS
- **Видео:** moviepy + FFmpeg
- **Скрейпинг:** TikTokApi, yt-dlp, VK API
- **AI:** OpenAI API (GPT-4o, GPT-4o-mini, TTS, DALL-E)
- **Аудио:** edge-tts (бесплатный TTS от Microsoft), pydub для микширования
- **БД:** SQLite (локальная)
- **Запуск:** `python main.py` → localhost:8000

---

## Архитектура

```
┌─────────────────────────────────────────────┐
│           React UI (localhost:5173)          │
│  ┌─────┐ ┌────────┐ ┌────────┐ ┌────────┐  │
│  │Тренд│ │Анализ  │ │Проекты │ │Генера- │  │
│  │  ы  │ │        │ │        │ │  ция   │  │
│  └──┬──┘ └───┬────┘ └───┬────┘ └───┬────┘  │
└─────┼────────┼──────────┼──────────┼────────┘
      │        │          │          │
      ▼        ▼          ▼          ▼
┌─────────────────────────────────────────────┐
│         FastAPI Backend (localhost:8000)     │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │ Scanner  │  │ Analyzer │  │ Generator │ │
│  │ TikTok   │  │ GPT-4o   │  │ Scripts   │ │
│  │ VK Clips │  │ Vision   │  │ Hooks     │ │
│  │ yt-dlp   │  │ Patterns │  │ Copy      │ │
│  └──────────┘  └──────────┘  └───────────┘ │
│                                             │
│  ┌──────────┐  ┌──────────┐  ┌───────────┐ │
│  │ Audio    │  │ Renderer │  │ Database  │ │
│  │ TTS      │  │ moviepy  │  │ SQLite    │ │
│  │ Trending │  │ FFmpeg   │  │ Trends    │ │
│  │ Mixer    │  │ Effects  │  │ Projects  │ │
│  └──────────┘  └──────────┘  └───────────┘ │
└─────────────────────────────────────────────┘
```

---

## Модули бэкенда

### 1. Scanner — сбор трендов

**Что делает:** Сканирует TikTok и VK Клипы по заданной нише (ключевые слова, хэштеги). Скачивает топ видео + метаданные. Сохраняет в SQLite + файловую систему.

**Входы:**
- Ключевые слова ниши (например: «мобильное приложение», «AI app», «baby face»)
- Количество видео для сбора (по умолчанию 30)
- Платформа: TikTok / VK / обе

**Выходы:**
- Скачанные MP4 файлы в `downloads/`
- Записи в БД: video_id, url, views, likes, shares, comments, hashtags, audio_id, audio_name, description, duration, downloaded_at

**Технологии:**
- TikTokApi (Python) для получения списка трендовых видео
- TikTok Creative Center scraper для трендовых хэштегов и звуков
- yt-dlp для скачивания MP4
- VK API (vk_api Python) для VK Клипов
- Residential proxy для стабильности TikTok

**API endpoints:**
- `POST /api/scan` — запустить сканирование
- `GET /api/trends` — получить список собранных трендов
- `GET /api/trends/{id}/video` — стримить скачанное видео

---

### 2. Analyzer — AI анализ трендов

**Что делает:** Берёт скачанные видео и через GPT-4o Vision анализирует: структуру, hook, тайминги, текст, переходы, CTA. Выявляет паттерны — что общего у топ-видео в нише.

**Входы:**
- Список video_id из БД (или «все за последние N дней»)

**Выходы:**
- Для каждого видео: JSON с разбором (hook_type, hook_text, structure, cuts_count, cta_type, audio_style, duration, text_placement)
- Общий отчёт по нише: топ-3 формата хуков, средний темп, популярные CTA, рекомендуемая длительность

**Как работает:**
1. Извлекает 5-8 ключевых кадров из видео (равномерно по таймлайну)
2. Отправляет кадры + описание в GPT-4o Vision
3. Промпт: «Проанализируй это промо-видео: какой hook в первые 3 секунды, сколько переходов, какой CTA, какой стиль текста, что делает его вирусным»
4. Парсит ответ в структурированный JSON
5. Агрегирует по всем видео → паттерны ниши

**API endpoints:**
- `POST /api/analyze` — запустить анализ
- `GET /api/analysis/{scan_id}` — результат анализа
- `GET /api/patterns` — агрегированные паттерны

---

### 3. Generator — генерация контента

**Что делает:** На основе анализа трендов + данных о приложении генерирует полный контент-пакет.

**Входы:**
- project_id (из вкладки Проекты)
- Паттерны из Analyzer
- Количество вариантов (по умолчанию 10)

**Выходы:**
- Сценарии (10 штук): hook → проблема → решение → CTA, с таймингами
- Hook-тексты (20 штук): короткие фразы для первых 3 секунд
- Описания для платформ: VK (до 2200 символов), YouTube Shorts (до 100 символов заголовок), TikTok (до 2200 символов)
- Хэштеги: 5-10 штук на каждое видео, микс трендовых + нишевых
- Текст для био профиля

**Как работает:**
1. Собирает контекст: app_name, description, key_features, screenshots, target_audience
2. Подставляет в промпт паттерны из анализа: «Вот что работает в нише: [паттерны]. Сгенерируй сценарии для продвижения [app_name]»
3. GPT-4o-mini генерирует (дешевле, достаточно для текста)
4. Форматирует под каждую платформу

**API endpoints:**
- `POST /api/generate/scripts` — сценарии и hooks
- `POST /api/generate/copy` — описания, хэштеги, био
- `GET /api/generated/{project_id}` — все сгенерированные материалы

---

### 4. Audio — звуковой движок

**Что делает:** Подбирает/генерирует звук для видео.

**Три режима:**

**A) Трендовый звук:** Ищет в базе скачанных трендов популярные аудио. Показывает топ-10 по использованию. Пользователь выбирает. (Юридически серая зона — для органического контента ок, для рекламы нет.)

**B) AI озвучка (TTS):** Генерирует закадровый голос по сценарию.
- edge-tts (Microsoft, бесплатный, 100+ голосов, русский)
- Или OpenAI TTS ($15/1M символов, натуральнее)

**C) Royalty-free музыка:** Локальная библиотека в `assets/sounds/`. Категоризирована по настроению: energetic, chill, dramatic, funny.

**Микширование:** pydub — голос на -6dB, музыка на -18dB, экспорт в AAC.

**API endpoints:**
- `GET /api/audio/trending` — трендовые звуки из скачанных видео
- `POST /api/audio/tts` — сгенерировать озвучку
- `GET /api/audio/library` — библиотека royalty-free
- `POST /api/audio/mix` — микшировать голос + музыка

---

### 5. Renderer — рендер видео

**Что делает:** Собирает финальный MP4 из всех компонентов.

**Входы:**
- Сценарий (из Generator)
- Скриншоты приложения
- Аудио (из Audio)
- Настройки: шаблон, длительность, стиль текста

**Шаблоны видео (5 штук):**

1. **AppReveal** — чёрный экран → hook-текст крупно → скриншоты в phone frame с зумом → CTA
2. **POVReaction** — «POV: ты кинул это крашу» → скриншоты каскадом → typing dots → CTA
3. **HookAndShow** — большой emoji + hook → быстрая смена экранов → gradient CTA button
4. **SplitScreen** — слева «до» (проблема) → справа «после» (приложение) → CTA
5. **Testimonial** — AI-сгенерированная «говорящая голова» с субтитрами + скриншоты на фоне

**Технические параметры:**
- 1080×1920 px (9:16)
- 30 FPS
- H.264 + AAC
- Длительность: 15 / 30 / 60 секунд (выбирается)
- Safe zones: текст не ниже 80% высоты, не правее 90% ширины
- Субтитры: белый текст, чёрная обводка 3px, Montserrat Bold

**Эффекты:**
- Zoom-in на скриншоты (Ken Burns effect)
- Fade-in/fade-out между слайдами
- Pop-in анимация текста (слова по одному)
- Phone device frame (iPhone/Android мокапы)
- Водяной знак (название приложения + ссылка)

**Пакетный рендер:** Параллельно рендерит несколько видео (multiprocessing).

**API endpoints:**
- `POST /api/render` — запустить рендер одного видео
- `POST /api/render/batch` — пакетный рендер
- `GET /api/render/status/{job_id}` — статус рендера
- `GET /api/render/output/{job_id}` — скачать готовый MP4

---

## Фронтенд

### Вкладка 1: Тренды

- Кнопка «Сканировать» → ввод ниши → прогресс-бар → список видео
- Каждое видео: превью, views, likes, shares, длительность, хэштеги
- Кнопка «Воспроизвести» — встроенный плеер
- Фильтры: по платформе, по дате, по views

### Вкладка 2: Анализ

- Кнопка «Анализировать тренды» → прогресс → отчёт
- Для каждого видео: breakdown (hook, структура, CTA)
- Общие паттерны ниши: карточки с инсайтами
- «Что работает»: топ хуков, средний темп, лучшие CTA

### Вкладка 3: Проекты

- Список приложений (BabyFace AI, TierList, QuizDrop...)
- Добавить проект: название, описание, ключевые фичи, ЦА, ссылка
- Загрузить скриншоты (drag & drop)
- У каждого проекта — папка с аутпутами

### Вкладка 4: Генерация

- Выбрать проект → выбрать шаблон(ы) → настройки (длительность, стиль, количество)
- Кнопка «ГЕНЕРИРОВАТЬ ВСЁ» → прогресс
- Параллельно: генерация сценариев + подбор звука + рендер
- Превью каждого видео по мере готовности

### Вкладка 5: Экспорт

- Сетка готовых видео с превью
- Для каждого: описание, хэштеги, рекомендуемое время публикации
- Кнопки: «Скачать MP4», «Скопировать описание», «Скопировать хэштеги»
- «Скачать всё» — ZIP с видео + texts.md

---

## База данных (SQLite)

### Таблица `trends`
```sql
id TEXT PRIMARY KEY,
platform TEXT,          -- 'tiktok' | 'vk'
url TEXT,
views INTEGER,
likes INTEGER,
shares INTEGER,
comments INTEGER,
duration REAL,
hashtags TEXT,           -- JSON array
audio_id TEXT,
audio_name TEXT,
description TEXT,
file_path TEXT,          -- путь к скачанному MP4
analyzed INTEGER DEFAULT 0,
analysis TEXT,           -- JSON результат анализа
scanned_at TIMESTAMP
```

### Таблица `projects`
```sql
id TEXT PRIMARY KEY,
name TEXT,
description TEXT,
features TEXT,            -- JSON array
target_audience TEXT,
app_url TEXT,
screenshots_dir TEXT,
created_at TIMESTAMP
```

### Таблица `renders`
```sql
id TEXT PRIMARY KEY,
project_id TEXT,
template TEXT,
hook_text TEXT,
script TEXT,              -- JSON сценарий
audio_path TEXT,
output_path TEXT,
duration REAL,
status TEXT,              -- 'pending' | 'rendering' | 'done' | 'error'
platform_copy TEXT,       -- JSON {vk, youtube, tiktok}
hashtags TEXT,            -- JSON array
created_at TIMESTAMP
```

---

## Файловая структура

```
promo-machine/
├── main.py                          # Точка входа: запуск FastAPI + открытие браузера
├── requirements.txt
├── config.yaml                      # API ключи, пути, настройки
│
├── backend/
│   ├── __init__.py
│   ├── app.py                       # FastAPI app, CORS, static files
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── scan.py                  # /api/scan, /api/trends
│   │   ├── analyze.py               # /api/analyze, /api/patterns
│   │   ├── generate.py              # /api/generate/*
│   │   ├── audio.py                 # /api/audio/*
│   │   ├── render.py                # /api/render/*
│   │   └── projects.py              # /api/projects/*
│   │
│   ├── scanner/
│   │   ├── __init__.py
│   │   ├── tiktok.py                # TikTokApi + Creative Center
│   │   ├── vk.py                    # VK API clips
│   │   └── downloader.py            # yt-dlp wrapper
│   │
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── video_analyzer.py        # GPT-4o Vision разбор видео
│   │   ├── frame_extractor.py       # Извлечение ключевых кадров
│   │   └── pattern_detector.py      # Агрегация паттернов
│   │
│   ├── generator/
│   │   ├── __init__.py
│   │   ├── script_writer.py         # Сценарии через GPT
│   │   ├── hook_writer.py           # Hook-тексты
│   │   ├── copy_writer.py           # Описания, хэштеги, био
│   │   └── prompts.py               # Шаблоны промптов
│   │
│   ├── audio/
│   │   ├── __init__.py
│   │   ├── tts.py                   # edge-tts / OpenAI TTS
│   │   ├── trending.py              # Трендовые звуки из скачанных видео
│   │   └── mixer.py                 # pydub микширование
│   │
│   ├── renderer/
│   │   ├── __init__.py
│   │   ├── composer.py              # Главный движок сборки (moviepy)
│   │   ├── templates/
│   │   │   ├── app_reveal.py
│   │   │   ├── pov_reaction.py
│   │   │   ├── hook_and_show.py
│   │   │   ├── split_screen.py
│   │   │   └── testimonial.py
│   │   ├── effects.py               # Зум, fade, pop-in текст
│   │   ├── text_overlay.py          # Текст + субтитры + safe zones
│   │   ├── device_frame.py          # Phone mockup overlay
│   │   └── batch.py                 # Пакетный рендер (multiprocessing)
│   │
│   └── db/
│       ├── __init__.py
│       ├── database.py              # SQLite подключение
│       └── models.py                # SQL таблицы
│
├── frontend/
│   ├── package.json
│   ├── vite.config.ts
│   ├── index.html
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx                  # Табы + роутинг
│   │   ├── api.ts                   # fetch wrapper для бэкенда
│   │   ├── components/
│   │   │   ├── TrendsTab.tsx
│   │   │   ├── AnalysisTab.tsx
│   │   │   ├── ProjectsTab.tsx
│   │   │   ├── GenerateTab.tsx
│   │   │   ├── ExportTab.tsx
│   │   │   ├── VideoPlayer.tsx
│   │   │   └── ProgressBar.tsx
│   │   └── styles/
│   │       └── globals.css
│   └── public/
│
├── assets/
│   ├── fonts/
│   │   └── Montserrat-Bold.ttf
│   ├── frames/
│   │   ├── iphone-frame.png
│   │   └── android-frame.png
│   └── sounds/
│       ├── energetic/
│       ├── chill/
│       └── dramatic/
│
├── data/
│   ├── promo.db                     # SQLite база
│   ├── downloads/                   # Скачанные тренды
│   │   ├── tiktok/
│   │   └── vk/
│   └── projects/                    # Данные проектов
│       └── babyface/
│           ├── screenshots/
│           └── output/
│
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-04-20-promo-machine-design.md
```

---

## Зависимости (requirements.txt)

```
fastapi>=0.115
uvicorn>=0.34
openai>=1.60
moviepy>=2.1
Pillow>=11.0
pydub>=0.25
edge-tts>=7.0
yt-dlp>=2024.12
TikTokApi>=7.3
vk-api>=11.9
aiosqlite>=0.20
python-multipart>=0.0.18
httpx>=0.28
playwright>=1.49
```

---

## Порядок разработки

1. **Скелет** — FastAPI + React + SQLite + config.yaml (2 часа)
2. **Projects** — CRUD проектов + загрузка скриншотов (2 часа)
3. **Scanner** — TikTok + VK сбор трендов (4 часа)
4. **Analyzer** — GPT-4o Vision разбор + паттерны (3 часа)
5. **Generator** — сценарии, hooks, копирайтинг (2 часа)
6. **Audio** — TTS + микширование (2 часа)
7. **Renderer** — 5 шаблонов видео + эффекты + batch (6 часов)
8. **Export** — скачивание + копирование текстов (1 час)

**Итого: ~22 часа = 2-3 дня интенсивной работы.**
