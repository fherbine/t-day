import json

from kivy.event import EventDispatcher
from kivy.logger import Logger
from kivy.properties import DictProperty

class Meetings(EventDispatcher):
    '''Meetings controller/handler.

    Meetings ListProperty :attr: self.meetings
    { m_id(str): {
        'coordinate': {'lat': x, 'lon': y},
        'level': 1-3,
        'data': {
            'comment': '...',
            'datetime': 'ISOFORMAT_DATETIME',
            'title': '...',
        },
    }, ...}
    '''

    meetings = DictProperty()

    def add_meeting(self, priority_level=3, coordinate=None, **kwargs):
        '''Add new meeting to calendar.

        It takes as arguments:

        :priority_level: from 1 to 3 it is relevant of the importance of
        the event. The default is 3.
        :coordinate: Wich is not mandatory, default to `None`. Its the
        Coordinate object of kivy.garden.mapview of the event marker if it
        exists.
        :kwargs: could take:
        :datetime: Should be the iso-format datetime of the event.
        :title: Title of the event.
        :comment: A short description of the event.
        '''
        m_id = len(self.meetings)
        meeting = {
            'priority_level': priority_level,
            'coordinate': coordinate,
            'data': kwargs,
        }
        self.meetings[str(m_id)] = meeting

        Logger.info('Meetings - added: ' + repr(meeting) + 'with id: ' + m_id)

        self.save_meetings()

    def save_meetings(self):
        '''Writing meetings property into a meetings.json file.'''
        with open('meetings.json', 'w+') as meetings_file:
            json.dump(self.meetings, meetings_file)

        Logger.info('Meetings - saved: ' + repr(self.meetings))

    def load_meetings(self):
        '''Reading into meetings.json file to parse it into meetings prop.'''
        with open('meetings.json', 'r') as meetings_file:
            self.meetings = json.load(meetings_file)

        Logger.info('Meetings - loaded: ' + repr(self.meetings))
