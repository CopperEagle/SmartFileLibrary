"""Utilities for the DatabaseInterface."""

import re
import os
import pickle
import time
from typing import Union, Callable, Collection, Tuple

SEARCHMETHOD = "ISBN"
DIGIT_AT_END = r"(.*) [0-9]+$"

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

def get_books(directory : str, metalib : list, 
	chat : Callable[str, str]) -> Collection[Tuple[str, str, list, Union[dict, None]]]:
	"""
	Get the books from the given directory. Will try to retreive the title,
	path, keywords and metadata for each file.

	Parameters
	-----------
	directory : str
		The directory from which to get the files from.
	metalib : list
		The metadata db from crossref.
	chat : Callable str -> str
		The model functionality, input in, answer out.
	"""
	what = os.listdir(directory)
	bookannotated = []

	for book in what:
		libbk = _search(book, metalib)
		try:
			title = libbk['title'][0]
		except KeyError:
			libbk = None
			title = book
		except TypeError:
			title = book

		answer = chat(f"Please give keywords what sciences this book is about: '{title}'")
		time.sleep(1)
		answer = chat(f"Please extract the keywords mentioned in this book description and list these comma seperated: {answer}")
		time.sleep(1)
		answer = answer.replace(".", ",")
		answer = answer.split(",")
		if answer[-1] == "":
			del answer[-1]
		if len(answer) == 1:
			answer = answer[0].split(" - ")
		elif len(answer) == 0:
			answer = ["no-keywords-available"]
		for i in range(len(answer)):
			answer[i] = answer[i].strip()

		for i in range(len(answer) - 1, -1, -1):
			if ":" in answer[i]:
				del answer[i]
		#print(f"{title} : {answer}")

		bookannotated.append((title, book, answer, libbk))

	return bookannotated


def _getnumpages(path : str) -> int:
	"""Retreive the number of pages for this pdf.

	Parameters
	-----------
	path : str
		The path of the book (pdf) in question.
	"""
	os.system(f"pdfinfo {path} > local_quick_pdf_pylib_analysis0453454.txt")
	with open("local_quick_pdf_pylib_analysis0453454.txt", "r") as f:
		a = f.readlines()
	
	os.remove("local_quick_pdf_pylib_analysis0453454.txt")
	for i in a:
		if i.startswith("Pages:"):
			return int(i.split(":")[1].strip())


def _cleankeywords(kws : Collection[str]) -> Collection[str]:
	"""
	Cleans the keywords list a bit, removing some trivial answers.

	Parameters
	-----------
	kws : collection of strings
		The list of keywords.
	"""
	for i in range(len(kws) - 1, -1, -1):
		kws[i] = kws[i].title()
		if kws[i] in ("Book", "Science", "Sciences", "", "Books"):
			del kws[i]
			continue
		if kws[i].startswith("- "):
			kws[i] = kws[i][2:]
			if kws[i] == "":
				del kws[i]
				continue
		m = re.match(DIGIT_AT_END, kws[i])
		if m is not None:
			kws[i] = m.group(1)
	return kws

def write_actions_to_db(books : Collection[Tuple[str, str, list, Union[dict, None]]],
		 result_file : str, pub_id : int, filesdir : str) -> None:
	"""
	Write actions into Python file.

	Parameters
	-----------
	books : str
		The output from get_books.
	result_file : str
		Path for the Python file.
	pub_id : int
		The publisher ID.
	filesdir : str
		The directory for the files in question.
	"""
	with open(result_file, "w") as f:
		f.write(f"def add_books(db):\n\tpublisher = {pub_id}\n")
		for (title, path, answer, meta) in books:
			fullpath = os.path.join(filesdir, path)
			year = None
			answer = list(set(_cleankeywords(answer)))
			try:
				year = meta['created']['date-parts'][0][0]
			except:
				pass
			try:
				year = meta['issued']['date-parts'][0][0]
			except:
				pass
			try:
				year = meta['published']['date-parts'][0][0]
			except:
				pass

			insert = f"""\tbook_id = db.addbook('{title}', {year}, publisher, 'book', """ + \
			f"""{answer})\n\tdb.addfile(book_id, "{fullpath}", {_getnumpages(fullpath)})\n\n"""

			f.write(insert)
