
DROP TABLE Publisher, Form, Book, File, Topic, subtopic_of, book_topic, UseCase, usecase_book;

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

);
