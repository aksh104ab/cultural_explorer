import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'pass.env'))

# Use relative path (recommended)
csv_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'cultural_sites.csv')

# Load the CSV file
df = pd.read_csv(csv_file)

# Connect to Snowflake
conn = snowflake.connector.connect(
    user=os.environ['SNOWFLAKE_USER'],
    password=os.environ['SNOWFLAKE_PASSWORD'],
    account=os.environ['SNOWFLAKE_ACCOUNT'],
    warehouse=os.environ['SNOWFLAKE_WAREHOUSE'],
    database=os.environ['SNOWFLAKE_DATABASE'],
    schema=os.environ['SNOWFLAKE_SCHEMA']
)

cursor = conn.cursor()

# Insert each row into the table (with description)
for _, row in df.iterrows():
    cursor.execute("""
        INSERT INTO cultural_sites 
        (site_name, state, art_form, seasonality, responsible_score, latitude, longitude, image_url, describtion)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            row['site_name'],
            row['state'],
            row['art_form'],
            row['seasonality'],
            float(row['responsible_score']),
            float(row['latitude']),
            float(row['longitude']),
            row['image_url'],
            row['describtion']
        )
    )


cursor.close()
conn.close()

print("✅ Data inserted successfully into cultural_sites table.")


