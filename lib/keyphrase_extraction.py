# KBIR: https://arxiv.org/abs/2112.08547
# https://huggingface.co/ml6team/keyphrase-extraction-kbir-inspec

from transformers import (
    TokenClassificationPipeline,
    AutoModelForTokenClassification,
    AutoTokenizer,
)
from transformers.pipelines import AggregationStrategy
import numpy as np

# Define keyphrase extraction pipeline
class KeyphraseExtractionPipeline(TokenClassificationPipeline):
    def __init__(self, model, *args, **kwargs):
        super().__init__(
            model=AutoModelForTokenClassification.from_pretrained(model),
            tokenizer=AutoTokenizer.from_pretrained(model),
            *args,
            **kwargs
        )

    def postprocess(self, model_outputs):
        results = super().postprocess(
            model_outputs=model_outputs,
            aggregation_strategy=AggregationStrategy.SIMPLE,
        )
        return np.unique([result.get("word").strip() for result in results])

model_name = "ml6team/keyphrase-extraction-kbir-inspec"
extractor = KeyphraseExtractionPipeline(model=model_name)

def extract_keyphrase(article: str) -> list[str]:
    return list(extractor(article))

if __name__ == '__main__':
    # Inference
    text = """
    Keyphrase extraction is a technique in text analysis where you extract the
    important keyphrases from a document. Thanks to these keyphrases humans can
    understand the content of a text very quickly and easily without reading it
    completely. Keyphrase extraction was first done primarily by human annotators,
    who read the text in detail and then wrote down the most important keyphrases.
    The disadvantage is that if you work with a lot of documents, this process
    can take a lot of time. 

    Here is where Artificial Intelligence comes in. Currently, classical machine
    learning methods, that use statistical and linguistic features, are widely used
    for the extraction process. Now with deep learning, it is possible to capture
    the semantic meaning of a text even better than these classical methods.
    Classical methods look at the frequency, occurrence and order of words
    in the text, whereas these neural approaches can capture long-term
    semantic dependencies and context of words in a text.
    """.replace("\n", " ")

    keyphrases = extract_keyphrase(text)

    print(keyphrases)

    # Output
    # ['Artificial Intelligence' 'Keyphrase extraction' 'deep learning'
    #  'linguistic features' 'machine learning' 'semantic meaning'
    #  'text analysis']
