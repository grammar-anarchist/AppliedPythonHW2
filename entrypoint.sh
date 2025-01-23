#!/bin/sh

FLAG_FILE="/app/.db_setup_done"

if [ ! -f "$FLAG_FILE" ]; then
    echo "Database setup required. Running db_setup.py..."
    echo "YES" | python /app/db_setup.py

    if [ $? -eq 0 ]; then
        echo "Database setup completed successfully."
        touch "$FLAG_FILE"  # Mark the setup as done
    else
        echo "Database setup failed. Exiting..."
        exit 1
    fi
else
    echo "Database setup already completed. Skipping db_setup.py."
fi

echo "Starting bot.py..."
exec python /app/bot.py
