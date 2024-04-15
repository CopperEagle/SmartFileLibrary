"""The metadata database loading utilities, using the crossref API."""
import time
import pickle
from crossref_commons.iteration import iterate_publications_as_json

def _find_pdf_entry(l):
	for elt in l:
		if elt['content-type'] == 'application/pdf':
			return elt
	return None


def getDB(pub_name : str, formtype : str, max_results : int):
	"""
	Get metadata DB from crossref.

	Parameters
	-----------
	pub_name : str
		The publisher name.
	formtype : str
		The form, like 'book', see DatabaseInterface.
	max_results : int
		Maximum number of entries.
	"""
	filter = { 'type' : formtype }
	queries = { 'query.publisher-name' : pub_name }
	fullinfo = []
	i = 0	
	ts = time.monotonic()
	print(f"[Info] Start fetching crossref DB for publisher {pub_name}. This may take a while...")
	for p in iterate_publications_as_json(max_results=max_results + 1, filter=filter, queries=queries):
		try:
			elt = _find_pdf_entry(p['link'])
		except KeyError:
			elt = p
		if elt is None:
			continue
		fullinfo.append(p)
		i += 1
	print(f"[Info] Fetched {i} entries from crossref on publisher {pub_name} in {time.monotonic() - ts} seconds")
	if i < 2:
		print(f"[Warning] Something has gone wrong finding the DB for the publisher {pub_name} "
			"on crossref. Are you sure you use the correct name? "
			"For more information, take a look at the official crossref website.")
		return []
	return fullinfo