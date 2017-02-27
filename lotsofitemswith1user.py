from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, CategoryItems, User

engine = create_engine('sqlite:///catalogitemswith1user.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Items for Category1 - Soccer
category1 = Category(user_id=1, name="Soccer")

session.add(category1)
session.commit()

catItem1 = CategoryItems(user_id=1, name="Ball", description="black and white, smaller than basketball", usage="please write usage here", category=category1)

session.add(catItem1)
session.commit()

catItem2 = CategoryItems(user_id=1, name="Sock", description="beautiful and long, very important for comfortablly running on grass", usage="please write usage here", category=category1)

session.add(catItem2)
session.commit()

catItem3 = CategoryItems(user_id=1, name="Shoes", description="specialized design with rivets for running on grass", usage="please write usage here", category=category1)

session.add(catItem3)
session.commit()

# Items for Category2 - Basketball

category2 = Category(user_id=1, name="Basketball")

session.add(category2)
session.commit()

catItem1 = CategoryItems(user_id=1, name="Ball", description="orange color with grips for better handling", usage="please write usage here", category=category2)

session.add(catItem1)
session.commit()

catItem2 = CategoryItems(user_id=1, name="Sock", description="comfort and fit for better cushion and feeling", usage="please write usage here", category=category2)

session.add(catItem2)
session.commit()

catItem3 = CategoryItems(user_id=1, name="Shoes", description="specialized design for make movement on different floor, such as jump or stop", usage="please write usage here", category=category2)

session.add(catItem3)
session.commit()

# Items for Category3 - Snowboarding
category3 = Category(user_id=1, name="Snowboarding")

session.add(category3)
session.commit()

catItem1 = CategoryItems(user_id=1, name="Board", description="different demension, shape and material matters", usage="please write usage here", category=category3)

session.add(catItem1)
session.commit()

catItem2 = CategoryItems(user_id=1, name="Boots", description="Fit and comfort is the key point to choose from, not the external appearance", usage="please write usage here", category=category3)

session.add(catItem2)
session.commit()

catItem3 = CategoryItems(user_id=1, name="Goggle", description="Viewing better and looking better and some functions like UV protection", usage="please write usage here", category=category3)

session.add(catItem3)
session.commit()

# Items for Category4 - Rock Climbing
category4 = Category(user_id=1, name="Rock Climbing")

session.add(category4)
session.commit()

catItem1 = CategoryItems(user_id=1, name="Harness", description="bucket it correctly and tightly with trainer for new climber", usage="please write usage here", category=category4)

session.add(catItem1)
session.commit()

catItem2 = CategoryItems(user_id=1, name="Rope", description="various way to climbing, and always take a company with you", usage="please write usage here", category=category4)

session.add(catItem2)
session.commit()

catItem3 = CategoryItems(user_id=1, name="Shoes", description="some people prefer not wearing shoes, but I bet you should", usage="please write usage here", category=category4)

session.add(catItem3)
session.commit()

# Items for Category5 - Swimming
category5 = Category(user_id=1, name="Swimming")

session.add(category5)
session.commit()

catItem1 = CategoryItems(user_id=1, name="Suits", description="buy with Hi-Tech suits if you can afford, but it's only worth for professional swimmers", usage="please write usage here", category=category5)

session.add(catItem1)
session.commit()

catItem2 = CategoryItems(user_id=1, name="Goggle", description="viewing nicely underwater, another new scene of the world", usage="please write usage here", category=category5)

session.add(catItem2)
session.commit()

catItem3 = CategoryItems(user_id=1, name="Earplug", description="It's my must have item, but maybe it's not yours unless you have some ear problem", usage="please write usage here", category=category5)

session.add(catItem3)
session.commit()

print "added menu items!"