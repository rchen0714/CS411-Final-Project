# Permission:
# chmod +x delete_cache.sh

#!/bin/bash

# Deletes all __pycache__ and .pytest_cache folders recursively

echo "Deleting __pycache__ folders..."
find . -type d -name "__pycache__" -exec rm -rf {} +

echo "Deleting .pytest_cache folders..."
find . -type d -name ".pytest_cache" -exec rm -rf {} +

echo "Cache cleared!"