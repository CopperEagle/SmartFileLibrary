"""The DatabaseInterface is the main programming interface to the user."""

import os
import pickle
from typing import Collection

from .crossref_db import getDB
from .utilities import get_books, write_actions_to_db

import psycopg2
try:
	from transformers import pipeline
except ImportError:
	print("ERROR: COULD NOT IMPORT TRANSFORMERS. "
		"AI model functionality will thus not be available.\n"
		"Fix by executing 'pip3 install transformers'.")
	def pipeline(**kwargs):
		def func(arg, **kwargs):
			return [{"generated_text":""}]
		return func




class DatabaseInterface:
	"""Interfaces with a database and will make sure that all actions are committed. Furthermore,
	it will log all that has been executed such that mistakes can be undone by redoing everything."""
	MAXOUTPUTLENGTH = 2048
	MAXENTRYCROSSREF = 240000

	def __init__(self, dbname : str = "library", user : str = "user", password : str = "pw"):
		"""This is the constructor.

		Parameters
		-----------
		dbname : str
			Database name in PostgreSQL.
		user : str
			The name of the user in PostgreSQL.
		password : str
			The password for the user in PostgreSQL.
		"""
		self.conn = psycopg2.connect(
		host="localhost",
		database=dbname,
		user=user,
		password=password)
		self.cur = self.conn.cursor()
		self.logfile = "locallog.txt"


		self.publishers_added = {}
		self.book_id = 0
		self.pub_id = 0
		self.collection_id = 0
		self.form = {'book' : 1, 'lecture document' : 2, 'exercise' : 3,
			'website' : 4, 'collection' : 5, 'notes' : 6, 'research article' : 7, 
			'data' : 8, 'code' : 9}
		self.topics = []

	def execute(self, command : str):
		"""
		Execute a SQL statement.

		Parameters
		-----------
		command : str
			SQL string to execute.
		"""
		self.cur.execute(command)
		ret = None
		try:
			ret = self.cur.fetchall()
		except psycopg2.ProgrammingError:
			pass

		with open(self.logfile, 'a') as f:
			f.write(command + "\n")
		return ret

	def executefile(self, file : str, update_param : bool = True):
		"""
		Execute file containing SQL statements.
		NOTE: May commit. See update_param.

		Parameters
		-----------
		file : str
			Filepath of said file.
		update_param : bool
			Reflect changes also onto the Python side. True unless you know what you do.
			Setting this False and then adding new entries may corrupt your database.
			Note: If true then this commits!
		"""
		with open(file, "r") as f:
			read = "".join(f.readlines())
		self.execute(read)
		if update_param:
			self._update_parameters()

	def addbook(self, title : str, year : int, pub_id : int, form : str, topics : Collection[str], 
			favorite : bool = False, addunknowntopics : bool = True) -> int: 
		"""
		Add a book to the database. Returns the id of the book.

		Parameters
		-----------
		title : str
			Title of the book.
		year : int
			Publishing year.
		pub_id : int
			Publisher ID returned from addpublisher.
		form : str
			One of 'book','lecture document', 'exercise',
			'website', 'collection', 'notes', 'research article',
			'dataset', 'code'
		topics : collection of str
			Collection of topics.
		favourite : bool
			Favourite status
		addunknowntopics : bool
			Whether ot automatically add topics that were not yet registered.
			If False, will throw ValueError if topic was not registered before.
		"""

		if len(title) > 100:
			raise ValueError(f"[Error] {title} too long")
		if title is None:
			raise ValueError(f"[Error] Need title not None.")

		if isinstance(topics, str):
			topics = (topics,)			

		f = self.form[form.lower()]

		if pub_id is None:
			pub_id = 'NULL'

		if year is None:
			self.execute(f'''INSERT INTO book (title, pub_id, form_id, favorite)'''
				f''' VALUES ('{title}', {pub_id}, {f}, {favorite});''')
		else:
			self.execute(f'''INSERT INTO book (title, year, pub_id, form_id, favorite)'''
				f''' VALUES ('{title}', {year}, {pub_id}, {f}, {favorite});''')
		self.book_id += 1

		if topics is not None:
			for t in topics:
				self.checktopic(t, addunknowntopics)
				self.execute(f'''INSERT INTO book_topic (book_id, '''
					f'''topic_name) VALUES ({self.book_id}, '{t}');''')


		return self.book_id

	def _update_parameters(self):
		"""
		If you replay from a file, you must afterwards update some parameters
		that are stored on the Python side. If you call executefile, 
		you should call this to reflect the changes also on the Python side.
		"""
		self.conn.commit()
		self.cur = self.conn.cursor()
		self.cur.execute("SELECT COUNT(*) FROM Book;")
		self.book_id = self.cur.fetchall()[0][0]
		self.cur.execute("SELECT pub_id, name FROM Publisher;")

		for pub_id, name in self.cur.fetchall():
			self.publishers_added[name] = pub_id

		self.pub_id = len(self.publishers_added)
		self.cur.execute("SELECT topic_name FROM Topic;")

		for t in self.cur.fetchall():
			topic = t[0]
			if topic not in self.topics:
				self.topics.append(topic)

	def addtopics(self, topics : Collection[str]):
		"""
		Register a topic.

		Parameters
		-----------
		topics : collection of str
			Collection of topics to be registered.
		"""
		for t in topics:
			self.topics.append(t)
			self.execute(f'''INSERT INTO Topic (topic_name) VALUES ('{t}');''')

	def checktopic(self, topic : str, addunknowntopics : bool = True):
		"""
		Check if topic was registered. If addunknowntopics is False,
		will throw ValueError if unknown. Else will register the topic.

		Parameters
		-----------
		topic : str
			Name of the topic.
		addunknowntopics : bool
			Whether to register the topic if unknown.
		"""
		if not topic in self.topics:
			if not addunknowntopics:
				raise ValueError(f"[Error] {topic} is unknown topic.")
			else:
				self.addtopics((topic, ))

	def subtopic(self, base : str, sub : str, addunknowntopics : bool = True):
		"""
		Register a subtopic relationship.

		Parameters
		-----------
		base : str
			The supertopic.
		sub : str
			The subtopic.
		addunknowntopics : bool
			If any of the topics is unknown then wither register or
			throw ValueError. True results in the former behavior.
		"""
		self.checktopic(base, addunknowntopics)
		self.checktopic(sub, addunknowntopics)
		self.execute(f'''INSERT INTO subtopic_of (basetopic_name, subtopic_name) VALUES ('{base}', '{sub}');''')

	def addpublisher(self, name : str):
		"""
		Register a publisher. Returns the publisher ID.
		
		Parameters
		-----------
		name : str
			The name of the publisher.
		"""
		name = name.lower()
		if name in self.publishers_added:
			return self.publishers_added[name]

		self.execute(f'''INSERT INTO Publisher (name) VALUES ('{name}');''')
		self.pub_id += 1
		self.publishers_added[name] = self.pub_id
		return self.pub_id

	def addfile(self, book_id : int, path : str, num_pages : int, subname : str = ""):
		"""
		Register a file.

		Parameters
		-----------
		book_id : int
			Value returned by the addbook method.
		path : str
			THe filepath of the file.
		num_pages : int
			The number of pages this PDF has.
		subname : str
			Secondary name like 'Chapter 2'. Especially useful if one book is made of
			several files.
		"""
		if len(path) > 100:
			raise ValueError(f"[Error] Too long path {path}")

		if num_pages is None:
			self.execute('''INSERT INTO File (book_id, filepath, subname)'''
				f''' VALUES ({book_id}, '{path}', '{subname}');''')
		else:
			self.execute('''INSERT INTO File (book_id, filepath, num_pages, subname)'''
				f''' VALUES ({book_id}, '{path}', {num_pages}, '{subname}');''')


	def finish(self, commit : bool = True):
		"""
		Save changes and close the database,

		Parameters
		-----------
		commit : bool
			If False, it will not save the changes.
		"""
		print(f"[Info] Closing library database connection.")
		self.cur.close()
		if commit:
			self.conn.commit()
		self.conn.close()

	def cleardb(self):
		"""
		Clear the contents of the DB and setup the plain tables again.
		"""
		with open(self.logfile, "w") as f:
			f.write("") # make sure that the file is overwritten
		try:
			self.execute("DROP TABLE Publisher, Form, Book, File, "
				"Topic, subtopic_of, book_topic, UseCase, usecase_book;")
		except:
			print("[Error] Removing tables error: Probably first run.")
			self.conn.commit()
			self.cur = self.conn.cursor()
		self.execute(self.SQLSETUP)

	def cancel_transaction(self):
		"""
		Recovers from an error from the DB. Will revert the state to the last commit.
		Thus, it cancels the current transaction.
		"""
		self.conn.cancel()

	def commit_transaction(self):
		"""
		Commits the transaction. The equivalent of a savegame: If an error now appears,
		the transaction is saved.
		"""
		self.conn.commit()

	def standardsetup(self):
		"""
		Insert some typical values into the DB. You may check them out by
		calling this method and then looking at the logfile.
		"""
		self.execute('''INSERT INTO Form (form_name) VALUES
			('book'), -- ID == 1
			('lecture document'),
			('exercise'),
			('website'),
			('collection'),
			('notes'),
			('research article'), -- ID == 7;
			('dataset'),
			('code');
		''')
		self.addtopics(('Geography', 'Meteorology', 'Naval', 'Airspace',
			'Geolocation', 'Naval Traffic', 'Air Traffic', "No-Keywords-Available-No-Title"))
		self.subtopic('Computer Science', 'Data Science')
		self.subtopic('Computer Science', 'CS Tools')
		self.subtopic('Data Science', 'Data Management')
		self.subtopic('Data Science', 'Data Gathering')
		self.subtopic('Data Management', 'SQL')
		self.subtopic('Data Science', 'Artificial Intelligence')
		self.subtopic('Artificial Intelligence', 'Deep Learning')
		self.subtopic('Artificial Intelligence', 'Machine Learning')
		self.subtopic('Deep Learning', 'LLMs')
		self.subtopic('Data Management', 'Image Data')
		self.subtopic('Data Management', 'Accoustic Data')
		self.subtopic('Data Management', 'Text Data')
		self.subtopic('Geography', 'Geolocation')
		self.subtopic('Naval', 'Naval Traffic')
		self.subtopic('Airspace', 'Air Traffic')

	def preview_all(self, filesdir : str, pub : str, 
		to_file : str = "preview_db.py", fetch_metadb : bool = True):
		"""Try to automatically generate the entries into the DB, given some file directory.
		WIll not make any changes to the DB, instead will preview all changes into a
		Python file.

		Parameters
		-----------
		filesdir : str
			The directory of the files.
		pub : str
			The publisher name of the files in the directory.
		to_file : str
			The filepath where the preview will be saved.
		fetch_metadb : bool
			Whether to try to fetch the metadata DB from crossref.
		"""
		dbname = f"{ pub.replace(' ', '_') }_crossref_mdb.dump"
		if not os.path.exists(dbname) and fetch_metadb:
			db = getDB(pub, formtype="book", max_results = self.MAXENTRYCROSSREF)
			with open(dbname, "wb") as f:
				pickle.dump(db, f)
		elif not getDB:
			db = []
		else:
			print("[Info] Found previous metadata DB. Loading.")
			with open(dbname, "rb") as f:
				db = pickle.load(f)
			print("[Info] Loading metadata DB done.")
		pub_id = self.addpublisher(pub)
		books = get_books(filesdir, db, self._chat)
		write_actions_to_db(books, to_file, pub_id, filesdir)

	def _chat(self, inp : str):
		return ""

	def set_keywords_model(self, model : str, tokenizer : str):
		"""Set the location of the model used to generate the keywords.
		See the tutorial for more information.

		Parameters
		-----------
		model : str
			The location of the model.
		tokenizer : str
			The location of the tokenizer.
		"""
		print(f"[Info] Loading model at {model}.")
		model = pipeline(task= 'text2text-generation', 
		    model=model, tokenizer=tokenizer)
		print(f"[Info] Done loading model!")

		def chat(self, inp : str):
		    return model(inp, max_length=self.MAXOUTPUTLENGTH, do_sample=True)[0]['generated_text']
		self._chat = chat

	SQLSETUP = """
CREATE TABLE Publisher(
	pub_id SERIAL PRIMARY KEY, 
	name VARCHAR(20)
);

CREATE TABLE Form(
	form_id SERIAL PRIMARY KEY,
	form_name VARCHAR(20) UNIQUE
);

CREATE TABLE Book(
	book_id SERIAL PRIMARY KEY, 
	title VARCHAR(100) NOT NULL,
	year INT,
	pub_id INT,
	form_id INT,
	favorite BOOL default false,

	CONSTRAINT publisher FOREIGN KEY (pub_id) REFERENCES Publisher
		ON DELETE SET NULL ON UPDATE CASCADE,

	CONSTRAINT form FOREIGN KEY (form_id) REFERENCES Form
		ON DELETE SET NULL ON UPDATE CASCADE
);

CREATE TABLE File(
	book_id INT,
	collection_id SERIAL,
	filepath VARCHAR(100) UNIQUE,
	num_pages INT,
	subname VARCHAR(20) DEFAULT '',

	PRIMARY KEY(book_id, collection_id),

	CONSTRAINT bookentity FOREIGN KEY (book_id) REFERENCES Book
		ON DELETE CASCADE ON UPDATE CASCADE -- File is weak entity linked to book
);


CREATE TABLE Topic(
	topic_name VARCHAR(40) PRIMARY KEY
);

CREATE TABLE subtopic_of(
	basetopic_name VARCHAR(40),
	subtopic_name VARCHAR(40),

	PRIMARY KEY(basetopic_name, subtopic_name),

	CONSTRAINT basetopicname FOREIGN KEY (basetopic_name) REFERENCES Topic
		ON DELETE CASCADE ON UPDATE CASCADE, -- update: change name of topic, delete: no longer a thing here

	CONSTRAINT subtopicname FOREIGN KEY (subtopic_name) REFERENCES Topic
		ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE book_topic(
	book_id INT,
	topic_name VARCHAR(40),

	PRIMARY KEY(book_id, topic_name),

	CONSTRAINT bookentity FOREIGN KEY (book_id) REFERENCES Book
		ON DELETE CASCADE ON UPDATE CASCADE,

	CONSTRAINT basetopicname FOREIGN KEY (topic_name) REFERENCES Topic
		ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE UseCase(
	usecase_id SERIAL PRIMARY KEY,
	name VARCHAR(30) NOT NULL,
	source VARCHAR(20),
	metadata_path VARCHAR(100) UNIQUE
);

CREATE TABLE usecase_book(
	book_id INT,
	usecase_id INT,

	PRIMARY KEY(book_id, usecase_id),

	CONSTRAINT bookentity FOREIGN KEY (book_id) REFERENCES Book
		ON DELETE CASCADE ON UPDATE CASCADE,

	CONSTRAINT usecaseentity FOREIGN KEY (usecase_id) REFERENCES UseCase
		ON DELETE CASCADE ON UPDATE CASCADE

);"""


	
