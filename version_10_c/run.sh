#!/bin/bash

# Virtual environment setup and activation
# Automatically activates venv whether creating new or using existing
if [ ! -d "venv" ]; then
    python3 -m venv venv
    . venv/bin/activate
    venv/bin/pip install --upgrade pip
    venv/bin/pip install -r requirements.txt
else
    . venv/bin/activate
fi


echo "Virtual environment setup complete"
echo "To activate in your current shell, run:"
echo "source venv/bin/activate"
