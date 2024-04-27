import re
import os
import torch
import fitz
from PIL import Image
from transformers import VisionEncoderDecoderModel, DonutProcessor

from .basedocumentanalyzer import BaseDocumentAnalyzer
from smartfilelibrary.config import config


class DonutAnalyzer(BaseDocumentAnalyzer):
    """Analyzer using a finetuned version of the nougat model by facebook.
    This model is relatively old (2023). If you can, prefer Idefics2-8b.

    The memory requirements for this model are 3GB peak usage and 2GB average usage."""

    HUGGINGFACE_NAME = "naver-clova-ix/donut-base-finetuned-docvqa"

    def __init__(self):
        super(DonutAnalyzer, self).__init__()
        self.processor = None
        self.model = None
        self.device = None

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
        if config["DEBUG"]:
            print(f"Loading model {self.HUGGINGFACE_NAME}")
        self.processor = DonutProcessor.from_pretrained(self.HUGGINGFACE_NAME if proc_loc == "" else proc_loc)
        self.model = VisionEncoderDecoderModel.from_pretrained(self.HUGGINGFACE_NAME if model_loc == "" else model_loc,
            revision="refs/pr/15", use_safetensors=True)
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
        self.processor.save_pretrained(model_loc)
        self.model.save_pretrained(proc_loc, max_shard_size=sharding_size)

    def get_extraction_name(self):
        """Get the name of the method to extract metadata."""
        return self.HUGGINGFACE_NAME

    def get_title(self):
        """
        Get the title of this document.
        """
        a = self._ask("What is the title of this document? Please doublecheck your answer.")
        return a

    def get_publisher(self):
        """
        Get the publisher of this document.
        """
        return self._ask("What is the publisher of this document? It is usually written in a corner. Please doublecheck your answer.")

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
        prompt = f"<s_docvqa><s_question>{question}</s_question><s_answer>"
        decoder_input_ids = self.processor.tokenizer(prompt, add_special_tokens=False, return_tensors="pt").input_ids
        pixel_values = self.processor(self.image, return_tensors="pt").pixel_values

        outputs = self.model.generate(
            pixel_values.to(self.device),
            decoder_input_ids=decoder_input_ids.to(self.device),
            max_length=self.model.decoder.config.max_position_embeddings,
            pad_token_id=self.processor.tokenizer.pad_token_id,
            eos_token_id=self.processor.tokenizer.eos_token_id,
            use_cache=True,
            bad_words_ids=[[self.processor.tokenizer.unk_token_id]],
            return_dict_in_generate=True,

        )

        sequence = self.processor.batch_decode(outputs.sequences)[0]
        sequence = sequence.replace(self.processor.tokenizer.eos_token, "").replace(self.processor.tokenizer.pad_token, "")
        sequence = re.sub(r"<.*?>", "", sequence, count=1).strip()  
        return self.processor.token2json(sequence)["answer"]