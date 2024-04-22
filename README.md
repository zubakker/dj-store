# dj-store
A generic e-commerce backend app with
product tags, authorization on access/refresh tokens, search and
filtering, shopping cart, swagger documentation;

# How to run
1. Clone this Repository
2. Navigate to the directory with this README, then to 
3. Create virtualenv - Optional
```
python -m venv venv
source venv/bin/activate
# venv\Scripts\activate on Windows
```
4. Install the requirements for the package:
```
pip install -r requirements.txt
```
5. Apply migrations
```
python djstore/manage.py migrate
```
6. Create Superuser (optional)
```
python djstore/manage.py createsuperuser
```
7. Run the server
```
python djstore/manage.py runserver
```

# How to use
You can open swagger documentation on http://127.0.0.1:8000/swagger/ , all currently supported requests are documented there.
