###Tournaments Stuff
class Tournament:
    next_id = 0

    def __init__(self,t_name,t_time,t_reg,t_costs,t_link,t_slots,t_id):
        self.id = Tournament.next_id
        Tournament.next_id += 1
        self.name = t_name
        self.time = t_time
        self.reg = t_reg
        self.costs = t_costs
        self.link = t_link
        self.slots = t_slots
        self.tid = t_id

class Version:
    nr = "0"
    date = ""
    changes = ""
 
    def __init__(self, nr, date, changes):
        self.nr = nr
        self.date = date
        self.changes = changes