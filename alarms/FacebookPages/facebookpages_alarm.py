#Setup logging
import logging
log = logging.getLogger(__name__)

#Python Modules
from datetime import datetime

#Local Modules
from ..alarm import Alarm
from ..utils import *

#Exernal Modules
import facebook

class FacebookPages_Alarm(Alarm):

	_defaults = {
		'pokemon':{
			'message': "A wild <pkmn> has appeared! Catch it at <address> <city>. Available until <24h_time> (<time_left>).",
			'link': "<gmaps>",
			'title': "https://raw.githubusercontent.com/brusselopole/Worldopole/master/core/pokemons/<id>.png",
			'name': "<pkmn>"
		},
		'pokestop':{
			'message': "Someone has placed a lure on a Pokestop! Lure will expire at <24h_time> (<time_left>).",
			'link': "<gmaps>",
			'title': "https://raw.githubusercontent.com/brusselopole/Worldopole/master/core/img/pokestop.png",
			'name': "Pokestop Lure"
		},
		'gym':{
			'message':"A Team <old_team> gym has fallen! It is now controlled by <new_team>.",
			'link': "<gmaps>",
			'title':"https://raw.githubusercontent.com/brusselopole/Worldopole/master/core/img/<new_team>.png",
			'name': "Gym Change"
		}
	}

	#Gather settings and create alarm
	def __init__(self, settings):
		#Service Info
		self.page_access_token = settings['page_access_token']
		self.startup_message = settings.get('startup_message', "True")
		self.startup_list = settings.get('startup_list', "True")
				
		#Set Alerts
		self.pokemon = self.set_alert(settings.get('pokemon', {}), self._defaults['pokemon'])
		self.pokestop = self.set_alert(settings.get('pokestop', {}), self._defaults['pokestop'])
		self.gym = self.set_alert(settings.get('gyms', {}), self._defaults['gym'])
		
		#Connect and send startup messages
		self.connect()
		timestamps = get_timestamps(datetime.utcnow());
		if parse_boolean(self.startup_message):
			self.client.put_object("157783561377843", "feed", message="%s - PokeAlarm has intialized!" % timestamps[2])
		log.info("FacebookPages Alarm intialized.")
		
	#Establish connection with FacebookPages
	def connect(self):
		self.client = facebook.GraphAPI(self.page_access_token)
			
	#Set the appropriate settings for each alert
	def set_alert(self, settings, default):
		alert = {}
		alert['message'] = settings.get('message', default['message'])
		alert['link'] = settings.get('link', default['link'])
		alert['title'] = settings.get('title', default['title'])
		alert['name'] = settings.get('name', default['name'])
		return alert
	
	#Post Pokemon Message
	def send_alert(self, alert, info):
		args = {
			"parent_object":"157783561377843",
			"connection_name":"feed",
			"message": replace(alert['message'], info),
			"link": replace(alert['link'], info),
			"name": replace(alert['name'], info),
			"caption":"Valor Boolopole",
			"description":"Click to open google maps and precise location",
			"picture": replace(alert['title'], info)
		}
		
		try_sending(log, self.connect, "FacebookPages", self.client.put_object, args)
		
	#Trigger an alert based on Pokemon info
	def pokemon_alert(self, pokemon_info):
		self.send_alert(self.pokemon, pokemon_info)
	
	#Trigger an alert based on Pokestop info
	def pokestop_alert(self, pokestop_info):
		self.send_alert(self.pokestop, pokestop_info)
		
	#Trigger an alert based on Gym info
	def gym_alert(self, gym_info):
		self.send_alert(self.gym, gym_info)
