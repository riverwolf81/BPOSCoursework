# Raspberry Pi 5 Buildroot Project

This repository contains my custom Buildroot project for the Raspberry Pi 5, including three packages. This includes my overlays and configuration.

## Contents

- `configs/raspberrypi5_filemgr_config`  
  Contains my .config file

- `board/raspberrypi5/`  
  Contains overlays and changes to the files needed to run on the Raspberry Pi 5.

- `package/filemgr/`, `package/filebrowser/`, `package/filemgr_web/`  
  The three custom packages included in this project. These directories include the package definition files and source code.

- `.gitignore`  
  Standard Buildroot gitignore file to prevent uploading generated build artifacts or downloaded sources. Auto-generated via my terminal.

## How to Access the Files from a Terminal 

```bash
# 1. Clone the repository and enter it
git clone https://github.com/riverwolf81/BPOSCoursework.git
cd BPOSCoursework

# 2. Configure WiFi
cd board/raspberrypi/rootfs_overlays/etc
nano wpa_supplicant.conf
# Inside nano, add your network details like this -

# For Home WIFI
# network={
#     ssid="YOUR_WIFI_NAME"
#     psk="YOUR_WIFI_PASSWORD"
# }

#For EDUROAM:
#network={
#    ssid="eduroam"
#    key_mgmt=WPA-EAP
#    eap=PEAP
#    identity="EMAIL"
#    password="YOUR PASSWORD"
#    phase2="auth=MSCHAPV2"
#}

# Then save and exit: CTRL+X -> Y -> Enter
