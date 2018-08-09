# Fortnite-Bot by th3infinity (#6720)

## Features
* Automatic WinRate Roles
  * blacklist
  * match Minimum
  * usageDatabase
* Tournament Crawler
* modList
* bot Channel restriction
* setup for multi server support
* databases are discord server based

### Auto WinRate
Takes a Platform <pc, psn, xbl> and the EpicGamesName as parameters. Platform can be lower or upper case. Bot transforms it into 
FortniteTracker readable format. 

* checks if name in blacklist
* gets stats from fntracker
* checks for minimum of Games
* adds used name + sender of command to userDatabase
* sends Warning at high WinRates
* sends log if AccNames was used more then one time

### Tournament Crawler
Crawles EGL and UMG (support for cmg to add) for Tournaments.

* saves posted Tournaments per server
* saves Tournaments in dict for use on other servers to reduce crawl time

To Add:
* Date Limit
* Entry Fee Parameter

## Suggestions and Credits/Usage
Feel free to use this Bot but it would be nice if you message me (maybe show your server) and give credits. ;)
I'm open to any suggestions or new features. Just open a pull request or add an issue.

If you wanna support me then I would be happy about an donation. Just message me. <3
