import sqlite3
import pandas as pd

DB_PATH = "db/zoho_database.db"
OUTPUT_FILE = "chat_history.csv"  # Change to .xlsx for Excel

conn = sqlite3.connect(DB_PATH)

df = pd.read_sql_query("SELECT * FROM chat_history", conn)
df.to_csv(OUTPUT_FILE, index=False)

# Optional: Export to Excel
# df.to_excel("conversation_history.xlsx", index=False)

conn.close()
print(f"Data exported successfully to {OUTPUT_FILE}")
