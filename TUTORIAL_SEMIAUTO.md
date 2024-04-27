
# The semiautonomous process

The process takes a directory and then writes all entries as a **function in a python file**. This allows the user to check the entries that are to be added to make sure all additions meet expectations. In some cases, this process can be augmented with the `crossref` public metadata database.

## Overview
The process has two components.
- The inference of metadata of the document. This includes the title, publishing year and publisher.
- The keyword generation for this document.

For now, these two components are seperated and may be done with different or the same methods.


## The metadata inference

Currently, the project supports two options:

- Option 1: Inference using the metadata of the pdf file and optionally the `crossref` database. This option takes as arguments whether `crossref` should be used and the publisher name.
- Option 2: Inference using a document question and answer AI model, [this one](https://huggingface.co/naver-clova-ix/donut-base-finetuned-docvqa).

```py
from smartfilelibrary import DatabaseInterface


db = DatabaseInterface("library", "user", "password")
db.cleardb()
db.standardsetup()

option = 1 # enter your selection

if option == 1:
    db.set_metadata_method(1, fetch_metadb = True, publisher = "MyPublisher")
else:
    db.set_metadata_method(2)
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

#### Step 1 (optional): Setup LLM model

The current version of this software infers keywords from the title. If the title from the crossref library is not available, then it will use the filename, which may not be helpful. Currently, a **locally run** AI model is used. The fallowing sets up a small (~ 3.2GB) but relatively capable model from Huggingface. You can use a different model, given you can use it with the `pipeline` function from `transformers`. For the time being, APIs like the one for ChatGPT are not yet supported.

First, we need the transformers library:

```bash
pip3 install transformers==4.40.0

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

#### Step 2: Use it

```py
from smartfilelibrary import DatabaseInterface

# Enter credentials to local DB.
db = DatabaseInterface("dbname", "user", "password")
db.cleardb()
db.standardsetup()

if option == 1:
    db.set_metadata_method(1, fetch_metadb = True, publisher = "MyPublisher")
else:
    db.set_metadata_method(2)

db.set_keywords_model(model="./model", tokenizer="./tokenizer")
db.preview_all("this/directory", "preview_db.py")

# Now, there should be a file called preview_db.py with a function.
# This will add entries to the db in the above (manual) style.
# Proceed, if you agree with the output:
from preview_all import add_books
add_books(db)

# Commit all changes
db.finish()

```