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

class Version:
    nr = "0"
    date = ""
    changes = ""
 
    def __init__(self, nr, date, changes):
        self.nr = nr
        self.date = date
        self.changes = changes

_version1 = Version("0.4.3", "2018-09-29", " - added winrate to output")
changeLog.append(_version1)