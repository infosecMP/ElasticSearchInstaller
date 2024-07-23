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
sudo apt-get update && sudo apt-get upgrade -y
print_ok

# Perform a dist-upgrade to handle dependencies
print_header "Performing dist-upgrade..."
sudo apt-get dist-upgrade -y
print_ok

# Install apt-transport-https
print_header "Installing apt-transport-https..."
sudo apt-get install apt-transport-https -y
print_ok

# Install Python 3, pip, virtualenv, and other necessary packages
print_header "Installing Python 3, pip, virtualenv, fortune, lolcat, and cowsay..."
sudo apt-get install python3 python3-pip python3-venv fortune lolcat cowsay -y
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

# Create a folder for Elasticsearch certificates
print_header "Creating a folder for Elasticsearch certificates..."
sudo mkdir -p /etc/elasticsearch/certificates
print_ok

# Add Elasticsearch GPG key directly to the new keyring
print_header "Adding Elasticsearch GPG key..."
wget -qO - https://artifacts.elastic.co/GPG-KEY-elasticsearch | sudo gpg --dearmor -o /usr/share/keyrings/elasticsearch-keyring.gpg
print_ok

# Save the repository definition
print_header "Saving Elasticsearch repository definition..."
echo "deb [signed-by=/usr/share/keyrings/elasticsearch-keyring.gpg] https://artifacts.elastic.co/packages/8.x/apt stable main" | sudo tee /etc/apt/sources.list.d/elastic-8.x.list
print_ok

# Update package lists
print_header "Updating package lists..."
sudo apt-get update
print_ok

# Install Elasticsearch
print_header "Installing Elasticsearch..."
sudo apt-get install elasticsearch -y
print_ok

# Enable and start Elasticsearch service
print_header "Enabling and starting Elasticsearch service..."
sudo systemctl enable elasticsearch
sudo systemctl start elasticsearch
print_ok

# Confirm installations
print_header "Confirming installations..."
python --version
print_ok
echo -e "\n\n"
pip --version
print_ok
echo -e "\n\n"
pip show psutil
print_ok
echo -e "\n\n"
pip show termcolor
print_ok
echo -e "\n\n"

echo "Setup complete. To use the virtual environment, run 'source /opt/elasticsearch_env/bin/activate'."

# Ensure the commands are executed without sudo to avoid permission issues
fortune | cowsay | lolcat
