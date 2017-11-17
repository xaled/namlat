class Report:
    def __init__(self, module, uri, type, period, entries, title="{PERIODLY} report of {MODULE}", subtitle="" ):
        self.__dict__ = dict()
        self.__dict__['module'] = module
        self.__dict__['uri'] = uri
        self.__dict__['type'] = type
        self.__dict__['period'] = period
        self.__dict__['title'] = title
        self.__dict__['subtitle'] = subtitle
        self.__dict__['entries'] = list()
        for entry in entries:
            self.__dict__['entries'].append(entry.__dict__)


class Entry:
    def __init__(self, title, message_body, anchor, id=None):
        self.__dict__ = dict()
        self.__dict__['title'] = title
        self.__dict__['message_body'] = message_body
        self.__dict__['anchor'] = anchor
        self.__dict__['id'] = id


def report(data, address, report):
    data['new_reports'][address].append(report.__dict__)
