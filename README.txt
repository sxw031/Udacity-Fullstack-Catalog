# Project: Item Catalog APP
##### by Shijie Wang
---

### Overview:
A web application that provides a list of items from the database, allow users to edit and delete the catalog with details within a integration of third-party(facebook and google) user registration and authentication. Both the CRUD communication between database and the server, and the HTTP communication between client and server are implemented by the Flask Framework. 

### Enviornment setup:
This APP uses:
* Flask
* SQLAlchemy
* Python 2.7

Please install these dependencies before you run the app. The easiest way to do it by these command below in the virtual machine:
```
pip install Flask
pip install SQLAlchemy
```

### How to run the APP:
This project uses a pre-configured vagrant virtual machine installed which includes the Flask.

1. Clone my repository
2. Log in to the virtual machine by command by
    ```
    $ cd vagrant
    $ vagrant up
    $ vagrant ssh
    ```
3. Running the application by
    ```
    $ cd /vagrant/catalog
    $ python application.py
    ```
4. Navigate to localhost:8888 on your favorite browser to play with the APP.
