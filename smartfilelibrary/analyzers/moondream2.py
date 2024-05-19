import re
import os
import torch
from PIL import Image
from transformers import AutoModelForCausalLM, AutoTokenizer

from .basedocumentanalyzer import BaseDocumentAnalyzer
from smartfilelibrary.config import config


class Moondream2(BaseDocumentAnalyzer):
    """Analyzer using the Moondream2 model by vikhyatk. Good for small devices."""

    HUGGINGFACE_NAME = "vikhyatk/moondream2"
    REVISION = "2024-05-08"

    def __init__(self):
        super(Moondream2, self).__init__()
        self.tokenizer = None
        self.model = None
        self.device = None
        self.enc_image = None

    def load(self, model_loc : os.PathLike = "", proc_loc : os.PathLike = ""):
        """
        Load the model.
        Note that the paths are ignored, because this model requires setup code to be running
        that cannot be explicitly saved to a specified directory. Huggingface complains
        when trying to load from a specified file directory.

        Parameters:
        ------------
        model_loc : os.PathLike
            The location of the previously saved model. Leave empty to load from
            the web or the system cache.
        proc_loc : os.PathLike
            The location of the previously saved tokenizer. Leave empty to load
            from the web or the system cache.
        """
        if config["DEBUG"]:
            print(f"Loading model {self.HUGGINGFACE_NAME}")

        self.tokenizer = AutoTokenizer.from_pretrained(HUGGINGFACE_NAME, revision=REVISION, trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            HUGGINGFACE_NAME, revision=REVISION, trust_remote_code=True
        )
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if config["DEBUG"]:
            print(f"Loading model {self.HUGGINGFACE_NAME} done: Processing device {self.device}")
        self.model.to(self.device)

    def save(self, model_loc : os.PathLike, proc_loc : os.PathLike, sharding_size : str = "200MB"):
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
        self.tokenizer.save_pretrained(model_loc)
        self.model.save_pretrained(proc_loc, max_shard_size=sharding_size)

    def get_extraction_name(self):
        """Get the name of the method to extract metadata."""
        return self.HUGGINGFACE_NAME

    def _get_image(self, path : os.PathLike):
        """Get the image of the first page and encode the image.
        """
        super(Moondream2, self)._get_image(path)
        self.enc_image = model.encode_image(self.image)

    def get_title(self):
        """
        Get the title of this document.
        """
        return self._ask("What is the title?")

    def get_publisher(self):
        """
        Get the publisher of this document.
        """
        return self._ask("What is the name of the publisher? Just return the name.")

    def _ask(self, question : str):
        """
        Send question to the model. Must call analyze(pdffilepath) first.

        Parameters:
        ------------
        question : str
            The question to ask.
        """
        if (self.model is None):
            raise ValueError("Must load model first.")
        if (self.enc_image is None):
            raise ValueError("Must encode image first")
        return self.model.answer_question(self.enc_image, question, self.tokenizer)