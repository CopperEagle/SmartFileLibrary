import os
import re
import abc
import fitz
from PIL import Image
from smartfilelibrary.config import config

class BaseKeywordInference(metaclass=abc.ABCMeta):
    """Document keywords extractor base class. Provides core functionality."""
    def __init__(self):
        self.image = None
        self.path = None

    def analyze(self, path : os.PathLike):
        """Prepare PDF file.

        Parameters:
        ------------
        path : os.PathLike
            The path of the PDF file.
        """
        if not path.lower().endswith(".pdf"):
            raise ValueError(f"Can only analyze PDFs! Violating instance: {path}")
        if not os.path.isfile(path):
            raise ValueError(f"Need an existing PDF! Violating instance: {path}")
        self.path = path
        self._get_image(path)

    def _get_image(self, path : os.PathLike) -> Image:
        """Get image from PDF file, page 0.

        Parameters:
        ------------
        path : os.PathLike
            The path of the PDF file.
        """
        doc = fitz.open(path)
        page = doc.load_page(0)
        pix = page.get_pixmap(matrix = fitz.Matrix(2,2))
        if config["DEBUG"]:
            pix.save("debug-frontpage.png")
        self.image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()

    @abc.abstractmethod
    def get_keywords(self, title : str):
        """Get the keywords."""
        ...

    @abc.abstractmethod
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
        ...

    @abc.abstractmethod
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
        ...