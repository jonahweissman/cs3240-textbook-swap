# Textbook Swap
[![Build Status](https://travis-ci.com/uva-cs3240-s20/project-101-textbook-swap.svg?token=TLmEs1yASFdWYyqTLXkm&branch=master)](https://travis-ci.com/uva-cs3240-s20/project-101-textbook-swap)

> This project was created for CS 3240 Advanced Software Development Methods at the University of Virginia by Ashish Upadhyaya, Charles Fang, Hart Lukens, Matt Newberry, Jonah Weissman, and Nitesh Parajuli.

Textbook Swap is a marketplace for textbooks. Students can sell a textbook by posting a listing in the "Add Listing" tab, specifying information about the book and its condition (and optionally providing the ISBN to allow automatic filling of some fields). Buyers can find the textbook by name, author, or ISBN using the search feature. Once they've found what they're looking for, buyers can ask questions or arrange a pickup with the seller by clicking on a listing and then clicking "Contact seller." Both the buyer and seller are notified of new messages by email. They can respond to messages either by replying to the notification email or by going to the conversations page by clicking "View messages" on a listing. After payment and item exchange have occurred in person, the seller can go to their listing under the "My Listings" tab and update the status to "sold," so it will not be displayed to any more buyers.

### Citations for major services and libraries
- [Django](https://github.com/django/django/blob/master/LICENSE)
- [Bootstrap](https://github.com/twbs/bootstrap/blob/master/LICENSE)
- [PostgreSQL](https://www.postgresql.org/about/licence/)
- [CloudMailIn](https://www.cloudmailin.com/terms)
- [Google Books API](https://developers.google.com/terms/)
- [AWS S3](https://aws.amazon.com/service-terms/)

### Set up

Note: set up will require creating accounts with many different services and probably is more trouble than it's worth.

You will need a PostgreSQL database running. Create a file named `.env` with the following contents
```
DATABASE_URL=postgres://user:password@localhost:5432/db_name
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
CLOUDMAILIN_CREDENTIALS='user:password'
CLOUDMAILIN_ID=...
EMAIL_HOST_USER=...@gmail.com
EMAIL_HOST_PASSWORD=...
SECRET_KEY=...
DEBUG=True
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=....apps.googleusercontent.com
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=...
```
with AWS credentials to a publicly accessible S3 bucket named `django-textbook`.

Make sure to install the the dependencies, apply migrations, and collect
static files with
```
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic
```
