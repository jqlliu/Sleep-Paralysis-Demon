from typing import Final, Dict
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, File
from discord.ext import tasks
from person import Person

from datetime import datetime

import time
import threading

import openpyxl 
import random

import socket
import threading

import math

host = ""
port = 8000
soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def connect():
    while True: 
        # Establish connection with client. 
        c, addr = soc.accept()


try: 
    print("LISTENING")
    soc.bind((host, port))
except socket.error as message:
    print("ERR")

soc.listen(5)
#import asyncio
thread = threading.Thread(target=connect)
thread.start()

days_cell: str = "M1"
#Open files
file = openpyxl.load_workbook('record.xlsx')
point = file["Point"]
info = file["Info"]
track = file["Track"]

print(info["A2"].value)
#List of users
users: Dict[str, Person] = {
    "hydrogenjack": Person("jack", 2),
    "beveornaut": Person("beaverly", 3),
    "c.jy.z": Person("catherine", 4),
    "sunsetsoul": Person("darren", 5),
    "the_fooled_one": Person("hanrick", 6),
}

key_id: Dict[str, int] = {
    #perm
    "graces": 1,
    "points": 2,
    "lates": 3,
    "streak": 4,
    "stalked": 5,
    "fill": 6,
    "today": 7
}

day: int = int(info[ days_cell ].value)

#simple functions
def save() -> None:
    file.save("record.xlsx")
def cell(col: chr, row: int) -> str:
    return chr(col + ord('A') - 1) + str(row + 1)
#Time string to tick
def to_number(t: str) -> int:
    hours, minutes, seconds = map(int, t.split(':'))
    return hours * 3600 + minutes * 60 + seconds
#Tick to time string
def to_time(t: int) -> str:
    t = t % 86400
    hours = t // 3600
    minutes = (t % 3600) // 60
    seconds = t % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
#How many minutes late
def minutes_late(t1: int | str, t2: int | str) -> int:
    t1 = to_dlt(to_number(t1)) if isinstance(t1, str) else to_dlt(t1)
    t2 = to_dlt(to_number(t2)) if isinstance(t2, str) else to_dlt(t2)
    t1 = (t1 - 18000) % 86400
    t2 = (t2 - 18000) % 86400
    if t2 <= t1:
        return -1
    return math.ceil((t2 - t1) / 60)

def slept(user: Person):
    return get(user, "today") == -10


def get_day() -> int:
    return int(info[ days_cell ].value)
#functions

def get_points(user: Person, day: int = get_day() - 1) -> int | bool:
    if point[cell(user.column, day)].value:
        return int(point[cell(user.column, day)].value)
    return False

def set_points(user: Person, points: int, day: int = get_day()) -> None:
    point[cell(user.column, day)].value = str(points)
    save()

def get_time(user: Person, day: int = get_day()) -> tuple[int, bool]:
    print(track[cell(user.column, day)].value)
    if track[cell(user.column, day)].value == "---": return (-10, False) 
    if track[cell(user.column, day)].value[-1:] == "f":
        return (to_number(track[cell(user.column, day)].value[:-2]), True)
    return (to_number(track[cell(user.column, day)].value), False)

def set_time(user: Person, val: str | int, fill = False, day: int = get_day()) -> tuple[int, bool]:
    if fill:
        track[cell(user.column, day)].value = to_time(val) + " f"
    else:
        track[cell(user.column, day)].value = to_time(val)
#Get some info of a user
def get(user: Person, key: str) -> int | str:
    c = info[cell(user.column, key_id[key])]
    try:
        return int(c.value)
    except:
        return c.value

#put some info of a user
def put(user: Person, key: str, value: int | str) -> None:
    row = key_id[key]
    info[cell(user.column, row)].value = str(value)
    save()

def sum_points(user: Person) -> int:
    total = 0
    for i in range(1, get_day()):
        total += get_points(user, i)
    return total

def setup() -> None:
    for v in users.values():
        put(v, "points", sum_points(v))
    



night_crawler: str = "00:30:00"
four_am: str = "05:00:00"
interval: int = 15 * 60
done: int = 0
stalk_time: int = 60*90
default_points = 50

def on_time(t1: int | str, t2: int | str) -> bool:
    t1 = to_dlt(to_number(t1)) if isinstance(t1, str) else to_dlt(t1)
    t2 = to_dlt(to_number(t2)) if isinstance(t2, str) else to_dlt(t2)
    
    t1 = (t1 - 18000) % 86400
    t2 = (t2 - 18000) % 86400
    
    return t1 > t2

def current_month_day() -> tuple[int, int]:
    now = datetime.now()
    return now.month, now.day

