# ldv-dashbot
A library to help you automate interactions with LDV's dashboard (such as tracking grades updates)

## What is the Api ?
Recently, LDV decided to deploy the app MyDeVinci (com.devinci.mobile / fr.devinci.student).
This app uses protocols such OAuth2 for authentication, wich is way better than the SAML (via cookies) implementation of the Bot.
This is why you should consider using the API if the available endpoints are sufficiants for your use case (should be more stable than our html parser).


## INSTALL 
1. First, you have to download this repo
2. Jump in the repo folder (after extracting it)
3. Run `pip install -r requirements.txt`
4. Run `python test_crawler.py` to start with a simple grades exporter !

## ENDPOINTS
| Action                                    | Bot (crawler)                                                                        | Api (app)                  |
| ----------------------------------------- | ------------------------------------------------------------------------------------ | -------------------------- |
| Get authenticated user profile            | bot.user                                                                             | api.get_profile()          |
| Get user absences                         | bot.get_abs()                                                                        | api.get_absences()         |
| Get user presences of the day             | bot.get_day_presences() *Doesn't tell you if you are marked as present on a seance.* | api.get_presences()        |
| Get user presences for a specific seance  | bot.get_class_presence(seance_id) *Use this to know if you are marked as present !*  | -                          |
| Set user as present for a specific seance | bot.set_class_presence(seance_id) **Unfinished**                                     | api.set_present(seance_id) |
| Get user grades                           | bot.get_grades()                                                                     | -                           |

## FAQ

### What is cookie_cache

Cookie cache is a way to store session in a file to avoid the need to connect each time you restart the bot.
This is recommanded if you are still in dev/test phase, as the login process takes a few seconds and this may be detectable if you restart too frequently !