# Контроль финансов телеграм бот

# Calculating Finances telegram bot

## О проекте
Данный репозиторий содержит проект, представляющий собой телеграм-бота, который будет помогать вам контролировать и анализировать ваши расходы и доходы. Он включает в себя, генерацию синтетических данных и их анализ, а также реализацию бота на языке Python. 

## About The Project
This repository contains a project that is a Telegram bot that will help you monitor and analyze your expenses and income. It includes the generation of synthetic data and its analysis, as well as the implementation of the bot in Python.

## Структура проекта / Project structure

### Папка bot:

Данная папка содержит полностью рабочую реализацию бота на языке Phyton (в файл config.py необходиом добавить TELEGRAM_BOT_TOKEN).

### Bot folder

This folder contains a fully functional implementation of the bot in the Phyton language (add TELEGRAM_BOT_TOKEN to the config.py file).

### Папка data_generation:

Данная папка содержит сгенерированные синтетические данные о личных финансах пользователей за месяц (их доходы и расходы). Данные используются для демонстрации полезности телеграм-бота, визуализации финансовых проблем и дальнейшей их аналитики. 

JSON-файл содержит информацию для 100 пользователей:
1. user_id: Уникальный 9-значный идентификатор
2. name: Имя и фамилия
3. age: Возраст
4. gender: Пол
5. monthly_income: Месячные доходы
6. monthly_expense: Месячные расходы
7. difference: Разница между доходом и расходом
8. financial_status: Статус ("дефицит"/"профицит")

### Data_generation folder:

This contains generated synthetic data about user's personal finances for the month (their income and expenses). The data is used to demonstrate the Telegram bot's usefulness, visualize financial problems, and perform further analysis.

The JSON file contains information for 100 users:
1. user_id: Unique 9-digit identifier
2. name: First and last name
3. age: Age
4. gender: Gender
5. monthly_income: Monthly income
6. monthly_expense: Monthly expenses
7. difference: Difference between income and expenses
8. financial_status: Status ("deficit"/"surplus")

### Папка data_analysis:

Данная папка содержит анализ сгенерированных синтаксических данных. Анализ включает визуализацию данных, выявление ключевых проблем и обоснование полезности финансового телеграм-бота.

### Data_analysis folder:

This folder contains an analysis of the generated syntactic data. The analysis includes data visualization, identification of key issues, and justification of the usefulness of the financial telegram bot.

### Папка presentation

Данная папка содержит презентацию для выступления.

### Presentation folder

This folder contains a presentation for a speech.

## Автор / Author
Прохоренко С.А., ИСИБ-24-1, ИРНИТУ / Prokhorenko S.A., ISIB-24-1, IRNITU