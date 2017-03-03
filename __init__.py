import httplib2
import json
from flask import Flask, g, render_template, request, redirect, url_for, flash, jsonify
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, CategoryItems, User
# imports for Google Authentication login
# login_session is a dictionary
from flask import session as login_session
import random, string

# import for Gconnect
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from flask import make_response
import oauth2client, requests, ssl

from functools import wraps

app = Flask(__name__)

CLIENT_ID = json.loads(open('/var/www/catalog/catalog/g_client_secrets.json','r').read())['web']['client_id']
APPLICATION_NAME = "Fun Catalog"

########################### Connect to Databse and Create Session #################################

engine = create_engine('postgresql://postgres:happy123@localhost/catalogdb')
Base.metadata.bind = engine

DBSession = sessionmaker(bind = engine)
session = DBSession() 

###################################### Login Function #############################################

@app.route('/login')
@app.route('/catalog/login')
def showLogin():
	""" Create a state token to prevent request foregry, store it in the session and render login page."""
	state = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in xrange(32))
	login_session['state'] = state
	# return "The current session state is %s" % login_session['state']
	return render_template('login.html', STATE = state)

@app.route('/gconnect', methods = ['POST'])
@app.route('/catalog/gconnect', methods = ['POST'])
def gconnect():
	"""Managees the Google authentication process for login."""

	# Validate state token
	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Obtain authorization code	
	code = request.data

	try:
		# Upgrade the authorization code into a credentials object
		oauth_flow = flow_from_clientsecrets('g_client_secrets.json', scope='')
		oauth_flow.redirect_uri = 'postmessage'
		credentials = oauth_flow.step2_exchange(code)
	except FlowExchangeError:
		response = make_response(json.dumps('Failed to upgrade the authorization code'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Check that the access token is valid
	access_token = credentials.access_token
	url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s' % access_token)

	# Submit request, parse request - Python3 compatible
	h = httplib2.Http()
	result = json.loads(h.request(url, 'GET')[1])

	# If there was an error in the access token info, abort.
	if result.get('error') is not None:
		response = make_response(json.dumps(result.get('error')), 500)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is used for the intended user.
	gplus_id = credentials.id_token['sub']
	if result['user_id'] != gplus_id:
		response = make_response(
	    	json.dumps("Token's user ID doesn't match given user ID."), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Verify that the access token is valid for this app.
	if result['issued_to'] != CLIENT_ID:
		response = make_response(
			json.dumps("Token's client ID does not match app's."), 401)
		print "Token's client ID does not match app's."
		response.headers['Content-Type'] = 'application/json'
		return response

	stored_credentials = login_session.get('credentials')
	stored_gplus_id = login_session.get('gplus_id')
	if stored_credentials is not None and gplus_id == stored_gplus_id:
		response = make_response(json.dumps('Current user is already connected.'), 200)
		response.headers['Content-Type'] = 'application/json'
		return response

	# Store the access token in the session for later use.
	login_session['access_token'] = credentials.access_token
	login_session['gplus_id'] = gplus_id

	# Get user info
	userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
	params = {'access_token': credentials.access_token, 'alt': 'json'}
	answer = requests.get(userinfo_url, params=params)

	data = answer.json()

	login_session['provider'] = 'google'
	login_session['username'] = data['name']
	login_session['picture'] = data['picture']
	login_session['email'] = data['email']

	# Check to see if owner is in own database
	user_id = getUserID(login_session['email'])
	if not user_id:
		user_id = createUser(login_session)
	login_session['user_id'] = user_id

	# create the sccuess login screen
	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']
	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
	flash("you are now logged in as %s" % login_session['username'])
	return output

@app.route('/fbconnect', methods=['POST'])
@app.route('/catalog/fbconnect', methods=['POST'])
def fbconnect():
	"""Managees the Facebook authentication process for login."""

	if request.args.get('state') != login_session['state']:
		response = make_response(json.dumps('Invalid state parameter.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response

	# json.loads will laod a json object into a python dict, json.dumps will dump a python dict to a json object
	data = json.loads(request.data)
	access_token = data['access_token']
	# print "access token received %s " % access_token
	
	app_id = json.loads(open('/var/www/catalog/catalog/fb_client_secrets.json', 'r').read())['web']['app_id']
	app_secret = json.loads(open('var/www/catalog/catalog/fb_client_secrets.json', 'r').read())['web']['app_secret']
	url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (app_id, app_secret, access_token)
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]

	# Use token to get user info from API
	userinfo_url = "https://graph.facebook.com/v2.8/me"
	# strip expire tag from access token
	token = result.split("&")[0]


	url = 'https://graph.facebook.com/v2.8/me?%s&fields=name,id,email' % token
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	# print "url sent for API access:%s"% url
	# print "API JSON result: %s" % result
	data = json.loads(result)
	login_session['provider'] = 'facebook'
	login_session['username'] = data['name']
	login_session['email'] = data['email']
	login_session['facebook_id'] = data['id']

	# The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
	stored_token = token.split("=")[1]
	login_session['access_token'] = stored_token

	# Get user picture
	url = 'https://graph.facebook.com/v2.8/me/picture?%s&redirect=0&height=200&width=200' % token
	h = httplib2.Http()
	result = h.request(url, 'GET')[1]
	data = json.loads(result)

	login_session['picture'] = data['data']['url']

	# see if user exists
	user_id = getUserID(login_session['email'])
	if not user_id:
	    user_id = createUser(login_session)
	login_session['user_id'] = user_id

	output = ''
	output += '<h1>Welcome, '
	output += login_session['username']

	output += '!</h1>'
	output += '<img src="'
	output += login_session['picture']
	output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

	flash("Now logged in as %s" % login_session['username'])
	return output

################################### User Helper Function #########################################

def createUser(login_session):
	"""Adds user to user database and returns their user id"""
	newUser = User(name = login_session['username'], email = login_session['email'], picture = login_session['picture'])
	session.add(newUser)
	session.commit()
	user = session.query(User).filter_by(email = login_session['email']).one()
	return user.id

def getUserInfo(user_id):
	"""Returns user info for user with user_id"""
	if session.query(User).filter_by(id = user_id).one():
		user = session.query(User).filter_by(id = user_id).one()
		return user
	else:
		return "please log in"

def getUserID(email):
	"""Returns user id for user based on email address if user exists."""
	try:
	 	user = session.query(User).filter_by(email = email).one()
		return user.id
	except:
		return None 

def login_required(f):
	"""checks if the user is logged in or not"""
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if 'username' in login_session:
			return f(*args, **kwargs)
		else:
			flash("You need to be logged in first")
			return redirect('/login')
	return decorated_function

####################################### Logout ###################################################

@app.route('/logout')
@app.route('/catalog/logout')
def disconnect():
	""" Disconnect based on provider """
	if 'provider' in login_session:
		if login_session['provider'] == 'google':
			gdisconnect()
			del login_session['gplus_id']
			del login_session['access_token']
		if login_session['provider'] == 'facebook':
			fbdisconnect()
			del login_session['facebook_id']

		del login_session['username']
		del login_session['email']
		del login_session['picture']
		del login_session['user_id']
		del login_session['provider']
		flash("You have sccessfully been logged out")
		return redirect(url_for('categoryShow'))
	else:
		flash("You were not logged in to begin with")
		return redirect(url_for('categoryShow'))

@app.route('/gdisconnect')
@app.route('/catalog/gdisconnect')
def gdisconnect():
	""" Revoke a current Google user's token and reset their login_session """
	access_token = login_session.get('access_token')
    # print 'In gdisconnect access token is %s', access_token
    # print 'User name is: ' 
    # print login_session['username']
	if access_token is None:
 	# print 'Access Token is None'
		response = make_response(json.dumps('Current user not connected.'), 401)
		response.headers['Content-Type'] = 'application/json'
		return response
	url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
	h = httplib2.Http()
	result = h.request(url, 'GET')[0]
	print 'result is '
	print result
	if result['status'] == '200':
	# reset the user's session.
		response = make_response(json.dumps('Failed to revoke token for given user.', 400))
		response.headers['Content-Type'] = 'application/json'
		return response

@app.route('/fbdisconnect')
@app.route('/catalog/fbdisconnect')
def fbdisconnect():
	facebook_id = login_session['facebook_id']
	access_token = login_session['access_token']
	url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
	h = httplib2.Http()
	result = h.request(url, 'DELETE')[1]
	return "You've been logout"

######################################### Routes ################################################

@app.route('/')
@app.route('/catalog')
def categoryShow():
    """showing all categories, the main page"""
    category = session.query(Category).order_by(asc(Category.name))  
    if 'username' in login_session:
    	return render_template('main.html', category = category)
    else:
    	return render_template('publicmain.html', category = category)

# Route for category modification
@app.route('/catalog/new', methods=['GET','POST'])
@login_required
def newCategory():
	"""Page to create a new category."""
	# if 'username' not in login_session:
	# 	return redirect('/login')
	if request.method == 'POST':
		newCat = Category(name = request.form['name'], user_id=login_session['user_id'])
		session.add(newCat)
		session.commit()
		flash("New category %s is added!" % newCat.name)
		return redirect(url_for('categoryShow'))
	else:
		return render_template('newcategory.html')


@app.route('/catalog/<int:category_id>/edit', methods=['GET','POST'])
@login_required
def editCategory(category_id):
	"""Page to edit the category name."""
	editedCategory = session.query(Category).filter_by(id = category_id).one()
	# if 'username' not in login_session:
	# 	return redirect('/login')
	if editedCategory.user_id != login_session['user_id']:
		return "<script>function myFunction() { alert('You are not authrorized to edit this category. Please edit the category which created by yourself. If there is none, you can add a new category to edit.');window.location='/catalog/%s';}</script><body onload='myFunction()''>" % category_id	
	if request.method == 'POST':
		if request.form['name']:
			oldname = editedCategory.name
			editedCategory.name = request.form['name']
			session.add(editedCategory)
			session.commit()
			flash("%s is changed to %s!" % (oldname, editedCategory.name))
			return redirect(url_for('categoryShow'))
	else:
		return render_template('editcategory.html', category_id = category_id, category = editedCategory)

@app.route('/catalog/<int:category_id>/delete', methods=['GET','POST'])
@login_required
def deleteCategory(category_id):
	"""Page to delete a category. Task complete"""
	deletedCategory = session.query(Category).filter_by(id = category_id).one()
	# if 'username' not in login_session:
	# 	return redirect('/login')
	if deletedCategory.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authrorized to delete the category, which is created by other owner.');window.location='/catalog/%s';}</script><body onload='myFunction()''>" % category_id
	if request.method == 'POST':
		session.delete(deletedCategory)
		session.commit()
		flash("Category %s is deleted!" % deletedCategory.name)
		return redirect(url_for('categoryShow'))
	else:
		return render_template('deletecategory.html', category_id = category_id, category = deletedCategory)

# Route for Items modification
@app.route('/catalog/<int:category_id>')
def itemPage(category_id):
	"""Route for category display with its item lists"""
	category = session.query(Category).order_by(asc(Category.name))
	# selectedcategory = session.query(Category).filter_by(id=category_id).one()
	# creator = getUserInfo(selectedcategory.user_id)
	items = session.query(CategoryItems).filter_by(category_id = category_id).all()
	if 'username' in login_session:
		return render_template('itempage.html', category = category, category_id=category_id, items = items) # creator = creator
	else:
		return render_template('publicitempage.html', category = category, category_id = category_id, items = items) # creator = creator

@app.route('/catalog/<int:category_id>/new', methods = ['GET','POST'])
@login_required
def newItem(category_id):
	"""Page to add a new item to the specific category"""
	category = session.query(Category).filter_by(id = category_id).one()
	# if 'username' not in login_session:
	# 	return redirect('/login')
	if category.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authrorized to add a item. Please create your own catalog in order to add.');window.location = '/catalog/%s'}</script><body onload='myFunction()''>"	% category_id
	if request.method == 'POST':
		newItem = CategoryItems(name = request.form['name'], description = request.form['description'],category_id=category_id, user_id=category.user_id)
		session.add(newItem)
		session.commit()
		flash("'%s' is added to %s category!" % (newItem.name, category.name))
		return redirect(url_for('itemPage', category_id = category_id))
	else:
		return render_template('newitem.html', category_id = category_id)

@app.route('/catalog/<int:category_id>/<int:item_id>/edit', methods = ['GET','POST'])
@login_required
def editItem(category_id, item_id):
	""" Edit each item in the category """
	category = session.query(Category).filter_by(id = category_id).one()
	editedItem = session.query(CategoryItems).filter_by(id = item_id).one()
	# if 'username' not in login_session:
	# 	return redirect('/login')
	if category.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authrorized to edit this item. Please create your own catalog in order to edit.');window.location = '/catalog/%s'}</script><body onload='myFunction()''>" % category_id
	if request.method == 'POST':
		if request.form['name']:
			editedItem.name = request.form['name']
		if request.form['description']:
			editedItem.description = request.form['description']
		session.add(editedItem)
		session.commit()
		flash("Item Successfuly Edited!")
		return redirect(url_for('itemPage', category_id = category_id))
	else:
		return render_template('edititem.html', category_id = category_id, item_id = item_id, item = editedItem)

@app.route('/catalog/<int:category_id>/<int:item_id>/delete', methods = ['GET','POST'])
@login_required
def deleteItem(category_id, item_id):
	"""Page to delete a item."""
	category = session.query(Category).filter_by(id=category_id).one()
	deletedItem = session.query(CategoryItems).filter_by(id = item_id).one()
	# if 'username' not in login_session:
	# 	return redirect('/login')
	if category.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authrorized to delete this item. Please create your own catalog in order to delete.');window.location = '/catalog/%s'}</script><body onload='myFunction()''>" % category_id
	if request.method == 'POST':
		session.delete(deletedItem)
		session.commit()
		flash("%s is deleted from category %s!" % (deletedItem.name, category.name))
		return redirect(url_for('itemPage', category_id=category_id))
	else:
		return render_template('deleteitem.html', category_id = category_id, item_id = item_id, item = deletedItem)

@app.route('/catalog/<int:category_id>/<int:item_id>/')
def itemDetail(category_id, item_id):
	""" Showing the item detail page"""
	category = session.query(Category).order_by(asc(Category.name))
	# selectedcategory = session.query(Category).filter_by(id=category_id).one()
	# creator = getUserInfo(selectedcategory.user_id)
	item = session.query(CategoryItems).filter_by(id = item_id).one()
	if 'username' in login_session:
		return render_template('itemdetail.html',category = category, category_id = category_id, item = item) # creator=creator
	return render_template('publicitemdetail.html', category = category, category_id = category_id, item = item) # creator=creator

@app.route('/catalog/<int:category_id>/<int:item_id>/usage/edit', methods=['GET','POST'])
@login_required
def detailEdit(category_id, item_id):
	""" Edit the usage for item detail """
	editedItem = session.query(CategoryItems).filter_by(id = item_id).one()
	# if 'username' not in login_session:
	# 	return redirect('/login')
	if editedItem.user_id != login_session['user_id']:
		return "<script>function myFunction() {alert('You are not authrorized to edit this item. Please create your own catalog in order to edit.');window.location = '/catalog/%s/%s'}</script><body onload='myFunction()''>" % (category_id, item_id)
	if request.method == 'POST':
		if request.form['usage']:
			editedItem.usage = request.form['usage']
		session.add(editedItem)
		session.commit()
		flash("%s's usage has been successfully modified" % editedItem.name)
		return redirect(url_for('itemDetail', category_id = category_id, item_id = item_id))
	else:
		return render_template('editdetail.html', category_id = category_id, item_id = item_id, item = editedItem)


######################################## JASON API ##############################################

# Making a API Endpoint (GET request), JSON APIs to view category information
@app.route('/users/JSON')
@app.route('/catalog/users/JSON')
def userJSON():
	"""Returns JSON for all users in the database."""
	users = session.query(User)
	return jsonify(User=[i.serialize for i in users])

@app.route('/catalog/JSON')
def categoryJSON():
	"""Returns JSON for all category in the database."""
	catalog = session.query(Category)
	return jsonify(Category=[i.serialize for i in catalog])

@app.route('/catalog/<int:category_id>/items/JSON')
def categoryItemsJSON(category_id):
	"""Returns JSON for all items which are belonged to a specific category in the database."""
	category = session.query(Category).filter_by(id = category_id).one()
	items = session.query(CategoryItems).filter_by(category_id = category_id)
	return jsonify(CategoryItems=[i.serialize for i in items])

################################################################################################

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='127.0.0.1', port=8888)





