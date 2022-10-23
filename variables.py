from model import Version
from dateutil import tz

developerID = 198844841977708545
footerText = 'made with ♥ by th3infinity#6720'
botID = 470506590647091211 #TestBot
#botID = 511332522807001119 #RealBot
changeLog = []
debug = False

url = "https://api.fortnitetracker.com/v1/profile/{}/{}"
cmgurl = "https://www.checkmategaming.com/tournament/pc/fortnite/-80-free-amateur-global-2v2-fortnite-br-1nd-{}-{}"
platforms = ['pc', 'psn', 'xbl']
roles = ['80%+', '70%', '60%', '50%', '40%', '30%', '25%', '20%', '15%', '10%']
maint = False

hdr = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Accept-Charset': 'ISO-8859-1,utf-8;q=0.7,*;q=0.3',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive'}

localTimezone = tz.tzlocal()

umg_tournaments = []
egl_tournaments = []
cmg_tournaments = []

_version1 = Version("0.4.3", "2018-09-29", " - added winrate to output")
changeLog.append(_version1)