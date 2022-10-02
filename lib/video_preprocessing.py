from glob import glob
import os
import subprocess

def speedup_1_6x(work_dir: str) -> str:
    file_in = glob(os.path.join(work_dir, 'video.*'))[0]
    file_out = file_in.replace('video.', 'preprocessed.')

    _, filename_preprocessed = os.path.split(file_out)

    subprocess.run(('ffmpeg', '-y', '-i', file_in, '-filter_complex', '[0:v]setpts=0.625*PTS[v];[0:a]atempo=1.6[a]', '-map', '[v]', '-map', '[a]', file_out), check=True)

    return filename_preprocessed
