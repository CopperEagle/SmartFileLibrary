import re
import os
import pickle
from typing import Union
import fitz
from PIL import Image

from smartfilelibrary.crossref_db import getDB
from .basedocumentanalyzer import BaseDocumentAnalyzer

def _search(pth : str, metalib : list) -> Union[None, dict]:
    """Search for the publication within the metadata db.

    Parameters
    -----------
    pth : str
        The path of the book (pdf) in question.
    metalib : list
        The metadata db from crossref.
    """
    isbn = pth.split(".")[0].replace("-", "")
    for book in metalib:
        try:
            if isinstance(book['ISBN'], list):
                if isbn in book['ISBN']:
                    return book
            elif book['ISBN'] == isbn:
                return book
        except KeyError:
            pass
    return None


class PdfMetaAnalyzer(BaseDocumentAnalyzer):
    """Analyzer using a finetuned version of the nougat model by facebook.
    This model is relatively old (2023). If you can, prefer Idefics2-8b.

    The memory requirements for this model are 3GB peak usage and 2GB average usage."""
    MAXENTRYCROSSREF = 240000

    NAME = "PDF Metadata"

    def __init__(self, fetch_metadb, publisher):
        super(PdfMetaAnalyzer, self).__init__()
        self.fetch_metadb = fetch_metadb
        self.pub = publisher
        self.db = []
        self.metabook = None
        self.book_path = None
        self.bookobj = None

    def load(self, model_loc : os.PathLike = "", proc_loc : os.PathLike = ""):
        """
        Load the model.
        Will always try to use the cached model unless not available.
        If not available locally, it will fetch the savetensor version
        from Huggingface.

        Parameters:
        ------------
        Parameters are for interface conformance. They will be ignored.
        """
        dbname = f"{ self.pub.replace(' ', '_') }_crossref_mdb.dump"
        if not os.path.exists(dbname) and self.fetch_metadb:
            self.db = getDB(self.pub, formtype="book", max_results = self.MAXENTRYCROSSREF)
            with open(dbname, "wb") as f:
                pickle.dump(self.db, f)
        elif not self.fetch_metadb:
            self.db = []
        else:
            print("[Info] Found previous metadata DB. Loading.")
            with open(dbname, "rb") as f:
                self.db = pickle.load(f)
            print("[Info] Loading metadata DB done.")

    def save(self, model_loc : os.PathLike, proc_loc : os.PathLike, sharding_size : str = "200MB"):
        """
        This method is for interface conformance.

        Parameters:
        ------------
        Will be ignored.
        """
        return None

    def analyze(self, path : os.PathLike):
        super().analyze(path)
        self.book_path = path
        self.metabook = _search(os.path.split(path)[1], self.db)
        if self.bookobj is not None:
            self.bookobj.close()
        self.bookobj = fitz.open(path)

    def get_extraction_name(self):
        """Get the name of the method to extract metadata."""
        return self.NAME

    def get_title(self):
        """
        Get the title of this document.
        """
        title = os.path.split(self.book_path)[1]
        try:
            title = self.metabook['title'][0]
        except:
            pass

        pdfmeta = self.bookobj.metadata
        if "title" in pdfmeta and pdfmeta["title"] not in (None, ""):
            title = pdfmeta["title"]

        return title

    def get_publisher(self):
        """
        Get the publisher of this document.
        """
        return self.pub

    def get_publishing_year(self):
        """
        Get the publishing year of this document.
        """
        year = super().get_publishing_year()
        
        try:
            year = self.metabook['created']['date-parts'][0][0]
        except:
            pass
        try:
            year = self.metabook['issued']['date-parts'][0][0]
        except:
            pass
        try:
            year = self.metabook['published']['date-parts'][0][0]
        except:
            pass
        return year
