'''MapScreen

Home screen with meetings location and main UX.
'''

import datetime # Should be temporary to simumlate time

from plyer import gps

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
from kivy.logger import Logger
from kivy.properties import (
    BooleanProperty,
    DictProperty,
    ListProperty,
    StringProperty,
    NumericProperty,
    ObjectProperty,
)
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.modalview import ModalView
from kivy.utils import platform
from kivy.uix.screenmanager import Screen


class MapScreen(Screen):
    mapview = ObjectProperty(allownone=True)

    def on_mapview(self, *args):
        mapview = self.mapview

        if mapview is None:
            return

        mapview.init_gps()

    def on_leave(self, *args):
        mapview = self.mapview

        if mapview is None:
            return

        mapview.stop_gps()


class EventMarker(MapMarker):
    m_id = StringProperty()

    def on_release(self, *args):
        if not self.m_id:
            return

        popup = EventInfoPopup()
        popup.m_id = self.m_id
        popup.open()

class EventItemBox(BoxLayout):
    pass

class EventInfoPopup(ModalView):
    m_id = StringProperty()
    container = ObjectProperty()

    def on_m_id(self, *args):
        if not self.m_id:
            return

        app = App.get_running_app()
        meetings_controller = app.meetings_controller
        meetings = meetings_controller.meetings

        meeting = meetings[self.m_id]

        data = {
            **meeting.get('data', {}),
            'priority_level': meeting.get('priority_level'),
        }

        for key, value in data.items():
            item = EventItemBox()
            item.title = str(key)
            item.content = str(value)

            self.container.add_widget(item)



class WorldMapView(MapView):
    '''Modified version of Kivy Garden MapView.

    map_markers DictProperty :attr: self.map_markers
    {
        1: <EventMarker object>,
        2: <EventMarker object>,
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
    location_marker = ObjectProperty(allownone=True)


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
        self.tmp_map_marker = map_marker = EventMarker(
            lat=coordinate.lat,
            lon=coordinate.lon,
        )
        self.add_marker(map_marker)

    def add_meeting_marker(self, m_id, **kwargs):
        coordinate = kwargs.get('coordinate')

        if not coordinate:
            return

        lat, lon = coordinate['lat'], coordinate['lon']

        map_marker = EventMarker(
            lat=lat,
            lon=lon
        )
        map_marker.m_id = m_id
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

    def init_gps(self):
        try:
            gps.configure(
                on_location=self.update_location,
                on_status=self.on_gps_status,
            )
            self._start_gps(1000, 0)
        except NotImplementedError:
            Logger.info('GPS: Unavailable on {platform}'.format(
                platform=platform,
            ))

    def _start_gps(self, min_time, min_distance):
        gps.start(min_time, min_distance)

    def stop_gps(self):
        gps.stop()

    @mainthread
    def update_location(self, **kwargs):
        for coordinate in ('lat', 'lon'):
            setattr(self, coordinate, kwargs.get(coordinate, 0.0))

        self.place_location_marker()

    def place_location_marker(self):
        if self.location_marker is None:
            self.location_marker = LocationMarker()
        else:
            self.remove_marker(self.location_marker)

        self.location_marker.lat, self.location_marker.lon = self.lat, self.lon
        self.add_marker(self.location_marker)

    @mainthread
    def on_gps_status(self, stype, status):
        Logger.info('GPS: type={stype}\n{status}'.format(
            stype=stype,
            status=status,
        ))

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
    coordinate = ObjectProperty(allownone=True)
    target = ObjectProperty(allownone=True)
    tmp_marker = ObjectProperty(allownone=True)

    def on_open(self, *args):
        self.pos_hint = {'x': 1}
        open_animation = Animation(pos_hint={'x': 0}, duration=.5)
        open_animation.start(self)

    def add_meeting(self):
        """Add meeting event from meeting popup."""
        app = App.get_running_app()

        meetings_controller = app.meetings_controller

        data_container = self.ids.data_container
        data = data_container.children
        title = data[1].text
        comment = data[0].text
        level = int(data[-1].spinner_option if data[-1].spinner_option else '0')

        meetings_controller.add_meeting(
            priority_level=level,
            coordinate={
                'lat': self.coordinate.lat,
                'lon': self.coordinate.lon
                } if self.coordinate else None,
            datetime=datetime.datetime.now().isoformat(),
            title=title,
            comment=comment,
        )

        if self.tmp_marker is not None:
            self.target.remove_marker(self.tmp_marker)

        self.dismiss()

class LocationMarker(MapMarker, FloatLayout):
    pass


Factory.register('AddMeetingMenu', cls=AddMeetingMenu)

Builder.load_file('screens/worldmap.kv')
