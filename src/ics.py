# a really simple ICS file parser to avoid large dependencies
# such libraries are overweight for this project because we only 
# need to read these calendars
class ICSCalendar:
    def __init__(self, raw):
        self.lines = raw.splitlines()
        hdr = self.lines.pop(0).split(':')
        if hdr[0] != 'BEGIN': raise Exception('Invalid header')
        self.data=self._parse_obj(hdr[1])

    def _parse_obj(self, tp: str):
        data = {'@type': tp}
        while self.lines:
            parts = self.lines.pop(0).split(':')
            key = parts[0]
            value = ":".join(parts[1:])
            if key == 'END':
                return data
            if key == 'BEGIN':
                if value not in data:
                    data[value] = []
                data[value].append(self._parse_obj(value))
            else:
                data[key] = value
