import sqlite3

# Connect to the SQLite database
conn = sqlite3.connect('fashion_data.db')
cursor = conn.cursor()

# Specify the table name
table_name = 'fashion_sql'

# Fetch column names
cursor.execute(f"PRAGMA table_info({table_name})")
columns = cursor.fetchall()
column_names = [column[1] for column in columns]

# Check if column names are retrieved correctly
if not column_names:
    raise Exception("No columns found for the specified table. Please check the table name.")

# Construct the SQL query to delete rows with NULL values in any column
if column_names:
    # Escape column names with double quotes
    null_conditions = " OR ".join([f'"{col}" IS NULL' for col in column_names])
    delete_query = f"DELETE FROM {table_name} WHERE {null_conditions}"
else:
    raise Exception("No columns retrieved. Cannot construct query.")

print("Executing query:", delete_query)  # Debug: Print the query to check for syntax issues

try:
    # Execute the query
    cursor.execute(delete_query)

    # Commit the transaction
    conn.commit()
    
    print("Rows with NULL values have been deleted.")

except sqlite3.OperationalError as e:
    print(f"An operational error occurred: {e}")
except sqlite3.DatabaseError as e:
    print(f"A database error occurred: {e}")
except Exception as e:
    print(f"An unexpected error occurred: {e}")

# Close the connection
conn.close()
