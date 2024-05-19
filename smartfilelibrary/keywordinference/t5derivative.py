import os
import re
import fitz
from PIL import Image
from smartfilelibrary.config import config
from .basekeywordinference import BaseKeywordInference
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import pipeline


class T5Derivative(BaseKeywordInference):
    """Document analyzer base class. Provides core functionality."""

    HUGGINGFACE_NAME = "MBZUAI/LaMini-Flan-T5-783M"
    MAXOUTPUTLENGTH = 2048

    def __init__(self):
        self._tokenizer = None
        self.model = None
        self._model = None

    def get_extraction_name(self):
        """Get the name of the method to extract metadata."""
        return self.HUGGINGFACE_NAME

    def get_keywords(self, title : str):
        """Get the keywords."""
        return self.model(title, max_length=self.MAXOUTPUTLENGTH, do_sample=True)[0]['generated_text']

    def load(self, model_loc : os.PathLike = "", proc_loc : os.PathLike = ""):
        """
        Load the model.
        Will always try to use the cached model unless not available.
        If not available locally, it will fetch the savetensor version
        from Huggingface.

        Parameters:
        ------------
        model_loc : os.PathLike
            The location of the previously saved model. Leave empty to load from
            the web or the system cache.
        proc_loc : os.PathLike
            The location of the previously saved tokenizer. Leave empty to load
            from the web or the system cache.
        """
        print(f"[Info] Loading keywords extractor model {self.HUGGINGFACE_NAME}")
        self._tokenizer = AutoTokenizer.from_pretrained(self.HUGGINGFACE_NAME)
        self._model = AutoModelForSeq2SeqLM.from_pretrained(self.HUGGINGFACE_NAME, 
            revision="refs/pr/6", use_safetensors=True)

        self.model = pipeline(task= 'text2text-generation', 
            model=self._model, tokenizer=self._tokenizer)
        print(f"[Info] Done loading model!")


    def save(self, model_loc : os.PathLike, proc_loc : os.PathLike, 
        sharding_size : str = "200MB"):
        """
        Save the model.
        Can only be called after load(). Can save the model at a given
        location. Can be loaded from later again. Note that this is not
        necessary: The huggingface library will save the model in the system
        cache too. However, if you clear your cache regularly, this function
        is helpful.

        Parameters:
        ------------
        model_loc : os.PathLike
            The location to save the model to.
        proc_loc : os.PathLike
            The location to save the tokenizer to.
        sharding_size : str
            The shard size. Allows smoother loading.
        """
        self._tokenizer.save_pretrained(proc_loc)
        self._model.save_pretrained(model_loc", max_shard_size=sharding_size)