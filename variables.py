developerID = 198844841977708545
botID = 470506590647091211 #TestBot
#botID = 511332522807001119 #RealBot
changeLog = []

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