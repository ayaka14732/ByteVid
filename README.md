# ByteVid

The ByteVid project is made up of a number of repositories. Apart from this repository, here are the other repositories that you might be also interested in:

- [yolov7-slides-extraction](https://github.com/ztjhz/yolov7-slides-extraction)
- [ByteVidFrontend](https://github.com/xJQx/ByteVidFrontend)
- [ByteVidExtension](https://github.com/ztjhz/ByteVidExtension)

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

## Develop

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

## Deploy

```sh
waitress-serve --host 127.0.0.1 --port 31346 app:app
```

## How we built it

### Frontend

- React.js
- Tailwind CSS
- Deploy on GitHub pages

### Backend

- Flask server
- Deploy on a GPU machine
- Relay to an Internet-facing VPS
- Nginx reverse proxy
- Cloudflare protection

### Deep Learning

- [Whisper](https://github.com/openai/whisper): SOTA speech recognition (Sep 2022)
- [YOLOv7](https://github.com/WongKinYiu/yolov7): SOTA object detection (Jul 2022)
- [KBIR-inspec](https://huggingface.co/ml6team/keyphrase-extraction-kbir-inspec): key phrase extraction (Dec 2021)
- [Bert Extractive Summarizer](https://pypi.org/project/bert-extractive-summarizer/): summarisation (Jun 2019)
- [BlingFire](https://github.com/microsoft/BlingFire): sentence extraction
- [Baidu Translate API](https://api.fanyi.baidu.com/doc/21): translation

### Tools

- OpenCV
- youtube-dl
- ffmpeg
