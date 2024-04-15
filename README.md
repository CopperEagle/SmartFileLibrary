# SmartFileLibrary

[![Python](https://img.shields.io/badge/Python-3.10-3776AB.svg?style=flat&logo=python&logoColor=white)](https://www.python.org)
![Version](https://img.shields.io/badge/SmartFileLibrary_version-0.0.1-darkgreen)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


The problem this project in development tries to fix are local folders full of PDFs, code snippets and datasets, that typically have very nontelling filenames (like DOI numbers).

SmartFileLibrary is is an digital library, backed by a local database hosted by PostgreSQL. It allows to organize a collection of files to constitute a virtual book under a different title and location, adding keywords, usecases and other metadata, among other things.

The project's goal is to semiautomatically insert documents from local directories into the library. This includes LLM based analysis of documents to infer metadata and supply keywords. Semiautonomous insertion can be augmented for scientific papers using the API for the `crossref` metadata database. In the future, an AI model may be used to read off all required metadata from the PDF itself.

To strengthen privacy, the project focuses on running as much functionality *locally* as possible.

## Features

The project is ongoing. Some features are still in development.

#### Currently available
- Local database to organize the files.
- AI generated keywords based on the *title* of the file. If the actual title cannot be inferred from the `crossref` database, the filename will be used for now.
- Enhance the automated process for scientific works using the `crossref` metadata database.

#### Future
- Infer metadata like titles, keywords from PDF content using LLMs for analysis.
- Webinterface (GUI) for queries, etc.


## Installing
The project is written for Linux, Python 3.10+ and has a number of additional requirements

- PostgreSQL 14.11
- pdfinfo 22.02 for basic PDF metadata
- (optionally, see below) a text-to-text model from Huggingface to generate keywords

Optionally, you may setup a virtual environment.

```bash
python3 -m venv path/to/new/venv
cd path/to/new/venv
source bin/activate
```

Then download the code, navigate into that directory and run

```bash
pip3 install -r requirements.txt
pip3 install .
```


## Basic Use

### Setup

First, you need to setup an account over on PostgreSQL and a database. You likely do not want to use the default database which is named after the user account. 

### Manual insertion

The fallowing demonstrates the fully manual insertion of a publisher and a book into the DB. Note that all actions are being logged into a file called `locallog.txt`. This allows you to clear the DB later on and **replay** your previous actions.

```py
from smartfilelibrary import DatabaseInterface


db = DatabaseInterface("dbname", "user", "password")
# remove any previous tables and insertions
# Good practice to reset any counters.
db.cleardb()

## Replay previous actions:
# db.executefile(locallog.txt) 

# inserts a number of standard values
db.standardsetup()

# Add publisher, returns ID, required for adding books
apress = db.addpublisher("Apress")

# Add topics and subtopics
db.subtopic('Data Science', 'Database')
db.subtopic('Database', 'SQL')

# Add book and a file corresponding to this book (there may be many files per book)
sqlbook = db.addbook('Expert Performance Indexing in Azure SQL and SQL Server 2022', 
    2023, apress, 'book', ('SQL', ))
db.addfile(sqlbook, "path/to/book1.pdf", 300, "First Half")
db.addfile(sqlbook, "path/to/book2.pdf", 349, "Second Half")

# Commit all changes
db.finish()

```
The above registers a publisher, then a book by giving the title, publishing date, publisher, form and keywords.
Then, a book consists of one or several files, one is added with book_id, path and number of pages.

Now this all seems pretty boring to do, right? We may want to speed this process up a notch. This project is still at the beginning of doing so.

### Semiautomated process

The process takes a directory and a publisher name (string, may be empty), and then writes all entries as a **function in a python file**. This allows the user to check the entries that are to be added to make sure all additions meet expectations.

For *scientific literature*, this process is augmented with the `crossref` public metadata database. **The assumption currently is that the file's name is its own ISBN.** It can then retreive the actual title, publishing year, etc. If it is *not* scientific literature, then it will currently default to using filenames in the directory as titles. An LLM will be optionally used to infer keywords from the title. 


#### Step 1 (optional): Setup LLM model

The current version of this software infers keywords from the title. If the title from the crossref library is not available, then it will use the filename, which may not be helpful. Currently, a **locally run** AI model is used. The fallowing sets up a small (~ 3.2GB) but relatively capable model from Huggingface. You can use a different model, given you can use it with the `pipeline` function from `transformers`. For the time being, APIs like the one for ChatGPT are not yet allowed.

First, we need the transformers library:

```bash
pip3 install transformers==4.34.0

```

Then, we need to install the model locally. The model is being sharded to allow smooth loading and running in standard 8 GB RAM environments. Also, safetensors are being used.

```py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from transformers import pipeline

tokenizer = AutoTokenizer.from_pretrained("MBZUAI/LaMini-Flan-T5-783M")
tokenizer.save_pretrained("./tokenizer")

model = AutoModelForSeq2SeqLM.from_pretrained("MBZUAI/LaMini-Flan-T5-783M", revision="refs/pr/6", use_safetensors=True)
model.save_pretrained("./model", max_shard_size="200MB")
```

Doing it this way allows to avoid redownloading the model while also not having it hidden in some shadowy cache directory. You only need to execute the above once.

#### Step 2: Semiautomated Process

The `preview_all` method triggers the semiautomated process. It is only *semi* because no actual actions are performed on the DB. Instead, the actions are written into a Python file. You may then take a look, check and modify. Execute the function once you agree.

```py
from smartfilelibrary import DatabaseInterface


db = DatabaseInterface()
# Good practice to reset any counters.
db.cleardb()
# inserts a number of standard values
db.standardsetup()

# Add publisher
apress = db.addpublisher("Apress")

# Add topics and subtopics
db.subtopic('Data Science', 'Database')
db.subtopic('Database', 'SQL')

db.set_keywords_model(model="./model", tokenizer="./tokenizer")

# Automate book entry from said directory and publisher
# Write potential changes into preview_db.py
db.preview_all("this/directory", "Arxiv", "preview_db.py")

# Now, there should be a file called preview_db.py with a function.
# This will add entries to the db in the above (manual) style.
# Proceed, if you agree with the output:
from preview_all import add_books
add_books(db)

# Commit all changes
db.finish()

```


## The DB
The DB layout can be checked in ![setup.sql](setup.sql). It is in third normal form. Any higher was not required since no combinatoral recombination should be present. It contains the fallowing "objects":

- Book: Has properties title, Publisher, etc. May represent something other than books, like a codebase.
- File: A Book can consist of many files.
- Publisher: depending on the use, this may be the publishing company or the author
- Form: code, text, dataset, etc.
- Topic: keywords
- UseCase: the context(s) in which some resource is being used

Then, it also contains the reasonable relations:

- usecase_book: UseCase <-> Book; many to many
- book_topic: Book <-> Topic; many to many
- subtopic_of: Topic <-> Topic; many to many

The other relations like form_book, being either one-to-one or one-to-many have been folded into the object tables.

## Limitations

- Currently, this project can only do scientific publications fully automatically, thanks to the crossref metadata database and its free API access. These shortcommings could be reduced in the future by having AI models search the PDF for metadata like title, publisher, author, publishing year, etc.

- There is currently no option to use the ChatGPT API but this may be added in the future. This is currently not a priority since the goal is to rul locally as much as possible.


## TODOs
- Tests
- Give user direct access to the UseCase table, which is pretty useful...
- Make it crossplatform by removing the pdfinfo dependency and using a Python library instead.
- Use freely available PDF analyzing LLMs for more robust and informative output.
- Webinterface to actually use the DB
