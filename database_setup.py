import os, sys
from sqlalchemy import Column, ForeignKey, Integer, String, Unicode
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship 
# from sqlalchemy_imageattach.entity import Image, image_attachment
from sqlalchemy import create_engine

Base = declarative_base()

class User(Base):

	__tablename__ = 'user'

	id = Column(Integer, primary_key=True)
	name = Column(String(250), nullable=False)
	email = Column(String(250), nullable=False)
	picture = Column(String(250))

	@property
	def serialize(self):
		"""return object data in easily serializable format"""
		return {
			'id':self.id,
			'name': self.name,
			'email': self.email,
			'picture': self.picture,
		}

class Category(Base):

	__tablename__ = 'category'

	id = Column(Integer, primary_key = True)
	name = Column(String(250), nullable = False)
	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)


	@property
	def serialize(self):
		"""return object data in easily serializable format"""
		return {
			'id':self.id,
			'name': self.name,
		}

class CategoryItems(Base):

	__tablename__ = 'category_item'

	id = Column(Integer,primary_key = True)
	name = Column(String(50), nullable = False)
	description = Column(String(120))
	usage = Column(String(1000))

	category_id = Column(Integer, ForeignKey('category.id'))
	category = relationship(Category)

	user_id = Column(Integer, ForeignKey('user.id'))
	user = relationship(User)

	@property
	def serialize(self):
		"""return object data in easily serializable format"""
		return {
			'id': self.id,
			'name': self.name,
			'description': self.description,
			'usage': self.usage,
		}

####  insert at the end of file ####

engine = create_engine('sqlite:///catalogitems.db')

Base.metadata.create_all(engine)
 