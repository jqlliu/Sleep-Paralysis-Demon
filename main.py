from typing import Final, Dict
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, File
from discord.ext import tasks
from person import Person

from datetime import datetime
import functools
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


testing = False
# if not testing:
#     class RequestHandler(BaseHTTPRequestHandler):
#         print("RECIEVED")
#         def do_POST(self):
#             if self.path == "/":

#                 self.send_response(200)
#                 self.end_headers()
#                 self.wfile.write(b"OK")


def connect():
    if not testing:
        while True: 
            # Establish connection with client. 
            c, addr = soc.accept()


if not testing:
    try: 
            print("LISTENING")
            soc.bind((host, port))
    except socket.error as message:
        print("ERR")

    soc.listen(5)
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
#convert time zones
def to_standard(t: str | int) -> int:
    t = to_number(t) if isinstance(t, str) else t
    return (t + 18000) % 86400
def to_est(t: str | int) -> int:
    t = to_number(t) if isinstance(t, str) else t
    return (t - 18000) % 86400
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
#How many minutes late t1 is
def minutes_late(t1: int | str, t2: int | str) -> int:
    t1 = to_number(t1) if isinstance(t1, str) else t1
    t2 = to_number(t2) if isinstance(t2, str) else t2
    t1 = (t1 - 36000) % 86400
    t2 = (t2 - 36000) % 86400
    if t1 <= t2:
        return -1
    return math.ceil((t1 - t2) / 60)

def slept(user: Person):
    return get(user, "today") != -10

def get_day() -> int:
    return int(info[ days_cell ].value)

def get_points(user: Person, day: int = get_day() - 1) -> int | bool:
    if point[cell(user.column, day)].value:
        return int(point[cell(user.column, day)].value)
    return False

def set_points(user: Person, points: int, day: int = get_day()) -> None:
    point[cell(user.column, day)].value = str(points)
    save()

def get_time(user: Person, day: int = get_day()) -> tuple[int, bool, bool]:
    if track[cell(user.column, day)].value == "---": return (-10, False, False) 
    c = track[cell(user.column, day)].value[-1:]
    if c == "f":
        return (to_standard(to_number(track[cell(user.column, day)].value[:-2])), True, False)
    if c == "l":
        return (to_standard(to_number(track[cell(user.column, day)].value[:-2])), False, True)
    return (to_standard(to_number(track[cell(user.column, day)].value)), False, False)

def set_time(user: Person, val: str | int, fill = False, day: int = get_day()) -> tuple[int, bool]:
    if val == "":
        track[cell(user.column, day)].value = "---"
    elif fill:
        track[cell(user.column, day)].value = to_time(to_est(val)) + " f"
    elif user.late:
        track[cell(user.column, day)].value = to_time(to_est(val)) + " l"
    else:
        track[cell(user.column, day)].value = to_time(to_est(val))
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

def broken_streak(returns: tuple[int, bool]) -> bool:
    return True if returns[1] or returns[0] == -10 else False

def setup() -> None:
    for v in users.values():
        put(v, "points", sum_points(v))
        put(v, "today", -10)
    



night_crawler: str = "00:30:00"
dead_time: str = "05:00:00"
interval: int = 15 * 60
done: int = 0
stalk_time: int = 60*90
default_points = 50

def on_time(t1: int | str, t2: int | str) -> bool:
    t1 = to_number(t1) if isinstance(t1, str) else t1
    t2 = to_number(t2) if isinstance(t2, str) else t2
    
    t1 = (t1 - 36000) % 86400
    t2 = (t2 - 36000) % 86400
    
    return t1 > t2

def current_month_day() -> tuple[int, int]:
    now = datetime.now()
    return now.month, now.day

def to_dlt(t: str | int) -> int:
    t = to_number(t) if isinstance(t, str) else t
    month, day = current_month_day()
    dst = (month > 3 and month < 11) or (month == 3 and day >= 8) or (month == 11 and day < 8)
    return t if dst else t - 3600

def calculate_min() -> int:
    min: int = -1
    for v in users.values():
        points = get(v, "points")
        if points <= min or min == -1:
            min = points
    return min

#point managment

def calculate_points(user: Person, done: int, name: str, seconds: int, late: bool = False) -> tuple[int, str, int]:
    #Calculate first and second place
    min = calculate_min()
    #points to add
    points_add: int = 8 * (done - 1)
    #wtf does this do
    late_status: int = 0
    #Message
    message = ""
    message += name + " was #" + str(done) + "!\n"
    if user.late: 
        late = True
    #info
    points = get(user, "points")
    streak = get(user, "streak")
    #Night crawler
    if on_time(seconds, to_dlt(to_standard(night_crawler))) and not late:
        a = minutes_late(seconds, to_dlt(to_standard(night_crawler))) // 10
        points_add += a
        message += "Night crawler attacked for " + str(a) + " points!\n"
        if points >= min + 80:
            late_status = -1
            message += name + "'s streak falls...\n"
    else:
        if points >= min + 80:
            if streak > 0:
                message += "Melody is among us! -" + str(streak * 3) + " points!\n"
            points_add -= streak * 6
            late_status = 1
            message += name + "'s streak prevails to " + str(streak + 1) + "\n"

    #Symphony
    if points >= min + 50 and (done == 1 or done == 2):
        points_add -= 10
        message += "Symphony kicked in! -10 point\n"
    #Requium
    if points >= min + 35 and done == 1:
        points_add -= 20
        message += "Requium is active! -20 point\n"
    message = name + " has slept with " + str(points_add) + " points!\n" + message
    return (points_add, message, late_status)

