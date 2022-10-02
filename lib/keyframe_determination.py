from collections import namedtuple
import cv2
from glob import glob
import os
from pysrt import open as read_sub
from typing import Optional

Sub = namedtuple('Sub', ('start', 'end', 'text'))

def transcript_to_article(dir_in: str) -> list[Sub]:
    srt_file = glob(os.path.join(dir_in, '*.srt'))[0]
    subs = read_sub(srt_file)

    subs_new = []
    for sub in subs:
        sub_new = Sub(sub.start.ordinal, sub.end.ordinal, sub.text)
        subs_new.append(sub_new)
    return subs_new

def average(a: int, b: int) -> int:
    return (a + b) // 2

def match_summaries_with_timestamps(summaries: list[str], subs: list[Sub]) -> list[Optional[int]]:
    res = []
    for summary in summaries:
        done = False
        for sub in subs:
            if summary.startswith(sub.text):
                res.append(average(sub.start, sub.end))
                done = True
                break
        if not done:
            res.append(None)
    return res

def timestamps_to_images(video_path: str, dir_out: str, timestamps: list[Optional[int]]) -> list[Optional[str]]:
    video = cv2.VideoCapture(video_path)
    assert video.isOpened()
    res = []
    for i, timestamp in enumerate(timestamps):
        if timestamp is None:
            res.append(None)
        else:
            video.set(cv2.CAP_PROP_POS_MSEC, timestamp)  # in milliseconds
            ret, frame = video.read()
            img_name = f'keyframe_{i}.png'
            path_out = os.path.join(dir_out, img_name)
            cv2.imwrite(path_out, frame)
            res.append(img_name)
    video.release()
    return res

def determine_keyframes(work_dir: str, summaries: list[str]) -> list[Optional[str]]:
    video_file_orig = glob(os.path.join(work_dir, 'video.*'))[0]
    video_file = video_file_orig.replace('video.', 'preprocessed.')
    subs = transcript_to_article(work_dir)
    keyframe_timestamps = match_summaries_with_timestamps(summaries, subs)
    keyframe_paths = timestamps_to_images(video_file, work_dir, keyframe_timestamps)
    return keyframe_paths
