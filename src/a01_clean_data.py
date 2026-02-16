import pandas as pd
import matplotlib as mpl

def clean_data(filepath):

    df = pd.read_csv(filepath)

    # Datatype conversions
    df['date'] = pd.to_datetime(df['date'], utc=True).dt.tz_convert('US/Pacific').dt.tz_localize(None)
    df['is_weekend'] = df['is_weekend'].astype(bool)
    df['is_holiday'] = df['is_holiday'].astype(bool)
    df['is_start_of_semester'] = df['is_start_of_semester'].astype(bool)
    df['is_during_semester'] = df['is_during_semester'].astype(bool)

    # New columns
    df["year"] = df["date"].dt.year
    df["minute"] = df["date"].dt.round('10min')
    df["minute"] = df["minute"].dt.minute
    df["day"] = df["date"].dt.day
    df["day_of_week"] = df['date'].dt.day_name() # Original values were wrong + replace with Day name
    df['is_weekend'] = df["day_of_week"].isin(['Saturday', 'Sunday']) # Original values were wrong

    # Drop unnecessary / redundant columns
    df.drop(columns=["timestamp","temperature"], inplace=True)

    df['date_only'] = df['date'].dt.normalize() 
    mindate = df['date_only'].min()
    maxdate = df['date_only'].max()

    # Rename for clarity during merge
    df.rename(columns={'date_only': 'key_date'}, inplace=True)

    return df, mindate.strftime('%Y-%m-%d'), maxdate.strftime('%Y-%m-%d')

# df, mindate, maxdate = clean_data("../data/raw/data.csv")
# print(df, mindate, maxdate)