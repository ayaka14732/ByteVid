# Prerequisites

youtube-dl?

ffmpeg

# Deploy

```sh
python3.10 -m venv venv
. ./venv/bin/activate

pip install -U pip
pip install -U wheel
pip install "jax[cpu]==0.3.20"
pip install -r requirements.txt

wget https://github.com/ztjhz/yolov7-slides-extraction/releases/download/v1.0/best.pt

export BAIDU_APP_ID=_BAIDU_APP_ID
export BAIDU_APP_KEY=_BAIDU_APP_KEY

python main.py
```
