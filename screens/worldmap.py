'''MapScreen

Home screen with meetings location and main UX.
'''


from kivy.animation import Animation
from kivy.clock import mainthread
from kivy.factory import Factory
from kivy.garden.mapview import (
    MapMarker,
    MapSource,
    MapView,
)
from kivy.lang import Builder
from kivy.properties import (
    BooleanProperty,
    ListProperty,
    NumericProperty,
)
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen


class MapScreen(Screen):
    pass

class WorldMapView(MapView):
    '''Modified version of Kivy Garden MapView.

    Meetings ListProperty :attr: self.meetings
    [{
        'coordinate': {'lat': x, 'lon': y},
        'datetime': 'ISOFORMAT_DATETIME',
        'level': 1-3
    }]

    map_markers ListProperty :attr: self.map_markers
    [
        <MapMarker object>,
        <MapMarker object>,
        ...
    ]
    '''

    # internal
    add_meeting = BooleanProperty(False)
    marker_triggered = BooleanProperty(False)
    bounds = ListProperty([0, 0, 0, 0])
    map_markers = ListProperty()
    default_zoom = NumericProperty(11)
    max_zoom = NumericProperty(19)
    min_zoom = NumericProperty()

    # external
    meetings = ListProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.init_map()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.marker_triggered:
            self.add_meeting_marker(touch)
            self.add_meeting = True
            self.marker_triggered = False

        return super().on_touch_down(touch)

    def add_meeting_marker(self, touch):
        coordinate = self.get_latlon_at(*touch.pos, self.zoom)
        map_marker = MapMarker(lat=coordinate.lat, lon=coordinate.lon)
        self.add_marker(map_marker)

    @mainthread
    def init_map(self):
        '''Map initialisation.'''
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

class AddMeetingMenu(ModalView):
    def open(self, *args, **kwargs):
        super().open(animation=False, *args, **kwargs)

    def on_open(self, *args):
        self.pos_hint = {'top': 0}
        open_animation = Animation(pos_hint={'top': 1}, duration=.5)
        open_animation.start(self)



Factory.register('AddMeetingMenu', cls=AddMeetingMenu)

Builder.load_file('screens/worldmap.kv')
