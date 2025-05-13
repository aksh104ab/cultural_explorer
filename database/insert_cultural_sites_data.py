import pandas as pd
import snowflake.connector
import os

# Use relative path (recommended)
csv_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'cultural_sites.csv')

# Load the CSV file
df = pd.read_csv(csv_file)

# Connect to Snowflake
conn = snowflake.connector.connect(
    user='aksnow',
    password='Aks@snowflake123',
    account='NDXGPOT-GY59263',
    warehouse='CULTURAL_WH',
    database='CULTURAL_DB',
    schema='CULTURAL_SCHEMA'
)

cursor = conn.cursor()

# Insert each row
# ...existing code...
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO cultural_sites (site_name, state, art_form, seasonality, responsible_score, latitude, longitude, image_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            row['site_name'],
            row['state'],
            row['art_form'],
            row['seasonality'],
            float(row['responsible_score']),
            float(row['latitude']),
            float(row['longitude']),
            row['image_url']
        )
    )
# ...existing code...

cursor.close()
conn.close()

print("✅ Data inserted successfully into cultural_sites table.")
