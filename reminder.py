############
## Module: reminder
## Author: Theunkn0wn1
## Function: add means to track paperwork and remind user if its not completed in a timely fashion
#####
##Imports
import hexchat as hc

######
## Hexchat required vars
__module_name__ = "reminder"
__module_version__ = "0.0.1"
__module_description__ = "reminds user if they still have pending PW"
######
## Config
# Your nickname
nickname = "theunkn0wn1"
# time in milliseconds between reminders
frequency = 120 * 1000

##
######
## Debug stuff - leave this be!
override_nickCheck = 1
strEvent = "['\x0327MechaSqueak[BOT]', 'Case XXFLIP916XX cleared! Infinite Jager, do the Paperwork: http://t.fuelr.at/gs9', '%']"
strEvent2 = [':MechaSqueak[BOT]!sopel@bot.fuelrats.com', 'PRIVMSG', '#ratchat', ':Case', 'HWM', 'Merlin', 'cleared!',
             'SC', 'Davros,', 'do', 'the', 'Paperwork:', 'http://t.fuelr.at/gsc']
# strEvent3 = [':RatMama[BOT]!RatMama@bot.fuelrats.com', 'PRIVMSG', '#ratchat', ':[API]', 'Paperwork', 'for', 'rescue', 'of', 'Rellian', 'in', 'NYEAJEE', 'SE-X', 'A28-4', 'has', 'been', 'completed', 'by', 'theunkn0wn1[PC][2]']
strEvent3 = [':RatMama[BOT]!RatMama@bot.fuelrats.com', 'PRIVMSG', '#ratchat', ':[API]', 'Paperwork', 'for', 'rescue',
             'of', 'HWM', 'in', 'NYEAJEE', 'SE-X', 'A28-4', 'has', 'been', 'completed', 'by', 'SC Davros,']
strEvent4 = strEvent2


# strEvent4[7] = 'potato'
def log(trace, msg, color=19):
    print(
    "[{Stack}:{trace}]\t \003{color}{message}".format(Stack=__module_name__, message=msg, trace=trace, color=color))


##
######
## Constants, leave these be!
masterDict = {'None': None}  # init the var as a dict, key purged during Init()
# masterDict.update({2: {'rat': 'Sir_Toby,', 'client': 'Ariestattoo'}, 3: {'rat': 'Do the', 'client': 'steeltiger484'}, 4: {'rat': 'Jim Wolfe,', 'client': 'h4x'}, 5: {'rat': 'Sir_Toby,', 'client': 'brown_couch4324'}})
dbIndex = 0
# bot's names
botNick = [":MechaSqueak[BOT]!sopel@bot.fuelrats.com", ":RatMama[BOT]!RatMama@bot.fuelrats.com"]


##
######
## DB Functionality, to keep track of the PW
class DataBase():
    """Holds DB management methods"""
    global masterDict
    masterDict.pop('None', None)

    def genCase(self, CID, client, rat):
        """Generates a new case Dictionary object"""
        ret = {
            CID: {
                'client': client,
                'rat': rat,
            }
        }
        return (ret)

    def append(self, CID, client, rat):
        """Add a case to the DataBase"""
        global masterDict
        try:
            masterDict.update(self.genCase(CID, client, rat))
            return (1)  # append sucessful
        except Exception:
            return (0)  # error occured, handle in calling method

    def remove(self, CID):
        """Removes a case from the DataBase by ID"""
        global masterDict
        result = masterDict.pop(CID, None)
        if result == None:
            return (0)  # error, probably the key not existing
        else:
            return (1)  # no error, return sucessful


##

