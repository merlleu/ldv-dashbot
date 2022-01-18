# ldv-dashbot
A library to help you automate interactions with LDV's dashboard (such as tracking grades updates)


## INSTALL 
1. First, you have to download this repo
2. Jump in the repo folder (after extracting it)
3. Run `pip install -r requirements.txt`
4. Run `python test.py` to start with a simple grades exporter !

## FAQ

### What is cookie_cache

Cookie cache is a way to store session in a file to avoid the need to connect each time you restart the bot.
This is recommanded if you are still in dev/test phase, as the login process takes a few seconds and this may be detectable if you restart too frequently !
