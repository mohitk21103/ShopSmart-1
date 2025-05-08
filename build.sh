#!/usr/bin/env bash

# Install Google Chrome
apt-get update
apt-get install -y wget gnupg unzip curl
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
apt install -y ./google-chrome-stable_current_amd64.deb || apt-get -fy install

# Install ChromeDriver
CHROME_VERSION=$(google-chrome --version | grep -oP '[0-9.]+' | head -1)
CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION" || curl -s https://chromedriver.storage.googleapis.com/LATEST_RELEASE)
wget -N https://chromedriver.storage.googleapis.com/$CHROMEDRIVER_VERSION/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
mv chromedriver /usr/local/bin/
chmod +x /usr/local/bin/chromedriver
chmod +x build.sh
