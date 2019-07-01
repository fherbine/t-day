'''T-Day App.
Todolist of the day will be useful for the everyday routine.
'''

__author__  = 'fherbine'


from kivy.app import App
from kivy.properties import ObjectProperty


class TDayApp(App):
    screenmanager = ObjectProperty(rebind=True)

    def build(self):
        self.screenmanager = self.root.screenmanager


if __name__ == '__main__':
    TDayApp().run()
