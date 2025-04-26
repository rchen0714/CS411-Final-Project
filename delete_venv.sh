VENV_DIR=venv

# Check if the virtual environment directory exists
if [ -d "$VENV_DIR" ]; then
  echo "Deleting virtual environment directory: $VENV_DIR"
  rm -rf $VENV_DIR  # Remove the virtual environment directory and all its contents
  deactivate
  echo "Virtual environment deleted."
else
  echo "No virtual environment found. Directory $VENV_DIR does not exist."
fi