def to_dlt(t: str | int) -> int:
    t = to_number(t) if isinstance(t, str) else t
    month, day = current_month_day()
    dst = (month > 3 and month < 11) or (month == 3 and day >= 8) or (month == 11 and day < 8)
    return t + 3600 if dst else t

def calculate_min() -> tuple[int, int]:
    min: int = -1
    two: int = -1
    for v in users.values():
        points = get(v, "points")
        if points <= min or min == -1:
            min = points
            two = min
    return (min, two)

#point managment

def calculate_points(user: Person, done: int, name: str, seconds: int) -> tuple[int, str, int]:
    #Calculate first and second place
    min, two = calculate_min()

    #points to add
    points_add: int = 8 * (done - 1)
    #wtf does this do
    late_status: int = 0
    #Message
    message = ""
    message += name + " was #" + str(done) + "!\n"

    #info
    points = get(user, "points")
    streak = get(user, "streak")

    #Night crawler
    if on_time(seconds, to_dlt(night_crawler)) and on_time(to_dlt(four_am), seconds) and not user.late:
        a = minutes_late(seconds, to_dlt(four_am)) % 10
        m = 1
        #Night hunter
        if points == min and two - min >= 5:
            m = 2
            message += "Night hunter hunts down first place for an extra " + str(a) + " points!\n"
        
        points_add += a * m
        message += "Night crawler attacked for " + str(a) + " points!\n"
        if points >= min + 30:
            late_status = -1
    else:
        if not user.late and points >= min + 30:
            if streak > 0:
                message += "Melody is among us! -" + str(user.streak) + " points!\n"
            points_add -= user.streak * 3
            late_status = 1

    #Symphony
    if points >= min + 20 and (done == 1 or done == 2):
        points_add -= 8
        message += "Symphony kicked in! -3 point\n"
    #Requium
    if points >= min + 15 and done == 1:
        points_add -= 10
        message += "Requium is active! -5 point\n"
    message = name + " has slept with " + str(points_add) + " points!\n" + message
    return (points_add, message, late_status)



def flatten_points(day: int = get_day()) -> None:
    places: list[tuple[Person, int]] = []
    for v in users.values():
        places.append((v, get_time(v, day)[0]))

    places.sort(key=lambda a: a[1])
    for i in range(0, 5):
        set_points(places[i][0], calculate_points(places[i][0], i + 1, "", get_time(places[i][0], day)[0])[0], day)
    

def flatten_all():
    for i in range(1, get_day() + 1):
        flatten_points(i)
    save()


#initial setup
load_dotenv()
flatten_all()
setup()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
#setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

#responces
print("Listening")

def get_response(input: str, message: Message) -> str:
    name: str = message.author.name
    input = str.lower(input)
    seconds: int = int(time.time()) % 86400
    user: Person = users[name]
    global night_crawler
    global done
    global daylight
    if user != None:
        #Gning
        if input == "gn" and user.today == -10:
            done += 1
            user.place = done
            a = calculate_points(user, done, name, seconds)
            put(user, "today", seconds)
            user.today = seconds
            set_time(user, seconds)

            s = a[1]
            if a[2] == 1 :
                put(user, "streak", get(user, "streak") + 1)
            elif a[2] == -1:
                put(user, "streak", 0)
            return s

        if input == "gn" and get_points(user, get_day() + 1):
            return "You already gn'd fool"

        #Late ticket
        if input == "late":
            user.late = True
            return name + " uses a saving grace. Night crawlers will not affect them"
        #Stalk
        if input == "stalk":
            user.stalked = not user.stalked
            if user.stalked:
                return name + " is being stalked during night! "
            else:
                return name + "'s trail is cold..."
        
        if input == "file":
            return "!!FILE!!"

        #Fill in time for yesterday
        if input[:4] == "fill" and get(user, "fill") == 1:
            
            return name + " has signaled their correct sleep time. Their points was adjusted by " + str(a)
        if input[:4] == "fill" and not user.last_late:
            return "You wern't late last night. Go drink sulfuric acid"
        #List stats
        if input == "stats" or input == "stat":
            r = ""
            for v in users.values():
                r += v.name + ": " + str(v.points) + " pts and " + str(v.lates) + " graces and a "  + str(v.streak) + " streak!\n" 
            return r
        #Make exception
        if input[:6] == "except":
            t = input[7:]
            t = t.split(" ")
            if len(t) == 2 and (str.isdigit(t[1]) or str.isdigit(t[1][1:]) and t[1][0] == "-") and users[t[0]]:
                n: str = t[0]
                p: int = int(t[1])
                users[n].points += p
                return n + " has been obliterated by " + name + " for " + str(p) + " points! "
            else:
                return "Wrong parameters bozo"
        #change crawler time
        if input[:5] == "crawl":
            t = input[6:]
            night_crawler = t
        return "BAHH WHAT HAPPENED SOMETHIGN ERORRE D AHHHH"

