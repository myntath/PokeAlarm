# Standard Library Imports
from datetime import datetime
import logging
# 3rd Party Imports
import facebook
# Local Imports
from ..Alarm import Alarm
from ..Utils import parse_boolean, get_time_as_str, reject_leftover_parameters, require_and_remove_key

log = logging.getLogger(__name__)
try_sending = Alarm.try_sending
replace = Alarm.replace


#####################################################  ATTENTION!  #####################################################
# You DO NOT NEED to edit this file to customize messages for services! Please see the Wiki on the correct way to
# customize services In fact, doing so will likely NOT work correctly with many features included in PokeAlarm.
#                               PLEASE ONLY EDIT IF YOU KNOW WHAT YOU ARE DOING!
#####################################################  ATTENTION!  #####################################################


class FacebookPageAlarm(Alarm):

    _defaults = {
        'pokemon': {
            'message': "A wild <pkmn> has appeared! Catch it at <address> <city>. Available until <24h_time> (<time_left>).",          
            'link': "<gmaps>",                                                                                                         
            'title': "https://raw.githubusercontent.com/brusselopole/Worldopole/master/core/pokemons/<id>.png",                        
            'name': "<pkmn>"
        },
        'pokestop': {
            'message': "Someone has placed a lure on a Pokestop! Lure will expire at <24h_time> (<time_left>).",                       
            'link': "<gmaps>",                                                                                                         
            'title': "https://raw.githubusercontent.com/brusselopole/Worldopole/master/core/img/pokestop.png",                         
            'name': "Pokestop Lure"
        },
        'gym': {
            'message':"A Team <old_team> gym has fallen! It is now controlled by <new_team>.",                                         
            'link': "<gmaps>",                                                                                                         
            'title':"https://raw.githubusercontent.com/brusselopole/Worldopole/master/core/img/<new_team>.png",                        
            'name': "Gym Change"
        }
    }

    # Gather settings and create alarm
    def __init__(self, settings):
        # Required Parameters
        self.__page_access_token = require_and_remove_key('page_access_token', settings, "'FacebookPage' type alarms.")
        self.__client = None

        # Optional Alarm Parameters
        self.__startup_message = parse_boolean(settings.pop('startup_message', "True"))

        # Set Alerts
        self.__pokemon = self.create_alert_settings(settings.pop('pokemon', {}), self._defaults['pokemon'])
        self.__pokestop = self.create_alert_settings(settings.pop('pokestop', {}), self._defaults['pokestop'])
        self.__gym = self.create_alert_settings(settings.pop('gym', {}), self._defaults['gym'])

        #  Warn user about leftover parameters
        reject_leftover_parameters(settings, "'Alarm level in FacebookPage alarm.")

        log.info("FacebookPage Alarm has been created!")

    # Establish connection with FacebookPage
    def connect(self):
        self.__client = facebook.GraphAPI(self.__page_access_token)

    # Sends a start up message on Telegram
    def startup_message(self):
        if self.__startup_message:
            timestamps = get_time_as_str(datetime.utcnow())
            self.post_to_wall("{} - PokeAlarm has intialized!".format(timestamps[2]))
            log.info("Startup message sent!")

    # Set the appropriate settings for each alert
    def create_alert_settings(self, settings, default):
        alert = {
            'message': settings.get('message', default['message']),
            'link': settings.get('link', default['link']),
            'title': settings.get('title', default['title']),
            'name': settings.get('name', default['name'])
        }
        reject_leftover_parameters(settings, "'Alert level in FacebookPage alarm.")
        return alert

    # Post Pokemon Message
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

        try_sending(log, self.connect, "FacebookPage", self.__client.put_object, args)
        #try_sending(log, self.connect, "FacebookPage", self.post_to_wall, args)

    # Trigger an alert based on Pokemon info
    def pokemon_alert(self, pokemon_info):
        self.send_alert(self.__pokemon, pokemon_info)

    # Trigger an alert based on Pokestop info
    def pokestop_alert(self, pokestop_info):
        self.send_alert(self.__pokestop, pokestop_info)

    # Trigger an alert based on Gym info
    def gym_alert(self, gym_info):
        self.send_alert(self.__gym, gym_info)

    # Temporrary TODO
    def send_text(self, text):
        pass

    # Sends a wall post to Facebook
    def post_to_wall(self, message, attachment=None):
        args = {"message": message}
        if attachment is not None:
            args['attachment'] = attachment
            self.__client.put_wall_post(message=message)
        try_sending(log, self.connect, "FacebookPage", self.__client.put_wall_post, args)
