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

1. Clone the repository:

```bash
git clone https://github.com/riverwolf81/BPOSCoursework.git
cd BPOSCoursework

2. Making Wifi Work
You will need to add your Wifi ID and Password to the wpa_Supplicant.conf file found at the following location:
```bash
cd BPOSCoursework
cd /board/raspberrypi5/rootfs_overlays/etc
