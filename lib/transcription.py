import os
import subprocess
from typing import Optional

def transcribe(work_dir: str, filename_preprocessed: str, language: Optional[str]=None, device: Optional[str]=None):
    language_option = () if not language else ('--language', language)
    device_option = () if not device else ('--device', device)
    file_in = os.path.join(work_dir, filename_preprocessed)
    subprocess.run(('whisper', *device_option, '--task', 'transcribe', *language_option, '--output_dir', work_dir, file_in), check=True)
