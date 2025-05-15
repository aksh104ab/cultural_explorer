import pandas as pd
import snowflake.connector
#from dotenv import load_dotenv
import os

# Load environment variables from .env file
#load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), '..', 'pass.env'))

# Use relative path (recommended)
csv_file = os.path.join(os.path.dirname(__file__), '..', 'data', 'tourism_stats.csv')

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
