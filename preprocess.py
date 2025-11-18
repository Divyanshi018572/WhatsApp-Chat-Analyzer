import re
import pandas as pd

def preprocessor(data):
    # WhatsApp date-time format pattern
    pattern = r"\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s-\s"

    # Split messages
    messages = re.split(pattern, data)[1:]
    dates = re.findall(pattern, data)

    df = pd.DataFrame({"user_message": messages, "message_date": dates})

    # Convert to datetime
    df["message_date"] = pd.to_datetime(
        df["message_date"],
        format="%d/%m/%Y, %H:%M - ",
        errors="coerce"     # avoids crash on unexpected formats
    )
    df.rename(columns={"message_date": "date"}, inplace=True)

    users = []
    msg_list = []

    for message in df["user_message"]:
        # Split "User: message"
        entry = re.split(r"([\w\W]+?):\s", message, maxsplit=1)

        if len(entry) >= 3:
            users.append(entry[1])
            msg_list.append(entry[2])
        else:
            users.append("notification")
            msg_list.append(entry[0])

    df["user"] = users
    df["message"] = msg_list

    # Cleanup
    df.drop(columns=["user_message"], inplace=True)

    # Extract date components
    df["year"] = df["date"].dt.year
    df["month"] = df["date"].dt.month_name()
    df["month_num"] = df["date"].dt.month
    df["day"] = df["date"].dt.day
    df["hour"] = df["date"].dt.hour
    df["minute"] = df["date"].dt.minute
    df["only_date"] = df["date"].dt.date
    df["day_name"] = df["date"].dt.day_name()

    # Period column (Hour range like "13-14")
    period = []
    for hour in df["hour"]:
        if hour == 23:
            period.append("23-00")
        elif hour == 0:
            period.append("00-1")
        else:
            period.append(f"{hour}-{hour+1}")

    df["period"] = period

    return df
