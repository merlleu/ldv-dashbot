LDVNET_URL = "https://www.leonard-de-vinci.net"
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'
AJAX_URL = LDVNET_URL + "/ajax.inc.php"
MARKS_URI = LDVNET_URL + "/?my=marks"
ABS_URI = LDVNET_URL + "/?my=abs"
PRESENCE_URI = LDVNET_URL + "/student/presences/"
PRESENCE_UPLOAD_URI = PRESENCE_URI + "upload.php"
STUDENT_UPLOAD_URI = LDVNET_URL + "/student/upload.php"
PROMOTION_AJAX_URI = LDVNET_URL + "/ajax/promotion"
PROMOTION_URI = LDVNET_URL + "/promotion/"
STUDENT_COURS_UPLOAD_URL = LDVNET_URL + "/student/cours/upload.php"
STUDENT_EVALUATIONS_URL = LDVNET_URL + "/student/cours/evaluations/{y}/{c}"
INTERACTIONS_URL = LDVNET_URL + "/interaction.php"


# -- myDeVinci app
# - OAuth2
OA2_CLIENT_ID = "ada8d8-98f42d-0df633-c1f59b-a64d83"
OA2_REDIRECT_URI = "com.devinci.mobile:/oauthredirect"
OA2_BASE = "https://adfs.devinci.fr/adfs/oauth2/"
OA2_AUTHORIZE = OA2_BASE + "authorize"
OA2_TOKEN = OA2_BASE + "token"
OA2_LOGOUT = OA2_BASE + "logout"

# - API
API_STUDENT_BASE = "https://api.devinci.me/students/"
API_STUDENT_ABSENCES = API_STUDENT_BASE + "absences"
API_STUDENT_PROFILE = API_STUDENT_BASE + "profile"
API_STUDENT_PRESENCES = API_STUDENT_BASE + "presences"
API_STUDENT_PRESENCE = API_STUDENT_BASE + "presence/{}"
API_STUDENT_ICAL = "https://ical.devinci.me/ical_student/{}"