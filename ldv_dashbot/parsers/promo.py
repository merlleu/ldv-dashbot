import re
import hashlib
import json

class PromotionParser:
    def __init__(self, soup):
        self._soup = soup
        self.events = []
        self.event_selector = None

    def parse(self):
        self._get_event_selector()
        self._parse_events()

    # select all the a tags with the class promo_chg_filter_evt
    # get the parent <li> tag and if it has the class "active" then
    # set the event_selector to the value of the data-id attribute
    def _get_event_selector(self):
        for a in self._soup.select('a.promo_chg_filter_evt'):
            li = a.parent
            if 'active' in li['class']:
                self.event_selector = a['data-id']
                break

    # select all <div> tags within the <div> with id "promo_content"
    # that have the clas "media"
    # call _parse_event for each of these
    def _parse_events(self):
        for div in self._soup.select('#promo_content div.media'):
            self.events.append(
                self._parse_event(div))

    #
    def _parse_event(self, div):
        d = {
            'title': self._parse_event_title(div),
            'type': self._parse_event_type(div),
            'id': self._get_event_id(div),
            'description': self._get_event_description(div),
            'audience': self._parse_event_audience(div),
            'labels': self._parse_event_labels(div),
            **self._parse_event_thumbnails(div)
        }

        d['hash'] = PromotionParser._get_event_hash(d)

        return d

    def _get_event_hash(d):
        j = json.dumps([
            d['title'],
            d['description'], 
            d['meta']['calendar'], 
            d['meta']['time'], 
            d['meta']['map']
        ])
        return hashlib.md5(j.encode('utf-8')).hexdigest()

    # select the <h4> tag within div with class "media-heading"
    def _parse_event_title(self, div):
        h4 = div.select('h4.media-heading')[0]
        return h4.text.strip()

    # select the <span> tag with the class "label-warning" within the <div> tag
    def _parse_event_type(self, div):
        span = div.select('p.pull-right span.label')[-1]
        return span.text.strip()

    # select the <div> tags within div with class "caption"
    def _parse_event_thumbnails(self, div):
        divs = div.select('div.caption')
        meta = self._parse_event_metadata(divs[0])
        regs = self._parse_event_registrations(divs[1])

        return {
            'meta': meta,
            'registrations': regs
        }

    # select each <tr> tag with the <div> tag
    # the data_type is the class of the <i> tag within the first <td> tag inside the <tr>
    # the data_value is the text of the second <td> tag inside the <tr>
    def _parse_event_metadata(self, div):
        meta = {}
        for tr in div.select('tr'):
            tds = tr.select('td')
            for i in range(0, len(tds), 2):
                data_type = tds[i].select('i')[0]['class'][0].split('-')[1]
                data_value = tds[i+1].text.strip()
                meta[data_type] = self._cleanup_str(data_value)
        
        return meta

    # returns a dict with the following keys: students, experts, managers
    # the value of each key is a dict with the following keys: total, registered, remaining
    # the value of each of these keys is an int
    # we have to parse the html table in form of:
    # | Organisation            | Inscrits               | Places restantes      |
    # |-------------------------|------------------------|-----------------------|
    # | {total} étudiants       | Total : {registered}   | Total : {remaining}   |
    # | dont {total} experts    | Expert : {registered}  | Expert : {remaining}  |
    # | dont {total} managers   | Manager : {registered} | Manager : {remaining} |
    def _parse_event_registrations(self, div):
        registrations = {
            k: {'total': 0, 'registered': 0, 'remaining': 0}
            for k in ['students', 'experts', 'managers']
        }

        tds = div.select('td')

        for td in tds:
            col = {
                'Organisation': 'total',
                'Inscrits': 'registered',
                'Places restantes': 'remaining'
            }[td.select('div.header')[0].text.strip()]
            if col == 'total':
                continue

            # for each node in the td tree, if it is a string then append it to the r list
            for node in td.contents:
                if isinstance(node, str) and node != '\n':
                    s = self._cleanup_str(node).replace('\n', '')
                    k, v = s.split(" : ")
                    registrations[
                        {
                            'Total': 'students',
                            'Expert': 'experts',
                            'Manager': 'managers'
                        }[k]
                    ][col] = int(v)

        # calculate the total number of students
        for k in registrations:
            registrations[k]['total'] = (
                registrations[k]['registered'] + registrations[k]['remaining'])

        return registrations

    # get the span tag with the class "promo-student-demande" and return the data-id attribute
    def _get_event_id(self, div):
        q = div.select('span.promo-student-demande')
        return q[0]['data-id'] if len(q) > 0 else None
    
    # get the div with class alert-info and return the text
    def _get_event_description(self, div):
        d = div.select('div.alert-info')
        return self._cleanup_str(d[0].text.strip()) if d else None
    
    def _parse_event_audience(self, div):
        audience = []
        for span in div.select('div.thumbnail div.thumbnail'):
            if 'Public' in span.text:
                for a in span.select('span.badge-info'):
                    audience.append(a.text.strip())
        return audience
    
    def _parse_event_labels(self, div):
        labels = []
        for span in div.select('div.thumbnail span.label-warning'):
            labels.append(span.text.strip())
        return labels

    # It seems that some fields does not support line breaks
    # so we replace large chunks of whitespace with line breaks
    def _cleanup_str(self, s: str):
        return re.sub(r'\s{2,}', '\n', s)
