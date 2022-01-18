import requests
from .constants import *
from .types import *
from bs4 import BeautifulSoup

class BotConfig: 
    email = ''
    password = ''

class AuthError(BaseException):
    def __init__(self, s): self.s = s
    def __repr__(self): return self.s

class NotAuthenticatedError(BaseException):pass
class InvalidCredentials(BaseException):pass

class Bot:
    def __init__(self, email, password):
        self.config = BotConfig()
        self.config.email = email
        self.config.password = password

        self.client = requests.Session()
        self.client.headers.update({'User-Agent': USER_AGENT})

        self.login()

  
    def login(self):
        # first of all we attempt a redirect to the login page
        self.client.get(LDVNET_URL)
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

    def parse_raw_homepage(self, raw):
        soup = BeautifulSoup(raw, 'html.parser')
        addr = soup.find_all('address')
        if not addr:
            raise NotAuthenticatedError()
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

    def request_html(self, method, url, **kwargs):
        r = self.client.request(method, url, **kwargs, allow_redirects=False)
        soup = BeautifulSoup(r.text, 'html.parser')
        if form.find('btn_connect') is not None:
            self.login()
            return self.request(method, url, **kwargs)
        else:
            return soup

    def get_grades(self):
        soup = self.request_html("GET", MARKS_URI)
        