'''T-Day App.
Todolist of the day will be useful for the everyday routine.
'''

__author__  = 'fherbine'


from kivy.app import App
from kivy.clock import Clock
from kivy.properties import (
    NumericProperty,
    ObjectProperty,
)

import config

from screens import * # noqa
from controllers.meetings import Meetings


class TDayApp(App):
    meetings_controller = ObjectProperty(rebind=True)
    screenmanager = ObjectProperty(rebind=True)
    time = NumericProperty()

    def build(self):
        self.screenmanager = self.root.screenmanager
        self.meetings_controller = meetings = Meetings()
        meetings.load_meetings()
        Clock.schedule_interval(self.update_time, 0)

    def update_time(self, dt):
        self.time += dt

    def on_meetings_controller(self, *_):
        pass


if __name__ == '__main__':
    TDayApp().run()
