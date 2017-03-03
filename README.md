# Project: Item Catalog APP
##### by Shijie Wang
---


### Overview:
A web application that provides a list of items from the database, allow users to edit and delete the catalog with details within a integration of third-party(facebook and google) user registration and authentication. Both the CRUD communication between database and the server, and the HTTP communication between client and server are implemented by the Flask Framework. 


### How to access the APP:

IP Address: 54.159.128.223

SSH port: 2200

URL: http://54.159.128.223

username: grader

ssh key: located in "linuxCourseFinalProject.pub" file

**ssh login sample code:**

`ssh -i linuxCourseFinalProject.pub grader@54.159.128.223 -p 2200`

### Software installed on the server:

* Amazon Lightsail
* Flask
* Apache2
* mod_wsgi
* PostgreSQL
* Python 2.7 
* vagrant
* finger

### Configuration changed:

* create a new user: `sudo adduser grder`
* create a new file in sudoers: `sudo nano /etc/sudoers.d/grader`
* change the grader permission: `grader ALL=(ALL:ALL) ALL`
* update and upgrade installed package: `sudo apt-get update`, `sudo apt-get upgrade`
* change SSH port from 22 to 2200: `sudo nano /etc/ssh/sshd_config`
* configure firewalls: 
	* `sudo ufw allow 2200/tcp`
	* `sudo ufw allow 80/tcp`
	* `sudo ufw allow 123/udp`
	* `sudo ufw enable`

* configure the local time time to UTC: `sudo dpkg-reconfigure tzdata`
* install apache2: `sudo apt-get install apache2`
* install mod_wsgi: 
	* Run sudo apt-get install libapache2-mod-wsgi python-dev
	* Enable mod_wsgi with sudo a2enmod wsgi
	* Start the web server with sudo service apache2 start
* deploy the catalog APP:
	* Install git using: sudo apt-get install git
	* cd /var/www
	* sudo mkdir catalog
	* Change owner of the newly created catalog folder `sudo chown -R grader:grader catalog`
	* cd /catalog
	* Clone your project from github git clone https://github.com/sxw031/Udacity-Fullstack-Catalog.git
	* Create a catalog.wsgi file, then add this inside
* install the virtual enviornment:
	* Install the virtual environment: `sudo pip install virtualenv`
	* Create a new virtual environment: `sudo virtualenv venv`
	* Activate the virutal environment: `source venv/bin/activate`
	* Change permissions `sudo chmod -R 777 venv`
	* Deactivate the virtual envrionment: `deactivate`
* install Flask and other dependencies:
	* Install pip: `sudo apt-get install python-pip`
	* Install Flask: `pip install Flask`
	* Install other project dependencies: `sudo pip install httplib2 oauth2client sqlalchemy psycopg2 sqlalchemy_utils`
* configure a new virtual host: `sudo nano /etc/apache2/sites-available/catalog.conf`
* enable the virtual host: `sudo a2ensite catalog`
* install postgreSQL
	* `sudo apt-get install libpq-dev python-dev`
	* `sudo apt-get install postgresql postgresql-contrib`
	* `sudo su - postgres`
	* `psql`
	* `\q`, or `exit`
* configure postgreSQL
	* CREATE USER catalog WITH PASSWORD 'happy123';
	* ALTER USER catalog CREATEDB;
	* CREATE DATABASE catalog WITH OWNER catalog;
	* \c catalog
	* REVOKE ALL ON SCHEMA public FROM public;
	* GRANT ALL ON SCHEMA public TO catalog;
* change the create_engine line in `__init__.py` and databasesetup:
	* `engine = create_engine('postgresql://catalog:@localhost/catalog')
* restart apache2: `sudo service apache2 restart`

### Reference used:
1. How To Deploy a Flask Application on an Ubuntu VPS
https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps


2. Engine Configuration.
http://docs.sqlalchemy.org/en/latest/core/engines.html#postgresql


3. How To Install and Use PostgreSQL on Ubuntu 14.04
https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04


4. fix error: opening file "g_client_secret.json"
https://discussions.udacity.com/t/invalidclientsecretserror-error-opening-file-g-client-secrets-json-no-such-file-or-directory-2/163046


5. Fix error: facebook login URL blocked:
http://stackoverflow.com/questions/37001004/facebook-login-message-url-blocked-this-redirect-failed-because-the-redirect