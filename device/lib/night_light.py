import time

def cettime():
    """https://forum.micropython.org/viewtopic.php?t=4034 (Thx to JumpZero)"""
    year = time.localtime()[0]       #get current year
    HHMarch   = time.mktime((year,3 ,(31-(int(5*year/4+4))%7),1,0,0,0,0,0)) #Time of March change to CEST
    HHOctober = time.mktime((year,10,(31-(int(5*year/4+1))%7),1,0,0,0,0,0)) #Time of October change to CET
    now=time.time()
    if now < HHMarch :               # we are before last sunday of march
        cet=time.localtime(now+3600) # CET:  UTC+1H
    elif now < HHOctober :           # we are before last sunday of october
        cet=time.localtime(now+7200) # CEST: UTC+2H
    else:                            # we are after last sunday of october
        cet=time.localtime(now+3600) # CET:  UTC+1H
    return(cet)


def timeToTuple(t): #?
    """Convert HH:mm to (HH,mm)"""
    return tuple(map(int, t.split(':')))


def getColor(rules, current_time):
    for rule in rules :
        current = current_time
        current_hhmm = '{}:{}'.format(('0'+str(current[3]))[-2:],('0'+str(current[4]))[-2:])
        begin, end = rule['begin'], rule['end']
        if (begin > end and (current_hhmm >= begin or current_hhmm < end )) or (begin < end and current_hhmm >= begin and current_hhmm < end ):
            return rule['colors']
            

"""
r={"rules":[
    {"begin":'20:05', "end":'07:30', 'colors':{"r": 0, "g": 0, "b":256}},
    {"begin":'07:30', "end":'20:30', 'colors':{"r": 0, "g": 256, "b":0}},
 ]
}
"""
