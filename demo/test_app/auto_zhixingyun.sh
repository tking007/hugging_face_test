#!/bin/bash

# Move file
mv frpc_linux_amd64_v0.2 /home/vipuser/anaconda3/lib/python3.9/site-packages/gradio

# Change directory
cd test_app/ || exit

# Install Python requirements
pip install -r requirements.txt

# Update system packages
sudo apt-get update

# Install psmisc
sudo apt-get install psmisc

# Uninstall gradio
pip uninstall gradio

# Remove gradio directory
rm -rf /home/vipuser/anaconda3/lib/python3.9/site-packages/gradio

# Install specific version of gradio
pip install gradio==4.25 accelerate

# Run Python script
python Qwen_web_demo.py --share --inbrowser --server_name=0.0.0.0 --server_port=20238