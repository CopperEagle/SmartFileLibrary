"""Utilities for the DatabaseInterface."""

import re
import os
import pickle
import time
from typing import Union, Callable, Collection, Tuple

from tqdm import tqdm

from .analyzers.donut_base_finetuned import BaseDocumentAnalyzer

SEARCHMETHOD = "ISBN"
DIGIT_AT_END = r"(.*) [0-9]+$"

def get_books(directory : str, metadata_extractor : BaseDocumentAnalyzer,
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

	for bookfilename in tqdm(what, desc="Analyzing books"):
		metadata_extractor.analyze(os.path.join(directory, bookfilename))
		
		title = metadata_extractor.get_title()
		numpages = metadata_extractor.get_pagecount()
		publisher = metadata_extractor.get_publisher()
		year = metadata_extractor.get_publishing_year()

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

		bookannotated.append((title, bookfilename, answer, publisher, year, numpages))

	return bookannotated


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
		 result_file : str, filesdir : str, dbinstance) -> None:
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
		f.write(f"def add_books(db):\n")
		for (title, bookfilename, answer, publisher, year, numpages) in books:
			fullpath = os.path.join(filesdir, bookfilename)
			answer = list(set(_cleankeywords(answer)))

			f.write(f"\t# Set publisher as '{publisher}':\n")
			f.write(f"\tpublisher_id = db.addpublisher('{publisher}')\n")
			
			insert = "\t# book_id = db.addbook(title (not filepath!), year, publisher_id, form, keywords)\n"
			insert += f"""\tbook_id = db.addbook('{title}', {year}, publisher_id, 'book', """ + \
			f"""{answer})\n\tdb.addfile(book_id, "{fullpath}", {numpages})\n\n"""

			f.write(insert)
