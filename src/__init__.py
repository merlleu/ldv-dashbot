import requests
from .constants import *
from .types import *
from .errors import *
from .months import *
import pickle, os, logging
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


class BotConfig: 
    email = ''
    password = ''
    cookies_cache = None


class Bot:
    def __init__(self, email, password, **kwargs):
        self.config = BotConfig()
        self.config.email = email
        self.config.password = password
        self.config.cookies_cache = kwargs.get('cookies_cache')

        self.client = requests.Session()
        self.client.headers.update({'User-Agent': USER_AGENT})

        self.login(True)

    def login(self, cold=False):
        # load cookies
        if cold and self.config.cookies_cache and os.path.exists(self.config.cookies_cache):
            with open(self.config.cookies_cache, 'rb') as f:
                logging.info("Loaded cookies cache !")
                self.client.cookies = pickle.load(f)
        
        # first of all we attempt a redirect to the login page
        r = self.client.get(LDVNET_URL)

        if self.parse_raw_homepage(r.text):
            logging.info("Logged-in from cache !")
            return
        else:
            logging.info("Logged-in from cache !")

        next_link = self.client.post(AJAX_URL, data = {
            'act': 'ident_analyse',
            'login': self.config.email
        }).text

        # if the ajax doesn't redirect the email is not good !
        if 'location' not in next_link:
            raise InvalidCredentials("Invalid Email !")
        next_link = next_link.split('"')[1].split('"')[0]

        r = self.client.get(LDVNET_URL + next_link)
        if r.status_code != 200:
            raise AuthError(str(r))

        soup = BeautifulSoup(r.text, 'html.parser')

        # we get the next link (with a client-request-id set in the query params !)
        next_link = 'https://adfs.devinci.fr' + soup.find(id = 'loginForm').get('action')
        
        # next step is to make a post request to the `next_link` url with user credentials
        r = self.client.post(next_link, data={
            'UserName': self.config.email,
            'Password': self.config.password,
            'AuthMethod': 'FormsAuthentication'
        })
        if r.status_code != 200:
            raise AuthError(str(r))

        # at this step the server returns an html doc containing a form with callback data
        soup = BeautifulSoup(r.text, 'html.parser')
        form = soup.find_all('form')[0]
        reqdata = {}
        for i in form.contents:
            if i.name == 'input':
                reqdata[i.get('name')] = i.get('value')

        # if action is relative path, this means the password is invalid !
        if form.get('action').startswith('/'):
            raise InvalidCredentials("Wrong password !")
        
        r = self.client.post(form.get('action'), data = reqdata)

        # we should now have access to the dashboard !
        self.parse_raw_homepage(r.text)

        # save cookies to cache
        if self.config.cookies_cache:
            with open(self.config.cookies_cache, 'wb') as f:
                pickle.dump(self.client.cookies, f)

    def parse_raw_homepage(self, raw):
        soup = BeautifulSoup(raw, 'html.parser')
        addr = soup.find_all('address')
        if not addr:
            return False
        addr = addr[0]
        user = User()
        for n, c in enumerate(addr.contents):
            if c.name == 'div':
                _, user.first_name, user.last_name, _ = c.contents[0].split(' ')
            if c.name == 'b':
                key = c.contents[0]
                if key == "Identifiant":
                    user.id = addr.contents[n+1].split(' ')[-1]
                elif key == "Numéro de badge":
                    user.badge_number = addr.contents[n+1].split(' ')[-1]
                elif key == "Numéro client":
                    user.client_number = addr.contents[n+1].split(' ')[-1]
                elif key == "Id. Administratif":
                    user.admin_id = addr.contents[n+2].contents[0].split(' ')[-1]
        self.user = user
        return True

    def request_html(self, method, url, **kwargs):
        r = self.client.request(method, url, **kwargs, allow_redirects=False)
        if r.status_code != 200:
            raise UnsuccessfullResponse(r)
        
        soup = BeautifulSoup(r.content.decode('utf-8'), 'html.parser')
        if soup.find('btn_connect') is not None:
            self.login(False)
            return self.request(method, url, **kwargs)
        else:
            return soup

    def get_grades(self):
        soup = self.request_html("GET", MARKS_URI)
        # with open("src/marks.html") as f:
        #     soup = BeautifulSoup(f.read(), 'html.parser')
        notes = soup.find(class_ = 'notes')

        semesters = []
        
        for i in notes.contents[1].contents:
            if i.name == 'ol':
                # parse semester
                c = i.contents[1].contents
                semester = Semester(semester = int(c[1].contents[2].strip().split(' ')[-1]), units = [])
                
                # parse semester units
                for k in range(3, len(c), 2):
                    u = c[k].contents[1].contents
                    unit = SemesterUnit(name = _clean_string(u[1].contents[2]), subjects = [])
                    
                    for i in u[3].contents:
                        if i.name == 'li':
                            name = _clean_string(i.contents[1].contents[2]).split(" ")

                            # parse subject !
                            subject = GradesSubject(
                                id = name[0],
                                name = " ".join(name[1:]),
                                grades = [],
                            )

                            # parse subject final grades
                            # those are set only once all grades are set.
                            if len(i.contents[1].contents[3].contents) > 2:
                                a = i.contents[1].contents[3].find('a')
                                if a:
                                    subject.evaluation_link = a.get('href')
                                else:
                                    subject.final_grade, subject.max_grade = map(float, i.contents[1].contents[3].contents[3].contents[1].contents[0].strip().split(' / '))
                                    if len(i.contents[1].contents) > 6:
                                        subject.promo_average = float(i.contents[1].contents[6].contents[0].split(' ')[-1])
                                        subject.coeff = float(i.contents[1].contents[10].contents[0].split(' ')[-1])
                                    else:
                                        subject.promo_average = float(i.contents[1].contents[5].contents[0].contents[0].split(' ')[-1])
                                        subject.coeff = float(i.contents[1].contents[5].contents[4].contents[0].split(' ')[-1])
                            
                            
                            # get subject public grades (sometimes they are all hidden !)
                            if len(i.contents) > 3:
                                for i in i.contents[3].contents:
                                    if i.name == 'li':
                                        # parse individual "public" grade !
                                        grade = Grade(
                                            name = _clean_string(i.contents[1].contents[2])
                                        )

                                        if len(i.contents[1].contents[3].contents) > 1:
                                            grade.grade, grade.max_grade = map(float, i.contents[1].contents[3].contents[3].contents[1].contents[0].strip().split(' / '))
                                            # the html is sometimes glitched :)
                                            if len(i.contents[1].contents) > 6:
                                                grade.promo_average = float(i.contents[1].contents[6].contents[0].split(' ')[-1])
                                            else:
                                                grade.promo_average = float(i.contents[1].contents[5].contents[0].contents[0].split(' ')[-1])
                            
                                        subject.grades.append(grade)
                            
                            unit.subjects.append(subject)
                    
                    semester.units.append(unit)

                semesters.append(semester)
        
        return semesters
    
    def get_abs(self) :
        soup = self.request_html("GET", ABS_URI)
        table = soup.find(class_ = 'table').find("tbody")

        absences = []
        for i in table.find_all("tr") :
            absences.append(Absence(
                subject_id = _clean_string(i.contents[3].contents[1].getText()),
                subject_name = _clean_string(i.contents[3].contents[2]),
                class_type = _clean_string(i.contents[5].getText()), 
                date = _clean_string(i.contents[7].getText()), 
                hour = _clean_string(i.contents[8].getText()), 
                duration = _clean_string(i.contents[10].getText()), 
                state = _clean_string(i.contents[12].getText())
            ))
        
        return absences
    
    def get_day_presences(self):
        soup = self.request_html("GET", PRESENCE_URI)
        table = soup.find(id="body_presences")
        presences = []
        date = soup.find(class_ = "panel-title").getText().strip().split()
        day = datetime(
            day=int(date[-3]), 
            month=1 + MONTHS.index(date[-2]) // 2, 
            year=int(date[-1])
        )
        
        for p in table.find_all("tr"):
            tdl = p.find_all("td")
            hours = tdl[0].getText().split()
            
            hosts = []
            for h in _clean_string(tdl[2].getText()).split(","):
                first_name, last_name = h.split()
                hosts.append(User(first_name=first_name, last_name=last_name))

            pres = Presence(
                start_time = day + _parse_timestr(hours[0]),
                end_time = day + _parse_timestr(hours[-1][1:]),
                subject_name = _clean_string(tdl[1].getText()),
                id = int(tdl[3].find('a').get('href').split('/')[-1]),
                hosts = hosts,
                success = p.get('class') == ['success']
            )

            # only if a zoom conference is configured for this class
            if tdl[4].find('a') is not None:
                pres.meeting_url = tdl[4].find('a').getText()
                pres.meeting_url_with_password = tdl[4].find('a').get('href')
                pres.meeting_password = tdl[4].find('span').get('title').split()[-1]
        
            presences.append(pres)
        return presences
    
    def get_class_presence(self, class_id: int):
        try:
            soup = self.request_html("GET", f"{PRESENCE_URI}{class_id}")
        except e:
            # handle not found !
            if e.status_code == 302: raise PresenceClassNotFound(f"Couldn't find a class with the id = {class_id}.")
            raise e
        
        tdl = soup.find("tbody").find_all("td")
        # parse dates
        date = _clean_string(tdl[0].getText()).split('/')
        day = datetime(
            day=int(date[0]), 
            month=int(date[1]), 
            year=int(date[2])
        )
        hours = tdl[1].getText().split(' - ')

        # parse hosts
        hosts = []
        hosts_raw = [_clean_string(tdl[2].getText())] if tdl[2].find('li') is None else [_clean_string(_.getText()) for _ in tdl[2].find_all('li')]
        

        for h in hosts_raw:
            first_name, last_name = h.split()
            hosts.append(User(first_name=first_name, last_name=last_name))
        
        pres = Presence(
                start_time = day + _parse_timestr(hours[0], 'h'),
                end_time = day + _parse_timestr(hours[1], 'h'),
                subject_name = _clean_string(soup.find(id = 'recap_cours').find('h3').getText()),
                id = int(class_id),
                hosts = hosts
        )

        body_presence = soup.find(id = 'body_presence')
        
        for p in body_presence.find_all('div'):
            c = p.getText()
            if 'pas encore ouvert' in c:
                pres.state = PresenceState.NOT_YET_OPEN

            # TODO: PresenceState: handle OPEN and CLOSED
            # TODO: handle success & parse success_time
        if tdl[3].find('a') is not None:
            pres.meeting_url = tdl[3].find('a').getText()
            pres.meeting_url_with_password = tdl[3].find('a').get('href')
            pres.meeting_password = tdl[3].find('span').get('title').split()[-1]

        return pres

    def set_class_presence(self, class_id: int):
        r = self.client.post(PRESENCE_UPLOAD_URI, data= {
            'act': 'set_present',
            'seance_pk': str(class_id)
        })
        
def _clean_string(s):
    # we remove garbage from start & tail of str
    s = s.strip()

    # on one specific unit there is a '\n' then approx 100 spaces after then the end of the unit name
    # this allows to fix the name !
    if '\n' in s:
        s = " ".join([_.strip() for _ in s.split('\n')])
    return s

def _parse_timestr(s: str, sep: str = ":"):
    h, m = map(int, s.split(sep))
    return timedelta(hours=h, minutes =m)