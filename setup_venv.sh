#!/bin/bash

# Set the name of the virtual environment directory
VENV_DIR=venv
REQUIREMENTS_FILE=requirements.txt

# Check if the virtual environment already exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv $VENV_DIR          # ✅ Actually creates the venv folder

  echo "Activating virtual environment..."
  source $VENV_DIR/bin/activate      # ✅ Activates the venv right away

  #export PYTHONPATH=$(pwd):$PYTHONPATH
  #echo "PYTHONPATH set to: $PYTHONPATH"   # Optional: Print to verify
  # Figure out how to set this in the venv activate script later, going to manually try now****

  # Install dependencies
  if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing dependencies from $REQUIREMENTS_FILE..."
    pip install --upgrade pip        # ✅ Always good to upgrade pip first
    pip install -r $REQUIREMENTS_FILE
  else
    echo "Error: $REQUIREMENTS_FILE not found."
    exit 1
  fi
else
  echo "Virtual environment already exists. To activate it, run:"
  echo "source $VENV_DIR/bin/activate"
fi

source $VENV_DIR/bin/activate