'''MapScreen

Home screen with meetings location and main UX.
'''


from kivy.clock import mainthread
from kivy.garden.mapview import (
    MapSource,
    MapView,
)
from kivy.lang import Builder
from kivy.properties import (
    ListProperty,
    NumericProperty,
)
from kivy.uix.screenmanager import Screen


class MapScreen(Screen):
    pass

class WorldMapView(MapView):
    '''Modified version of Kivy Garden MapView.'''

    default_zoom = NumericProperty(11)
    min_zoom = NumericProperty()
    max_zoom = NumericProperty(19)
    bounds = ListProperty([0, 0, 0, 0])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.init_map()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos):
            # add marker ?
            pass
        return super().on_touch_down(touch)

    @mainthread
    def init_map(self):
        #XXX: Hack stuff to set defaultzoom
        self.zoom = self.default_zoom
        self.lat = 48.8534
        self.lon = 2.3488
        #self.map_source.bounds = self.bounds

    def on_default_zoom(self, *args):
        '''Update map's default zoom.'''

        self.zoom = self.default_zoom

    def on_min_zoom(self, *args):
        '''Update map's minimum zoom.'''
        if not self.map_source:
            return

        self.update_map_source()

    def on_max_zoom(self, max_zoom):
        '''Update map's maximum zoom.'''
        if not self.map_source:
            return

        self.update_map_source()

    def update_map_source(self):
        '''Update Map map_source object, min/max zooms.'''
        source = MapSource(max_zoom=self.max_zoom, min_zoom=self.min_zoom)
        self.map_source = source


Builder.load_file('screens/worldmap.kv')
