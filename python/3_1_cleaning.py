import pandas as pd
import pycountry


def clean_events_data(file_path):
    try:
        df = pd.read_csv(file_path, dtype=str)
    except Exception as e:
        print(f"Критична помилка читання файлу: {e}")
        return pd.DataFrame(), pd.DataFrame()

    print(f"Початково завантажено рядків: {len(df)}")

    # Очищення ревеню
    if 'revenue_usd' in df.columns:
        raw_revenue = df['revenue_usd'].str.replace(',', '.', regex=False)
        numeric_revenue = pd.to_numeric(raw_revenue, errors='coerce')
        unparseable_count = numeric_revenue.isna().sum()
        print(f"Report: Replaced {unparseable_count} unparseable/empty revenue values with 0.0")
        df['revenue_usd'] = numeric_revenue.fillna(0.0)

    # Нормалізація країн
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
                country = pycountry.countries.lookup(val)
                return country.alpha_2
            except LookupError:
                return 'XX'

        # apply замість циклу проводить по функції всі рядки.
        df['country'] = df['country'].apply(normalize_country)


    # Парсинг часових міток у формат UTC
    time_columns = ['event_time', 'ingested_at']
    for col in time_columns:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)

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

    # Дедуплікація
    if 'event_id' in df.columns and 'ingested_at' in df.columns:
        df = df.sort_values(by=['event_id', 'ingested_at'], ascending=[True, False])
        df = df.drop_duplicates(subset=['event_id'], keep='first')

    clean_df = df.copy()
    return clean_df, quarantine_df


if __name__ == '__main__':
    FILE_PATH = '../data/events_raw.csv'
    clean_data, bad_data = clean_events_data(FILE_PATH)

    print("\n--- ЧИСТІ ДАНІ (перші 5 рядків) ---")
    print(clean_data.head().to_string())

    print("\n--- КАРАНТИН (перші 5 рядків) ---")
    print(bad_data.head().to_string())