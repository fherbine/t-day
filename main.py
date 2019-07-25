'''T-Day App.
Todolist of the day will be useful for the everyday routine.
'''

__author__  = 'fherbine'


import json

from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (
    DictProperty,
    NumericProperty,
    ObjectProperty,
    StringProperty,
)

from kivy.core.window import Window
Window.softinput_mode = 'below_target'  # noqa

import config

from screens import * # noqa
from controllers.meetings import Meetings


class TDayApp(App):
    language = StringProperty()
    screenmanager = ObjectProperty(rebind=True)
    settings = DictProperty()
    meetings_controller = ObjectProperty(rebind=True)
    time = NumericProperty()

    def build(self):
        self._load_settings()

        self.screenmanager = self.root.screenmanager
        self.meetings_controller = meetings = Meetings()
        meetings.load_meetings()
        Clock.schedule_interval(self._update_time, 0)

    def _load_settings(self):
        with open('settings.json') as settings_file:
            self.settings = settings = json.load(settings_file)

        self.language = settings.get('language', 'en_US')

    def _update_time(self, dt):
        self.time += dt

    def on_meetings_controller(self, *_):
        pass


if __name__ == '__main__':
    TDayApp().run()
