import time

def GetTime():

    DateTime = time.gmtime(time.time() - 6*60*60)

    Time = (DateTime[3],DateTime[4],DateTime[5])
    return Time