def deleted(input: str, message: Message) -> str:
    name: str = message.author.name
    input = str.lower(input)
    user: Person = users[name]
    global done
    if user != None:
        #Gn deleted
        if input == ";gn" and slept(user):
            done -= 1
            user.place = 0
            put(user, "today", -10)
            user.today = 0
            set_time(user, "")
            return name + " revoked their gn! Sending ballistic missiles"
    return "You have killed me"

#message handling
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("ERROR: NO MESSAGE") 
        return
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]
    try:
        if not is_private:
            if user_message[0] == ";":
                responses: str = get_response(user_message[1:], message)
                if responses == "!!FILE!!":
                    await message.channel.send(file=File(r"./record.xlsx"))
                else:
                    await message.channel.send(responses)

    except Exception as e:
        print(e)

async def send(message: str)-> None :
    await client.get_channel(1260219510292611082).send(message)

async def delete_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("ERROR: NO MESSAGE") 
    if is_private := user_message[0] == '?':
        user_message = user_message[1:]
    try:
        if not is_private:
            if user_message[0] == ";":
                responses: str = deleted(user_message, message)
                await message.channel.send(responses)

    except Exception as e:
        print(e)

@client.event
async def on_ready() -> None:
    print(f'{client.user} started')
    timer.start()

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
        return
    if message == None or len(message.content) == 0:
        return
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    await send_message(message, user_message)

@client.event
async def on_message_delete(message: Message) -> None:
    if message.author == client.user:
        return
    username: str = str(message.author)
    user_message: str = message.content
    channel: str = str(message.channel)

    await delete_message(message, user_message)

#Timer
updated = False
nighted = False
def update_charts() -> None:
    print("updating")
    global updated
    global day
    global done
    
    if not updated:
        updated = True
        

        flatten_points(get_day())

        setup()
        
        info[days_cell].value = str(get_day() + 1)

        for v in users.values():
            track[cell(v.column, get_day())].value = "---"
        print("update successful")
        
        save()
    
def reset_charts() -> None:
    global nighted
    global updated
    updated = False
    nighted = False

async def warn_night() -> None:
    global nighted
    if not nighted:
        nighted = True
        try:
            s = "NIGHT CRAWLERS HERE IN 10 MINUTE. GET AWAY TO SAFETY:"
            for i, v in users.items():
                if v.today == -10:
                    a = str(client.get_guild(1171158336864010330).get_member_named(i).id)
                    s += " <@{a}>\n"
            await send(s)
        except Exception as e:
            print("ERROR")

async def warn_stalk() -> None:
    global nighted
    if not nighted:
        nighted = True
        try:
            s = "NIGHT STALKERS HERE. HIDE. NOW:"
            for i, v in users.items():
                if ( get(v, "today") != 0 or not v.ready ) and v.stalked :
                    a = str(client.get_guild(1171158336864010330).get_member_named(i).id)
                    s += " <@{a}>\n"
            await send(s)
        except Exception as e:
            print("ERROR")

funnies = ["BANANA", "LEMON", "You have 5 days left to live", "PINEAPPLE", "DON'T LOOK BEHIND YOU", "Beaverly commits high treason", "We're no strangers to love\nYou know the rules and so do I\nA full commitment's what I'm thinkin' of\nYou wouldn't get this from any other guy\nI just wanna tell you how I'm feeling\nGotta make you understand\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\nWe've known each other for so long\nYour heart's been aching, but you're too shy to say it\nInside, we both know what's been going on\nWe know the game and we're gonna play it\nAnd if you ask me how I'm feeling\nDon't tell me you're too blind to see\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\nWe've known each other for so long\nYour heart's been aching, but you're too shy to say it\nInside, we both know what's been going on\nWe know the game and we're gonna play it\nI just wanna tell you how I'm feeling\nGotta make you understand\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you\nNever gonna give you up\nNever gonna let you down\nNever gonna run around and desert you\nNever gonna make you cry\nNever gonna say goodbye\nNever gonna tell a lie and hurt you"]

async def funny() -> None:
        try:
            await send(funnies[random.randint(1, len(funnies))])
        except Exception as e:
            print(e)
@tasks.loop(seconds = 0.5)

async def timer():
    if int(time.time()) % 86400 > to_number(four_am) and int(time.time()) % 86400 < to_number(four_am) + 10 :
        update_charts()
    elif int(time.time()) % 86400 == to_number(night_crawler):
        await warn_night()
    else:
        reset_charts()
    if random.randint(0, 500000) == 3:
        await funny()


#timer_thread = threading.Thread(target=wrap_timer)
#timer_thread.start()
#asyncio.run(timer())
def main() -> None:
    client.run(token = TOKEN)
    
if __name__ == '__main__':
   main()

