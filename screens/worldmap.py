'''MapScreen

Home screen with meetings location and main UX.
'''

import datetime # Should be temporary to simumlate time

from kivy.animation import Animation
from kivy.app import App
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
    DictProperty,
    ListProperty,
    StringProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen


class MapScreen(Screen):
    mapview = ObjectProperty(allownone=True)

    def on_mapview(self, *args):
        if self.mapview is None:
            return

class WorldMapView(MapView):
    '''Modified version of Kivy Garden MapView.

    map_markers DictProperty :attr: self.map_markers
    {
        1: <MapMarker object>,
        2: <MapMarker object>,
        ...
    {
    '''

    # internal
    add_meeting = BooleanProperty(False)
    marker_triggered = BooleanProperty(False)
    map_markers = DictProperty()
    bounds = ListProperty([0, 0, 0, 0])
    default_zoom = NumericProperty(11)
    max_zoom = NumericProperty(19)
    min_zoom = NumericProperty()
    preview_coordinate = ObjectProperty(allownone=True)
    tmp_map_marker = ObjectProperty(allownone=True)


    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.init_map()

    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.marker_triggered:
            self.add_preview_marker(touch)
            self.add_meeting = True
            self.marker_triggered = False

        return super().on_touch_down(touch)

    def add_preview_marker(self, touch):
        self.preview_coordinate = coordinate = self.get_latlon_at(
            *touch.pos,
            self.zoom,
        )
        self.tmp_map_marker = map_marker = MapMarker(
            lat=coordinate.lat,
            lon=coordinate.lon,
        )
        self.add_marker(map_marker)

    def add_meeting_marker(self, m_id, **kwargs):
        coordinate = kwargs.get('coordinate')

        if not coordinate:
            return

        lat, lon = coordinate['lat'], coordinate['lon']

        map_marker = MapMarker(
            lat=lat,
            lon=lon
        )
        self.add_marker(map_marker)
        self.map_markers[m_id] = map_marker

    def load_markers(self, _, meetings):
        for m_id, meeting in meetings.items():
            if m_id in self.map_markers:
                continue

            self.add_meeting_marker(m_id, **meeting)


    @mainthread
    def init_map(self):
        '''Map initialisation.'''
        #XXX: Hack stuff to set defaultzoom
        self.zoom = self.default_zoom
        self.lat = 48.8534
        self.lon = 2.3488

        app = App.get_running_app()
        meetings_controller = app.meetings_controller
        self.load_markers(None, meetings_controller.meetings)
        meetings_controller.bind(meetings=self.load_markers)

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
    priority_level = NumericProperty(3)
    coordinate = ObjectProperty(allownone=True)
    title = StringProperty()
    comment = StringProperty()
    target = ObjectProperty(allownone=True)
    tmp_marker = ObjectProperty(allownone=True)

    def on_open(self, *args):
        self.pos_hint = {'top': 0}
        open_animation = Animation(pos_hint={'top': 1}, duration=.5)
        open_animation.start(self)

    def add_meeting(self):
        """Add meeting event from meeting popup."""
        app = App.get_running_app()

        meetings_controller = app.meetings_controller
        meetings_controller.add_meeting(
            priority_level=self.priority_level,
            coordinate={
                'lat': self.coordinate.lat,
                'lon': self.coordinate.lon
                } if self.coordinate else None,
            datetime=datetime.datetime.now().isoformat(),
            title=self.title,
            comment=self.comment,
        )

        if self.tmp_marker is not None:
            self.target.remove_marker(self.tmp_marker)

        self.dismiss()


Factory.register('AddMeetingMenu', cls=AddMeetingMenu)

Builder.load_file('screens/worldmap.kv')
