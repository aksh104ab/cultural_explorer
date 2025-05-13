import pandas as pd
import snowflake.connector
import os

# Use relative path (recommended)
csv_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'tourism_stats.csv')

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
for _, row in df.iterrows():
    cursor.execute(
        """
        INSERT INTO tourism_stats (state, year, domestic_arrivals)
        VALUES (%s, %s, %s)
        """,
        (row['state'], int(row['year']), int(row['domestic_arrivals']))
    )

cursor.close()
conn.close()

print("✅ Data inserted successfully into tourism_stats table.")
