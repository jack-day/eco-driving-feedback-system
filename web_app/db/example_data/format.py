from datetime import datetime

def getNewTime(ts, hourChange, daysAgo):
    time = ts.split(' ')[1]
    hours = int(time[0:2]) + hourChange
    hours = '0' + str(hours) if hours < 10 else str(hours)
    time = hours + time[2:]
    return f"(CURRENT_DATE - INTERVAL '{daysAgo} days') + TIME '{time}'"

with open("formatted_example_data.sql", "w") as newFile:
    with open("original.sql", "r") as mockSQL:
        for line in mockSQL.readlines():
            if "INSERT INTO scores" in line:
                values = line.split('(')[1].split(', ')
                tsStr = values[1]
                ts = tsStr[1:-1]
                newTs = ts[0:-3]
                if len(newTs) == 25: newTs += '0'
                if len(newTs) == 24: newTs += '00'
                time = datetime.fromisoformat(newTs.replace(' ', 'T') + '+01:00')

                if time < datetime.fromisoformat('2022-05-04T23:42:00+01:00'):
                    newTime = getNewTime(ts, -12, 30)
                elif time < datetime.fromisoformat('2022-05-04T23:49:00+01:00'):
                    newTime = getNewTime(ts, -10, 27)
                elif time < datetime.fromisoformat('2022-05-04T23:55:00+01:00'):
                    newTime = getNewTime(ts, -14, 24)
                elif time < datetime.fromisoformat('2022-05-05T00:13:00+01:00'):
                    time = ts.split(' ')[1]
                    hours = int(time[0:2])
                    if hours == 0:
                        newTime = getNewTime(ts, 18, 21)
                    else:
                        newTime = getNewTime(ts, -6, 21)
                elif time < datetime.fromisoformat('2022-05-05T00:24:00+01:00'):
                    newTime = getNewTime(ts, 10, 18)
                elif time < datetime.fromisoformat('2022-05-05T00:31:00+01:00'):
                    newTime = getNewTime(ts, 14, 15)
                elif time < datetime.fromisoformat('2022-05-05T00:35:00+01:00'):
                    newTime = getNewTime(ts, 8, 12)
                elif time < datetime.fromisoformat('2022-05-05T00:39:00+01:00'):
                    newTime = getNewTime(ts, 17, 12)
                elif time < datetime.fromisoformat('2022-05-05T00:43:00+01:00'):
                    newTime = getNewTime(ts, 19, 8)
                elif time < datetime.fromisoformat('2022-05-05T00:52:00+01:00'):
                    newTime = getNewTime(ts, 15, 4)
                elif time < datetime.fromisoformat('2022-05-05T01:03:00+01:00'):
                    newTime = getNewTime(ts, 6, 0)
                
                newLine = line.replace(tsStr, newTime)
                newFile.write(newLine)