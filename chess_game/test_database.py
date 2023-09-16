import sqlite3

def print_game_history_from_database():
    print("Printing game history from database...")
    # Connect to the database (or create it if it doesn't exist)
    connection = sqlite3.connect("game_history.db")
    cursor = connection.cursor()

    # Select all rows from the game_history table
    cursor.execute("SELECT * FROM game_history")

    # Print the game history
    for row in cursor:
        print(f"Game ID: {row[1]}")
        print(f"Game History:\n{row[2]}")
        print("-" * 40)  # Separator

    # Close the connection
    connection.close()

print_game_history_from_database()
