#!/usr/bin/env bash

# Stop on error
set -e

echo "🔧 Starting Chrome installation..."

# Create directory for Chrome inside project (Render's persistent path)
mkdir -p .render/chrome
cd .render/chrome

# Download the latest stable Chrome Debian package
curl -sSL https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb -o chrome.deb

# Extract Chrome binary files (dpkg-deb instead of dpkg to avoid install issues)
dpkg-deb -x chrome.deb .

# Clean up
rm chrome.deb

echo "✅ Chrome installed at: $(pwd)/opt/google/chrome/chrome"
