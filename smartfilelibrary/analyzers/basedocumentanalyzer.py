import os
import re
import abc
import fitz
from PIL import Image
from smartfilelibrary.config import config

class BaseDocumentAnalyzer(metaclass=abc.ABCMeta):
    """Document analyzer base class. Provides core functionality."""
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

    def get_pagecount(self):
        """
        Get the page count of the document. Be sure to first pass the
        document path using analyze."""
        try:
            doc = fitz.open(self.path)
            pc = doc.page_count
            doc.close()
        except:
            return 0
        return pc

    def get_publishing_year(self):
        """
        Get the publishing year of this document.
        """
        year = None
        try:
            doc = fitz.open(self.path)
            pdfmeta = doc.metadata
            if "creationDate" in pdfmeta and pdfmeta["creationDate"] not in (None, ""):
                m = re.search("[1-2][0-9][0-9][0-9]", pdfmeta["creationDate"])
                if m is not None:
                    year = pdfmeta["creationDate"][m.span()[0] : m.span()[1]]
            doc.close()
        except:
            pass
        return year

    @abc.abstractmethod
    def get_extraction_name(self):
        """Get the name of the method to extract metadata."""
        ...

    @abc.abstractmethod
    def get_title(self):
        """
        Get the title of this document.
        """
        ...

    @abc.abstractmethod
    def get_publisher(self):
        """
        Get the publisher of this document.
        """
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