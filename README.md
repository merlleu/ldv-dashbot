# LDV DashBot 🎒
A library to help you automate interactions with LDV's dashboard (such as tracking grades updates)

**NEW:** we just added support for telegram webhooks.

## What is the Api ?
Recently, LDV decided to deploy the app MyDeVinci (com.devinci.mobile / fr.devinci.student).
This app uses protocols such as OAuth2 for authentication, which is way better than the SAML (via cookies) implementation of the Bot.
This is why you should consider using the API if the available endpoints are sufficients for your use case (should be more stable than our html parser).

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
| Set user as present for a specific seance | bot.set_class_presence(seance_id)                                                    | api.set_present(seance_id) |
| Get user grades                           | bot.get_grades()                                                                     | -                          |

## FAQ

### What is cookie_cache

Cookie cache is a way to store session in a file to avoid the need to connect each time you restart the bot.
This is recommanded if you are still in dev/test phase, as the login process takes a few seconds and this may be detectable if you restart too frequently !


# ldv-watcher 🎒
A bot based on ldv-dashbot to get webhooks when grades or presences are updated.
At the moment, we only support discord webhooks on as hooks, but we may later allow any http request.

## INSTALL USING DOCKER
1. Run `git clone https://github.com/merlleu/ldv-dashbot && cd ldv-dashbot` to clone this repo.
2. Build the image using `docker build -t ldv-watcher .`
2. Create a data folder for persistance: `mkdir ./data`
4. Rename `config.example.yaml` to `./data/config.yaml` and edit its content.
5. Run using `docker run -d -v ${PWD}/data:/app/data -v ${PWD}/data/config.yaml:/app/config.yaml --name ldv-watcher ldv-watcher`
6. You can now check everything is working by reading logs using `docker logs -f ldv-watcher`
