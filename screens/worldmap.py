'''MapScreen

Home screen with meetings location and main UX.
'''


from kivy.lang import Builder
from kivy.uix.screenmanager import Screen


class MapScreen(Screen):
    pass


Builder.load_file('screens/worldmap.kv')
