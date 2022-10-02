from lib.video_preprocessing import speedup_1_6x_and_excerpt_first_30min
from lib.transcription import transcribe
from lib.transcript_postprocessing import transcript_to_article
from lib.translation import translate
from lib.keyphrase_extraction import extract_keyphrase
from lib.summarisation import summarise
from lib.keyframe_determination import determine_keyframes
from lib.slides_detection import extract_slides

if __name__ == '__main__':
    work_dir = 'testdir'
    language = None

    filename_preprocessed = speedup_1_6x_and_excerpt_first_30min(work_dir)
    transcribe(work_dir, filename_preprocessed, language=language)
    article = transcript_to_article(work_dir)
    article_translated = translate(article)
    keyphrases = extract_keyphrase(article)
    summaries = summarise(article)
    keyframe_paths = determine_keyframes(work_dir, summaries)
    extracted_paths = extract_slides(work_dir, keyframe_paths)
