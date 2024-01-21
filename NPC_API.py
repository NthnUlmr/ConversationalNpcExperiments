# <GPLv3_Header>
## - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# \copyright
#                    Copyright (c) 2024 Nathan Ulmer.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# <\GPLv3_Header>

##
# \file NPC_API.py
#
# \author Nathan Ulmer
#
# \date \showdate "%A %d-%m-%Y"
#
# \brief Example of api calls that can be made by the AI. 

# say_to(message, "player") #This is an example of how I would speak to the player
# say_to("Hello", "player")
def say_to(message:str, target_person:str): # Say something to another character nearby
    person = getCharacter(target_person)  # returns reference to character specified by the given name string
    person.send(message) # Sends message that target person can see.

# give_to(item_name, count, "player") # This is an example of how to give the player a pint of cold ale
def give_to(item_name:str,count:int, target_person:str):
    person = getCharacter(target_person)  # returns reference to character specified by the given name string
    for i in range(len(count)):
        person.inventory.append(item_name)
    person.send(f"You received {item}!")   # Sends message that target person can see.

# request_from(item_name,count, "player") # This is an example of how to request money from the player for payment.
def request_from(item_name:str,count:int, target_person:str):
    true_count = 0
    person = getCharacter(target_person) # returns reference to character specified by the given name string
    for i in range(len(count)):
        if item_name in person.inventory:
            true_count = true_count + 1
            person.inventory.remove(item_name)
    if(true_count == count):
        person.send(f"You gave me {true_count} {item_name}. Thank you!")  # Sends message that target person can see.
    else:
        person.send(f"I'm sorry, you don't have enough {item_name}.")  # Sends message that target person can see.


# An example transaction with a player
# 1. Player asks for beer
say_to("We have cold ale here for {num} gold", "player") # 2. Describe the transaction to the player
request_from("gold_coin",num,"player") # 3. Request payment from the player
give_to("beer",1,"player") # 4. If the payment is valid, give the item to the player


# <GPLv3_Footer>
################################################################################
#                      Copyright (c) 2024 Nathan Ulmer.
################################################################################
# <\GPLv3_Footer>