class commands():
    """docstring for commands"""
    db = DataBase()

    def isRelated(self, target):
        global nickname
        return (target == nickname)

    def parseHook(self, x, y, z):
        ret = self.ParseEvent(x)
        # log("parseHook",ret)
        self.process(ret)
        # log("parseHook2",x)
        return (hc.EAT_NONE)

    def process(self, x):
        """processes relevent events and discards irrelevents"""
        global dbIndex
        global nickname
        global override_nickCheck
        # log("process",x[0])
        try:
            pass
            if x[0] == 1 and x[3] > 1:  # API event, md entry
                client = x[1]
                rat = "{},".format(x[2])
                for key in masterDict:
                    # log("process","trying to locate key matching rat {} and client {}".format(rat,client))
                    # log("process","master[key][{}] == {}".format(masterDict[key]['client'],client))
                    if masterDict[key]['client'] == client:
                        log("md+", "Hit! removing key {}".format(key))
                        self.db.remove(key)
                        break  # otherwise python gets really upset

            elif x[0] == 0 and x[3] > 1:  # new PW entry to parse
                if self.isRelated(x[2]) or override_nickCheck:
                    self.db.append(dbIndex, x[1], x[2])
                    dbIndex += 1
                    log("process", masterDict)
                else:
                    log("process", "Unrelated event")
                    log("process", "{} {}".format(x[1], x[2]))
            else:
                pass
        except Exception as e:
            pass

    def readOut(self, x, y=None, z=None):
        global masterDict
        log("readout", masterDict)
        return (True)  # resets timer hook

    def purge(self, x, y, z):
        """manually purges a case via CID"""
        CID = int(x[1])
        log("purge", "attempting puge of CID [{}] from db...".format(CID), 17)
        if self.db.remove(CID):
            log("purge", "Purge sucessful", 17)
        else:
            log("purge", "purge failed - no such CID [{}]".format(CID), 20)

    def ParseEvent(self, eventArg):
        commander = ""
        rat = ""
        try:
            sender = eventArg[0]  # gets the sender of the message
            if sender == botNick[0]:
                # its mecha - Paperwork to be done!
                i = 0
                commander = ""
                rat = ""
                validMarker = 0  # means of judging if the message is probably relevant
                for val in eventArg:
                    if val == ':Case':
                        commander = eventArg[i + 1]  # client name
                        validMarker += 1
                    elif val == 'cleared!':  # next line is the commander
                        rat = eventArg[i + 1]
                        if eventArg[i + 2] != 'do':  # if the commander has a single space in name
                            rat = "{} {}".format(rat, eventArg[i + 2])
                        validMarker += 1
                    i += 1
                return ([0, commander, rat, validMarker])
            elif sender == botNick[1]:
                # its RAtMamma! someone (probably) just completed paperwork becuase noone invokes her wrath, right?
                i = 0  # iterator
                validMarker = 0
                for val in eventArg:
                    if val == 'of':  # word preceding the client
                        commander = eventArg[i + 1]
                        validMarker += 1
                    elif val == 'by':  # word preceding Rat that completed PW
                        rat = eventArg[i + 1]
                        validMarker += 1
                    elif val == ":[API]":  # someone fired a API report event, this is probably good ;)
                        validMarker += 1
                    i += 1
                log("ParseEvent", [1, commander, rat, validMarker])
                return ([1, commander, rat, validMarker])
            else:
                return ([-1, None, None, None])  # event not relevent
        except Exception as e:
            pass

    def test(self, x, y, z):
        # self.process(self.ParseEvent(strEvent4))
        # self.process(self.ParseEvent(strEvent3))
        # self.process(self.ParseEvent(strEvent2))
        # self.process(self.ParseEvent(strEvent3))
        self.process([0, "clienz", "theunkn0wn1", 3])
        self.process([0, "clientz", "theunkn0wn1", 3])
        self.process([1, "brown_couch4324", "Sir_Toby,", 3])


def init():
    global frequency
    log("init", "=============------------===============")
    log("init", "initializing commands...")
    cmd = commands()
    log("init", "hooking server...")
    # hook is fired on server message/PM
    hc.hook_server("PRIVMSG", cmd.parseHook)  # hooks when the user is mentioned
    # hooks fire when the associated slash-command is entered
    log("init", "hooking commands...")
    hc.hook_command("test", cmd.test)
    hc.hook_command("readOut", cmd.readOut)
    hc.hook_command("purge", cmd.purge)
    # for timed reminders, HC provides a method for triggering timed callbacks
    log("init", "Hooking timer...")
    hc.hook_timer(frequency, cmd.readOut)
    log("init", "Done!")
    log("Init", "-----------------\n{} version {} loaded successfully!\n--------------".format(__module_name__, __module_version__))
init()
