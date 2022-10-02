# mumbling-monitor

## Prerequisites

The application requires the command-line tool `ffmpeg` to be installed on your system, which is available from most package managers:

### on Ubuntu or Debian

```sh
sudo apt update && sudo apt install ffmpeg
```

### on Arch Linux

```sh
sudo pacman -S ffmpeg
```

### on MacOS using Homebrew (https://brew.sh/)

```sh
brew install ffmpeg
```

### on Windows using Chocolatey (https://chocolatey.org/)

```sh
choco install ffmpeg
```

### on Windows using Scoop (https://scoop.sh/)

```sh
scoop install ffmpeg
```

## Deploy

```sh
## create an virtual environment
python3.10 -m venv venv
. ./venv/bin/activate

## install packages
pip install -U pip
pip install -U wheel
pip install -r requirements.txt

## download model weights
wget https://github.com/ztjhz/yolov7-slides-extraction/releases/download/v1.0/best.pt

## set API access key
export BAIDU_APP_ID=_BAIDU_APP_ID
export BAIDU_APP_KEY=_BAIDU_APP_KEY

## start the server
flask --app app run
```
