from datetime import datetime

# Global settings - update at beginning of each semester
NUM_TEAMS = 25
ORG_NAME = 'csucs314f20'
REQUEST_TIMEOUT = 30
SPRINT_DATES = {
    1: (datetime.strptime('2020-09-02 00:00:00', '%Y-%m-%d %H:%M:%S'),
        datetime.strptime('2020-09-10 22:00:00', '%Y-%m-%d %H:%M:%S')),
    2: (datetime.strptime('2020-09-15 00:00:00', '%Y-%m-%d %H:%M:%S'),
        datetime.strptime('2020-10-01 22:00:00', '%Y-%m-%d %H:%M:%S')),
    3: (datetime.strptime('2020-03-04 00:00:00', '%Y-%m-%d %H:%M:%S'),
        datetime.strptime('2020-03-26 22:00:00', '%Y-%m-%d %H:%M:%S')),
    4: (datetime.strptime('2020-04-01 00:00:00', '%Y-%m-%d %H:%M:%S'),
        datetime.strptime('2020-04-16 22:00:00', '%Y-%m-%d %H:%M:%S')),
    5: (datetime.strptime('2020-04-22 00:00:00', '%Y-%m-%d %H:%M:%S'),
        datetime.strptime('2020-05-07 22:00:00', '%Y-%m-%d %H:%M:%S'))
}

# API grading
HOST = 'black-bottle.cs.colostate.edu'
REQUEST_DEFINITIONS = {
    'config': {
        'name': 'config',
        'url': '/api/config',
        'request_type': 'get'
    },
    'distance': {
        'name': 'distance',
        'url': '/api/distance',
        'request_type': 'post'
    },
    'itinerary': {
        'name': 'itinerary',
        'url': '/api/itinerary',
        'request_type': 'post'
    },
    'find': {
        'name': 'find',
        'url': '/api/find',
        'request_type': 'post'
    }
}

# Travis

# Code Climate


def get_sprint_dates(sprint_num=None):
    if sprint_num:
        return SPRINT_DATES[sprint_num]
    now = datetime.now()
    for k in SPRINT_DATES:
        start, end = SPRINT_DATES[k]
        if start <= now <= end:
            return (start, end)
    return None, None
