#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 13 11:35:33 2024

@author: lichao
"""

mkdir -p ~/miniconda3
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda3/miniconda.sh
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh

~/miniconda3/bin/conda init bash
~/miniconda3/bin/conda init zsh

sudo reboot

conda create --name crawler python=3.9

conda activate crawler

pip install bs4 pandas selenium ipython google-cloud-bigquery pandas-gbq db-dtypes google-auth

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo apt install ./google-chrome-stable_current_amd64.deb

sudo apt-get update
sudo apt-get install chromium-chromedriver

google-chrome --version
chromedriver --version

nohup python CNKI_Crawler_headless.py >> log.txt &


#ipython

#from selenium import webdriver

#chrome_options = webdriver.ChromeOptions()
#chrome_options.binary_location = '/usr/bin/chromium-browser'  # Specify the path to chromedriver
#chrome_options.add_argument('--headless') 

#driver = webdriver.Chrome(options=chrome_options)

# Now you can use the driver object to interact with the browser
#driver.get("https://www.example.com")
