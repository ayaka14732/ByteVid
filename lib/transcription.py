import os
import subprocess
from typing import Optional

def transcribe(work_dir: str, filename_preprocessed: str, language: Optional[str]=None, device: str='cuda'):
    language_option = [] if not language else ('--language', language)
    file_in = os.path.join(work_dir, filename_preprocessed)
    subprocess.run(('whisper', '--device', device, '--task', 'transcribe', *language_option, '--output_dir', work_dir, file_in))
