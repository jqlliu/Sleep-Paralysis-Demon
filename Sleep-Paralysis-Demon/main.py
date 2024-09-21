from typing import Final, Dict
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from discord.ext import tasks
from person import Person
import time
import threading

import openpyxl 
import random

#import asyncio


days_cell: str = "M1"
file = openpyxl.load_workbook('record.xlsx')
record = file.active
users: Dict[str, Person] = {
    "hydrogenjack": Person("jack", 2),
    "beveornaut": Person("beaverly", 3),
    "c.jy.z": Person("catherine", 4),
    "sunsetsoul": Person("darren", 5),
    "the_fooled_one": Person("hanrick", 6),
}
day: int = record[ days_cell ].value

#Load info
def load_points(day: int):
    for v in users.values():
        v.points = int(record[ chr(v.column + ord('A') - 1) + str(day + 5) ].value)
        v.lates = int(record[ chr(v.column + ord('A') - 1) + "2" ].value)
        v.last_late = True if int(record[ chr(v.column + ord('A') - 1) + "3" ].value) == 1 else False

load_points(day)
#initial setup
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
#setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

#responces
print("Start")
night_crawler: int = ((0 + 4) * 60 * 60 + 45 * 60)% 86400
four_am: int = ((4 + 4) * 60 * 60)% 86400
interval: int = 30 * 60
done: int = 0

def get_response(input: str, message: Message) -> str:
    name: str = message.author.name
    input = str.lower(input)
    seconds: int = int(time.time()) % 86400
    user: Person = users[name]
    global done
    if user != None:
        min:int = -1
        for v in users.values():
            if v.points < min or min == -1:
                min = v.points
        #Gning
        if input == "gn" and user.today == -10:
            s = ""
            user.today = int(done)
            done += 1
            s += name + " was #" + str(done) + "!\n"
            #Night crawler
            if seconds > night_crawler and seconds < four_am and not user.late:
                a = int((seconds - night_crawler)/(interval)) + 1
                user.today += a
                s += "Night crawler attacked for " + str(int((seconds - night_crawler)/(interval)) + 1) + "points!\n"
            #Symphony
            if user.points >= min + 20 and (done == 1 or done == 2):
                user.today -= 1
                s += "Symphony kicked in! -1 point\n"
            #Requium
            if user.points >= min + 15 and done == 1:
                user.today -= 1
                s += "Requium kicked in! -1 point\n"
            s = name + " has slept with " + str(user.today) + " points!\n" + s
            return s

        if input == "gn" and user.today != -10:
            return "You already gn'd fool"
        #Late ticket
        if input == "late":
            user.late = True
            return name + " uses a saving grace. Night crawlers will not affect them"
        
        #Fill in time for yesterday
        if input[:4] == "fill" and user.last_late:
            t = input[5:]
            if str.isdigit(t[0:2]) and str.isdigit(t[3:5]):
                t1 = (int(t[0:2]) * 60 * 60 + int(t[3:5])*60)
                a = -6
                if t1 > night_crawler and t1 < four_am:
                    a += int((t1 - night_crawler)/interval) + 1
                user.last_late = False
                record[ chr(user.column + ord('A') - 1) + str(day + 5) ] = user.points + a
                user.points = user.points + a
                record[ chr(user.column + ord('A') - 1) + "3" ] = 0
                file.save("record.xlsx")
                return name + " has signaled their correct sleep time. Their points was adjusted"
        if input[:4] == "fill" and not user.last_late:
            return "You wern't late last night. Go drink sulfuric acid"
        #List stats
        if input == "stats":
            r = ""
            for v in users.values():
                r += v.name + ": " + str(v.points) + " pts and " + str(v.lates) + " saving graces"   +"!\n" 
            return r
        #Make exception
        if input[:6] == "except":
            t = input[7:]
            t = t.split(" ")
            if len(t) == 2 and (str.isdigit(t[1]) or str.isdigit(t[1][1:]) and t[1][0] == "-") and users[t[0]]:
                n: str = t[0]
                p: int = int(t[1])
                users[n].points += p
                return n + " has been executed (I mean excepted) by " + name + " for " + str(p) + " points! "
            else:
                return "Wrong parameters bozo"

        return "BAHH WHAT HAPPENED SOMETHIGN ERORRE D AHHHH"

def deleted(input: str, message: Message) -> str:
    name: str = message.author.name
    input = str.lower(input)
    user: Person = users[name]
    global done
    if user != None:
        #Gn deleted
        if input == ";gn" and user.today != -10:
            user.today = -10
            done -= 1
            return name + " revoked their gn! That fool. "
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
        day += 1
        
        done = 0
        for v in users.values():
            if v.today == -10:
                v.points += 10
                v.last_late = True
            else:
                v.points += v.today
            v.lates = v.lates - (v.late and 1 or 0)
            record[ chr(v.column + ord('A') - 1) + str(day + 5) ] = v.points
            record[ chr(v.column + ord('A') - 1) + "2" ] = v.lates
            record[ chr(v.column + ord('A') - 1) + "3" ] = v.last_late and 1 or 0
            record[ days_cell ] = day
        file.save("record.xlsx")
        for v in users.values():
            v.today = -10
            v.late = False
        print("update successful")
    
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
            await send("NIGHT CRAWLERS HERE IN 10 MINUTE. HIDE WHILE YOU STILL CAN")
        except Exception as e:
            print("ERROR")

async def funny() -> None:
        try:
            await send("BANANA")
        except Exception as e:
            print(e)
@tasks.loop(seconds = 0.5)
async def timer():
    if int(time.time()) % 86400 > four_am and int(time.time()) % 86400 < four_am + 10 :
        update_charts()
    elif int(time.time()) % 86400 == night_crawler - 10 * 60:
        await warn_night()
    else:
        reset_charts()
    if random.randint(0, 300000) == 3:
        await funny()


#timer_thread = threading.Thread(target=wrap_timer)
#timer_thread.start()
#asyncio.run(timer())
def main() -> None:
    client.run(token = TOKEN)
    
if __name__ == '__main__':
   main()

