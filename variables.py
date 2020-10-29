developerID = 198844841977708545
footerText = 'made with ♥ by th3infinity#6720'
botID = 470506590647091211 #TestBot
#botID = 511332522807001119 #RealBot
changeLog = []

rankNames = {   '80': '80+',
                '70': '70%', 
                '60': '60%', 
                '50': '50%', 
                '40': '40%', 
                '30': '30%', 
                '25': '25%', 
                '20': '20%', 
                '15': '15%', 
                '10': '10%' }

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