def count_streak(user: Person, a: int):
    if a == 1 :
            put(user, "streak", get(user, "streak") + 1)
    elif a == -1:
            put(user, "streak", 0)

def is_late(t1: tuple[Person, int], t2: tuple[Person, int]) -> int:
    return on_time(t1[1], t2[1]) - on_time(t2[1], t1[1])

comp = functools.cmp_to_key(is_late)

def flatten_points(day: int = get_day()) -> None:
    print("A NEW DAY!\n")
    places: list[tuple[Person, int]] = []
    others: list[tuple[Person, int]] = []
    for v in users.values():
        t = get_time(v, day)
        if t[2]:
            v.late = True
        if t[0] != -10 and not t[1]:
            places.append((v, t[0]))
        else:
            others.append((v, t[0]))

    places.sort(key=comp)
    for i in range(0, len(places)):
        pts = calculate_points(places[i][0], i + 1, "", places[i][1])
        set_points(places[i][0], pts[0], day)
        count_streak(places[i][0], pts[2])
        put(places[i][0], "points", get(places[i][0], "points") + pts[0])
        places[i][0].late = False
    for i in range(0, len(others)):
        if others[i][1] == -10:
            #print("DEAD: " +others[i][0].name)
            set_points(others[i][0], default_points, day)
            put(others[i][0], "points", get(others[i][0], "points") + default_points)
            count_streak(others[i][0], -1)
        else:
            #print("FILL: " +others[i][0].name)
            pts = calculate_points(others[i][0], len(others) + 1, "", others[i][1])
            set_points(others[i][0], pts[0], day)
            put(others[i][0], "points", get(others[i][0], "points") + pts[0])
            count_streak(others[i][0], -1)
        others[i][0].late = False
    

def flatten_all():
    
    for v in users.values():
        put(v, "streak", 0)
        put(v, "points", 0)
    for i in range(1, get_day()):
        flatten_points(i)
    save()


#initial setup
load_dotenv()
if not testing:
    flatten_all()

for v in users.values():
    track[cell(v.column, get_day())].value = "---"

setup()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
#setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

#responces
print("Listening")
save()


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
        if input == "gn" and not slept(user):
            done += 1
            user.place = done
            a = calculate_points(user, done, name, seconds)
            put(user, "today", seconds)
            user.today = seconds
            set_time(user, seconds)

            s = a[1]
            count_streak(user, a[2])
            return s

        if input == "gn" and slept(user):
            return "You already gn'd fool"

        #Late ticket
        if input == "late":
            user.late = True
            return name + " uses a saving grace. Night crawlers will not affect them"
        
        if input == "file":
            return "!!FILE!!"

        #Fill in time for yesterday
        if input[:4] == "fill" and get_time(user, get_day() - 1)[0] == -10 and to_number(input[5:]):
            set_time(user, input[5:], True, get_day() - 1)
            return name + " has signaled their correct sleep time. Their points was adjusted by " + str(a)
        if input[:4] == "fill" and not user.last_late:
            return "You wern't late last night. Go drink sulfuric acid"
        #List stats
        if input == "stats" or input == "stat":
            r = ""
            for v in users.values():
                r += v.name + ": " + str(get(v, "points")) + " pts and " + str(get(v, "graces")) + " graces and a "  + str(get(v, "streak")) + " streak!\n" 
            return r
        #Make exception
        if input[:6] == "except":
            t = input[7:]
            t = t.split(" ")
            if len(t) == 2 and (str.isdigit(t[1]) or str.isdigit(t[1][1:]) and t[1][0] == "-") and users[t[0]]:
                n: str = t[0]
                p: int = int(t[1])
                put(users[n], "points", get(users[n], "points") + p)
                set_points(users[n], get_points(v, get_day() - 1) + p, get_day() - 1)
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
            v.late = False
            v.today = -10
            put(v, "today", -10)
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
    if int(time.time()) % 86400 > to_number(dead_time) and int(time.time()) % 86400 < to_number(dead_time) + 10 :
        update_charts()
    elif int(time.time()) % 86400 == to_number(night_crawler):
        await warn_night()
    else:
        reset_charts()
    if random.randint(0, 500000) == 3:
        await funny()

if not testing:
    #print("Server up")
    #server = HTTPServer(("0.0.0.0", 8000), RequestHandler)
    #server.serve_forever()
    pass



def worker():
    print("SERVER UP")
    from http.server import HTTPServer, BaseHTTPRequestHandler
    class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):

        def do_GET(self):
            try:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
            except:
                self.send_response(404)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b'404 - Not Found')
                    
    httpd = HTTPServer(('', 8000), SimpleHTTPRequestHandler)
    httpd.serve_forever()
thread = threading.Thread(target=worker)
thread.start()
thread.join()






#timer_thread = threading.Thread(target=wrap_timer)
#timer_thread.start()
#asyncio.run(timer())
def main() -> None:
    if not testing:
        client.run(token = TOKEN)
    
if __name__ == '__main__':
   main()

