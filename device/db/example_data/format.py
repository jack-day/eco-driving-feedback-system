def getNewTime(ts, hourChange, daysAgo):
    time = ts.split(' ')[1]
    hours = int(time[0:2]) + hourChange
    hours = '0' + str(hours) if hours < 10 else str(hours)
    time = hours + time[2:]
    return f"(CURRENT_DATE - INTERVAL '{daysAgo} days') + TIME '{time}'"


with open("formatted_example_data.sql", "w") as newFile:
    with open("original.sql", "r") as mockSQL:
        for line in mockSQL.readlines():
            if "INSERT INTO driving_data" in line:
                values = line.split('(')[1].split(', ')
                tsStr = values[0]
                ts = tsStr[1:-1]
                journeyID = values[1]

                if journeyID == '1':
                    newTime = getNewTime(ts, -12, 30)
                if journeyID == '2':
                    newTime = getNewTime(ts, -10, 27)
                if journeyID == '3':
                    newTime = getNewTime(ts, -14, 24)
                if journeyID == '4':
                    time = ts.split(' ')[1]
                    hours = int(time[0:2])
                    if hours == 0:
                        newTime = getNewTime(ts, 18, 21)
                    else:
                        newTime = getNewTime(ts, -6, 21)
                if journeyID == '5':
                    newTime = getNewTime(ts, 10, 18)
                if journeyID == '6':
                    newTime = getNewTime(ts, 14, 15)
                if journeyID == '7':
                    newTime = getNewTime(ts, 8, 12)
                if journeyID == '8':
                    newTime = getNewTime(ts, 17, 12)
                if journeyID == '9':
                    newTime = getNewTime(ts, 19, 8)
                if journeyID == '10':
                    newTime = getNewTime(ts, 15, 4)
                if journeyID == '11':
                    newTime = getNewTime(ts, 6, 0)

                newLine = line.replace(tsStr, newTime)
                newFile.write(newLine)
