import pandas as pd
import pycountry
import argparse
import os

def clean_events_data(file_path):
    # завантаження
    try:
        df = pd.read_csv(file_path, dtype=str)
    except Exception as e:
        print(f"Критична помилка читання файлу: {e}")
        return pd.DataFrame(), pd.DataFrame(), {}

    # МЕТРИКА 1: початкова кількість рядків
    rows_in = len(df)

    # Трансформація (Гроші, Країни, Дати)
    # Очищення фінансів
    if 'revenue_usd' in df.columns:
        raw_revenue = df['revenue_usd'].str.replace(',', '.', regex=False)
        numeric_revenue = pd.to_numeric(raw_revenue, errors='coerce')
        df['revenue_usd'] = numeric_revenue.fillna(0.0)

    # 2.2 Нормалізація країн
    if 'country' in df.columns:
        def normalize_country(val):
            if pd.isna(val):
                return 'XX'
            val = str(val).strip()
            if not val:
                return 'XX'
            if len(val) == 2 and val.isalpha():
                return val.upper()
            try:
                return pycountry.countries.lookup(val).alpha_2
            except LookupError:
                return 'XX'

        # apply замість циклу проводить по функції всі рядки.
        df['country'] = df['country'].apply(normalize_country)

    # Парсинг часових міток (UTC)
    time_columns = ['event_time', 'ingested_at']
    for col in time_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)

    # Генерація ключа для партиціювання Parquet
    if 'event_time' in df.columns:
        # Створюємо нову колонку, де буде ТІЛЬКИ дата (рік-місяць-день) у текстовому форматі
        df['event_date'] = df['event_time'].dt.strftime('%Y-%m-%d')

    # Видалення тестових рядків
    if 'is_test' in df.columns:
        test_mask = df['is_test'].astype(str).str.lower().str.strip() == 'true'
        df = df[~test_mask]

        # Карантин
    if all(col in df.columns for col in ['event_id', 'event_time', 'ingested_at']):
        bad_rows_mask = df['event_id'].isna() | df['event_time'].isna() | df['ingested_at'].isna()
        quarantine_df = df[bad_rows_mask].copy()
        df = df[~bad_rows_mask]
    else:
        quarantine_df = pd.DataFrame()

        # МЕТРИКА 2: скільки рядків пішло в карантин
    rows_quarantined = len(quarantine_df)

    # Дедуплікація
    duplicates_removed = 0
    if 'event_id' in df.columns and 'ingested_at' in df.columns:
        df = df.sort_values(by=['event_id', 'ingested_at'], ascending=[True, False])
        len_before_dedup = len(df)

        df = df.drop_duplicates(subset=['event_id'], keep='first')

        # МЕТРИКА 3: скільки рядків видалилось
        duplicates_removed = len_before_dedup - len(df)

    # Пакування результатів
    clean_df = df.copy()

    # МЕТРИКА 4: фінальна кількість чистих рядків
    rows_out = len(clean_df)

    # всі метрики
    metrics = {
        'rows_in': rows_in,
        'rows_out': rows_out,
        'duplicates_removed': duplicates_removed,
        'rows_quarantined': rows_quarantined
    }

    # повертаємо чисту таблицю, карантин і звіт
    return clean_df, quarantine_df, metrics


if __name__ == '__main__':
    # 1. Налаштовуємо парсер консольних команд
    parser = argparse.ArgumentParser(description='Очищення даних про події та збереження у Parquet.')
    parser.add_argument('--input_file', required=True, help='Шлях до сирого CSV файлу')
    parser.add_argument('--output_dir', required=True, help='Папка для збереження Parquet файлів')

    args = parser.parse_args()

    # 2. Запускаємо нашу функцію
    print(f"Починаємо обробку файлу: {args.input_file}...")

    # Викликаємо функцію і ловимо 3 об'єкти, які вона повертає
    clean_df, quarantine_df, metrics = clean_events_data(args.input_file)

    # 3. Базовий захист
    if clean_df.empty and quarantine_df.empty:
        print("Обробку зупинено: файл порожній або сталася критична помилка.")
        exit()  # Зупиняємо скрипт

    # 4. Збереження чистих даних у Parquet з партиціюванням
    if not clean_df.empty:
        # Створюємо головну папку (out/), якщо її ще не існує
        os.makedirs(args.output_dir, exist_ok=True)

        # Зберігаємо чисті дані
        clean_df.to_parquet(
            args.output_dir,
            partition_cols=['event_date'],  # Розбиваємо на папки за датою
            engine='pyarrow',
            index=False
        )
        print(f"✅ Чисті дані збережено у папку: {args.output_dir}")

        # Зберігаємо карантинні рядки окремо (якщо вони є)
    if not quarantine_df.empty:
        quarantine_path = os.path.join(args.output_dir, 'quarantine.csv')
        quarantine_df.to_csv(quarantine_path, index=False)

    # 5. Друк фінального звіту (One-line summary)
    print(f"Summary: In: {metrics['rows_in']} | Out: {metrics['rows_out']} | "
          f"Quarantined: {metrics['rows_quarantined']} | Duplicates: {metrics['duplicates_removed']}")