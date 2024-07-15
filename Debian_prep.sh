#!/bin/bash

# Function to print a header in yellow
print_header() {
  echo -e "\033[1;33m"
  echo "====================================="
  echo "  $1"
  echo "====================================="
  echo -e "\033[0m"
}

# Function to print OK message in green
print_ok() {
  echo -e "\033[1;32mOK\033[0m"
}

# Update Debian 12 to the latest
print_header "Updating Debian 12 to the latest..."
sudo apt update && sudo apt upgrade -y
print_ok

# Install Python 3, pip, virtualenv, and other necessary packages
print_header "Installing Python 3, pip, virtualenv, fortune, lolcat, and cowsay..."
sudo apt install python3 python3-pip python3-venv fortune lolcat cowsay -y
print_ok

# Create a virtual environment
print_header "Creating a virtual environment..."
python3 -m venv /opt/elasticsearch_env
print_ok

# Activate the virtual environment
print_header "Activating the virtual environment..."
source /opt/elasticsearch_env/bin/activate
print_ok

# Install necessary Python modules in the virtual environment
print_header "Installing necessary Python modules..."
pip install psutil
pip install termcolor
print_ok

# Confirm installations
print_header "Confirming installations..."
python --version
pip --version
pip show psutil
pip show termcolor
print_ok

echo "Setup complete. To use the virtual environment, run 'source /opt/elasticsearch_env/bin/activate'."

# Ensure the commands are executed without sudo to avoid permission issues
fortune | cowsay | lolcat
