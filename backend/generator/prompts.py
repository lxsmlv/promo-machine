SCRIPT_SYSTEM = """Ты — эксперт по созданию вирусных коротких видео для продвижения мобильных приложений.
Формат: VK Клипы / YouTube Shorts / Reels. Аудитория: 14-25 лет, Россия.
Правила:
- Сценарий на русском
- Хук в первые 3 секунды
- Структура: Hook (0-3) → Проблема (3-8) → Решение (8-{end_sec}) → CTA (последние 5 сек)
- Формат ответа: JSON массив без markdown"""

SCRIPT_USER = """Приложение: {app_name}
Описание: {description}
Фичи: {features}
ЦА: {target_audience}
Паттерны: hook={hook_type}, cta={cta_type}, mood={mood}, face={use_face}, screen={use_screen}

Сгенерируй {count} сценариев по {duration} секунд. Каждый:
{{"title":"название","duration":{duration},"scenes":[{{"time":"0-3","visual":"что на экране","text_overlay":"текст","voiceover":"голос или null"}}],"hook_text":"хук","cta_text":"CTA"}}

Верни JSON массив."""

HOOKS_USER = """Приложение: {app_name}
Описание: {description}

Сгенерируй {count} hook-текстов для первых 3 секунд видео.
Правила: русский, макс 8 слов, 1-2 эмодзи, вызывает эмоцию.
Каждый на новой строке без нумерации."""

COPY_USER = """Приложение: {app_name}
Описание: {description}
Фичи: {features}

Верни ТОЛЬКО JSON (без markdown):
{{"vk_descriptions":["5 описаний для VK до 300 символов"],"youtube_titles":["5 заголовков YouTube до 70 символов"],"tiktok_descriptions":["5 описаний TikTok до 300 символов"],"hashtags":["15 хэштегов"],"bio_text":"текст для био"}}"""
