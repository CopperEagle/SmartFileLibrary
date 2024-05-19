
# The semiautonomous process

The process takes a directory and then writes all entries as a **function in a python file**. This allows the user to check the entries that are to be added to make sure all additions meet expectations. In some cases, this process can be augmented with the `crossref` public metadata database.

## Overview
The process has two components.
- The inference of metadata of the document. This includes the title, publishing year and publisher.
- The keyword generation for this document.

For now, these two components are seperated and may be done with different or the same methods.


## The metadata inference

Currently, the project supports three options. Recommended is option 3.

- Option `PDFMETA`: Inference using the metadata of the pdf file and optionally the `crossref` database. This option takes as arguments whether `crossref` should be used and the publisher name.
- Option DONUTFT: Inference using a document question and answer AI model, [this one](https://huggingface.co/naver-clova-ix/donut-base-finetuned-docvqa).
- Option MOONDREAM2: Using the moondream2 model. Requirements are no less than 8GB RAM.

```py
from smartfilelibrary import DatabaseInterface
from smartfilelibrary.methodconstants import *


db = DatabaseInterface("library", "user", "password")
db.cleardb()
db.standardsetup()

option = PDFMETA # enter your selection

if option == PDFMETA:
    db.set_metadata_method(PDFMETA, fetch_metadb = True, publisher = "MyPublisher")
else:
    db.set_metadata_method(MOONDREAM2)
db.preview_all("testdir", "preview_db.py")

# Now, there should be a file called preview_db.py with a function.
# This will add entries to the db in the above (manual) style.
# Proceed, if you agree with the output:
from preview_all import add_books
add_books(db)

# Commit all changes
db.finish()

```

Note, to use the `crossref` database: **The assumption currently is that the file's name is its own ISBN.** It can then retreive the actual title, publishing year, etc.

## The keyword inference
All that is needed is a single line, indicating the method to use. Currently, only one option exists.

T5DERIVATIVE: A derivative of Google's T5. Retreives the keywords from the title.

Work is ongoing to support other models and also APIs like the one for ChatGPT.

```py
from smartfilelibrary import DatabaseInterface
from smartfilelibrary.methodconstants import *


# Enter credentials to local DB.
db = DatabaseInterface("dbname", "user", "password")
db.cleardb()
db.standardsetup()

db.set_metadata_method(MOONDREAM2)
db.set_keywords_model(T5DERIVATIVE)
db.preview_all("this/directory", "preview_db.py")

# Now, there should be a file called preview_db.py with a function.
# This will add entries to the db in the above (manual) style.
# Proceed, if you agree with the output:
from preview_all import add_books
add_books(db)

# Commit all changes
db.finish()

```