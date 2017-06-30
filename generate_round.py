import sys
import os
import json
import shutil
import random

data_file_name = "data.json"
data = {}

def is_int(string):

    try:
        int(string)
        return True
    except ValueError:
        return False

def add_user():

    global data

    print("Enter user's name")
    new_user = input("> ")

    for user in data["users"]:
        if user.lower() == new_user.lower():
            print("User already exists")
            return

    data["users"].append(new_user)

def delete_user():

    global data

    print_users()

    print("Enter user's name (or number)")

    user_to_delete = input("> ")

    if is_int(user_to_delete):
        user_to_delete_index = int(user_to_delete)
        if user_to_delete_index < 0 or user_to_delete_index >= len(data["users"]):
            user_to_delete_index = None
    else:
        user_to_delete_index = None

        for user_index in range(len(data["users"])):
            user = data["users"][user_index]
            if user.lower() == user_to_delete.lower():
                user_to_delete_index = user_index
                break

    if user_to_delete_index is None:
        print("User doesn't exist")
    else:
        del data["users"][user_to_delete_index]

def get_user_mapping():

    global data

    user_mapping = {}

    for user in data["users"]:
        user_mapping[user] = set()

        for round in data["rounds"]:
            for table_number, pair in round.items():
                if user in pair:
                    for round_user in pair:
                        user_mapping[user].add(round_user)

    return user_mapping

def generate_round():

    global data

    user_mapping = get_user_mapping()

    #print("Current user mapping:")
    #print(user_mapping)

    num_solo_users = len(data["users"])
    allowable_num_solo_users = 1

    num_iterations_tried = 0
    max_num_iterations_before_giving_up = 1000

    while num_solo_users > allowable_num_solo_users:

        if num_iterations_tried >= max_num_iterations_before_giving_up:
            num_iterations_tried = 0
            allowable_num_solo_users += 1
            continue

        num_solo_users = 0

        unassigned_users = list(data["users"])

        round = {}

        table_number = 1

        while len(unassigned_users) > 0:

            #print("Generating assignment for table %i" % table_number)

            user_index = random.randint(0, len(unassigned_users) - 1)
            user = unassigned_users[user_index]

            del unassigned_users[user_index]

            #print("Finding partner for %s" % user)

            possible_partners = list(unassigned_users)
            partner_index = None

            while partner_index == None and len(possible_partners) > 0:
                partner_index = random.randint(0, len(possible_partners) - 1)
                partner = possible_partners[partner_index]

                #print("Checking if %s is a possible match for %s" % (partner, user))

                del possible_partners[partner_index]

                if partner in user_mapping[user]:
                    #print("%s has already been paired with %s" % (user, partner))
                    partner_index = None

            if partner_index == None:
                #print("No possible match for %s, sitting this one out" % (user))
                num_solo_users += 1
                round[table_number] = [user]
            else:
                #print("Assigning %s to %s at table %i" % (user, partner, table_number))
                round[table_number] = [user, partner]
                del unassigned_users[unassigned_users.index(partner)]


            table_number += 1

        num_iterations_tried += 1

    print_round(round)
    create_round_table(round, len(data["rounds"]) + 1)

    data["rounds"].append(round)

def print_round(round):

    for table_number, pair in round.items():
        if len(pair) > 1:
            print("%i: %s, %s" % (table_number, pair[0], pair[1]))
        else:
            print("%i: %s" % (table_number, pair[0]))

def create_round_table(round, round_number):

    html = """<html><table border="1">"""
    html += "<h1>Round {}</h1>".format(round_number)
    html += "<tr><th>Table</th><th>Person 1</th><th>Person 2</th></tr>"


    for table_number, pair in round.items():
        html += "<tr><td>{}</td>".format(table_number)
        html += "<td>{}</td>".format(pair[0])

        if len(pair) > 1:
            html += "<td>{}</td>".format(pair[1])
        else:
            html += "<td></td>"

        html += "</tr>"

    html += "</table></html>"

    html_file = open("round.html", "w")

    html_file.write(html)

    html_file.close()

def trash_round():

    global data

    del data["rounds"][-1]

def print_users():

    global data

    for user_index in range(len(data["users"])):
        user = data["users"][user_index]
        print("%i: %s" % (user_index, user))

def clear_rounds():

    global data

    data["rounds"] = []

def print_menu():
    print("")
    print("(A)dd user")
    print("(C)lear rounds")
    print("(D)elete user")
    print("(G)enerate round")
    print("(P)rint users")
    print("(T)rash round")
    print("(Q)uit")

def main():

    global data

    if os.path.isfile(data_file_name):
        data_file = open(data_file_name, "r")
        data = json.load(data_file)
        data_file.close()
    else:
        data = {}
        data["users"] = []
        data["rounds"] = []

    while True:

        print_menu()
        line = input('> ')
        if line.lower() == "a":
            add_user()
        elif line.lower() == "d":
            delete_user()
        elif line.lower() == "g":
            generate_round()
        elif line.lower() == "p":
            print_users()
        elif line.lower() == "q":
            break
        elif line.lower() == "c":
            clear_rounds()
        elif line.lower() == "t":
            trash_round()
        else:
            print("Invalid input")

    data_file = open(data_file_name, "w")
    json.dump(data, data_file, indent=4)
    data_file.close()


if __name__ == "__main__":
    main()