from google.appengine.ext import ndb

class Player(ndb.Model):
	name = ndb.StringProperty()
	level = ndb.StringProperty()
	clan = ndb.KeyProperty()
	squad = ndb.KeyProperty()
	teams = ndb.

	def update(self):
		pass

	def addTeam(self, teamID, leagueID):
		pass