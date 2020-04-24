# Textbook Swap
[![Build Status](https://travis-ci.com/uva-cs3240-s20/project-101-textbook-swap.svg?token=TLmEs1yASFdWYyqTLXkm&branch=master)](https://travis-ci.com/uva-cs3240-s20/project-101-textbook-swap)

Marketplace for textbooks

# Set up

You will need a PostgreSQL database running. Create a file named `.env` with the following contents
```
DATABASE_URL=postgres://user:password@localhost:5432/db_name
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```
with AWS credentials to an S3 bucket.

Make sure to install the the dependencies with
```
pip install -r requirements.txt
```
and to apply migrations with
```
python manage.py migrate
```
