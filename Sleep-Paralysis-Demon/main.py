from typing import Final, Dict
import os
from dotenv import load_dotenv
from discord import Intents, Client, Message

from person import Person
import time
import threading

import openpyxl 
import random


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
print(day)
for v in users.values():
    v.points = record[ chr(v.column + ord('A') - 1) + str(day + 5) ].value
    v.lates = record[ chr(v.column + ord('A') - 1) + "2" ].value
    v.last_late = True if record[ chr(v.column + ord('A') - 1) + "3" ].value == 1 else False

#initial setup
load_dotenv()
TOKEN: Final[str] = os.getenv('DISCORD_TOKEN')
#setup
intents: Intents = Intents.default()
intents.message_content = True
client: Client = Client(intents=intents)

#responces

night_crawler: int = ((0 + 4) * 60 * 60 + 45 * 60)% 86400
four_am: int = ((4 + 4) * 60 * 60 )% 86400
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
            user.today = done
            done += 1
            #Night crawler
            if seconds > night_crawler and seconds < four_am and not user.late:
                user.today += int((seconds - night_crawler)/(interval)) + 1
            #Symphony
            if user.points >= min + 20 and (done == 1 or done == 2):
                user.today -= 1
            #Requium
            if user.points >= min + 15 and done == 1:
                user.today -= 1
            
            return name + " has slept with " + str(user.today) + " points"
        if input == "gn" and user.today != -10:
            return "You already gn'd fool"
        #Late ticket
        if input == "late":
            user.late = True
            return name + " uses a saving grace. Night crawlers will not affect them"
        
        #Fill in time for yesterday
        if input[:5] == "fill" and user.last_late:
            t = input[5:]
            if str.isdigit(t[4:6]) and str.isdigit(t[7:9]):
                t1 = int(t[4:6])
                t2 = int(t[7:9])
                a = 0
                if t1 >= 1 and t1 < 4:
                    a += 2 * t1
                    a += t2 > 30 and 1 or 0
                else:
                    a = 6
                a -= 1
                user.last_late = False
                record[ chr(v.column + ord('A') - 1) + str(day + 4) ] = user.points - a
                record[ chr(v.column + ord('A') - 1) + "2" ] = user.lates
                record[ chr(v.column + ord('A') - 1) + "3" ] = user.last_late and 1 or 0
                file.save("record.xlsx")
                return name + " has signaled their correct sleep time. Their points was adjusted"
       
        #List stats
        if input == "stats":
            r = ""
            for v in users.values():
                r += v.name + ": " + str(v.points) + " pts and " + str(v.lates) + " saving graces"   +"!\n" 
            return r

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
            return name + " revoked their gn!"
    return "You have killed me"

#message handling
async def send_message(message: Message, user_message: str) -> None:
    if not user_message:
        print("ERROR: NO MESSAGE") 
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
    client.get_channel(1260219510292611082).send(str)

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

@client.event
async def on_message(message: Message) -> None:
    if message.author == client.user:
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
    if not updated:
        updated = True
        day += 1
        for v in users.values():
            if v.today == -10:
                v.points + 10
            else:
                v.points + v.today
            v.lates = v.lates - v.late and 1 or 0
            record[ chr(v.column + ord('A') - 1) + str(day + 5) ] = v.points
            record[ chr(v.column + ord('A') - 1) + "2" ] = v.lates
            record[ chr(v.column + ord('A') - 1) + "3" ] = v.last_late and 1 or 0

        file.save("record.xlsx")
        for v in users.values():
            v.today = -10
            v.late = False
    
def reset_charts() -> None:
    updated = False
    nighted = False
    done = 0

async def warn_night() -> None:
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
            print("ERROR")

def timer() -> None:
    while True:
        if int(time.time()) % 86400 == ((4 + 4) * 60 * 60)% 86400 :
            update_charts()
        elif int(time.time()) % 86400 == night_crawler - 10 * 60:
            warn_night()
        else:
            reset_charts()
        if random.randint(0, 300000) == 3:
            funny()
        time.sleep(0.5)


timer_thread = threading.Thread(target=timer)
timer_thread.start()

def main() -> None:
    client.run(token = TOKEN)
    
if __name__ == '__main__':
   main()

