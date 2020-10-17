#/usr/bin/env python3
import json
import csv
import requests
import gspread # use: pip install gspread --user
import os
import argparse
import shutil
from tempfile import NamedTemporaryFile
from datetime import datetime

# adding argument parser to script
parser = argparse.ArgumentParser()
parser.add_argument('-o', '--offset', const=20, default=0, type=int, help='an integer to set offset(default 0)', nargs='?')
parser.add_argument('-p', '--pagination', const=20, default=20, type=int, help='an integer to set pagination(default and max 20)', nargs='?')

args = parser.parse_args()

# validation data type of arguments, if not match the data type, exit
if args.offset and type(args.offset) is not int:
    exit(0)

if args.pagination and type(args.pagination) is not int:
    exit(0)

if args.pagination > 20:
    parser.error("Maximun pagination number is 20")


# getting all pokemons data from pokeapi
response_pokemons = requests.get("https://pokeapi.co/api/v2/pokemon?limit=" + str(args.pagination) + "&offset=" + str(args.offset))
pokemons = json.loads(response_pokemons.text)

# google drive/sheets credentials
credentials = "service_account.json"

# init session as a service account
gc = gspread.service_account(credentials)

# colums title list for csv file
titles = ["name", "url", "created_at", "modified_at"]
pokemons_list = []

# check if file doesn't exist (original should be if not, but since it is not completed I removed to avoid problems)
if not os.path.isfile("pokemons.csv"):

    # if it doesn't exist python will create it and open in write mode
    with open('pokemons.csv', 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)
    
        # write columns titles to file.
        writer.writerow(titles)
    
        for pokemon in pokemons["results"]:
            # append pokemon's info and current time to pokemons list.
            pokemons_list.append(pokemon["name"])
            pokemons_list.append(pokemon["url"])
            pokemons_list.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
            pokemons_list.append("No modifications yet")
    
            # write to file each row of pokemons.
            writer.writerow(pokemons_list)
            pokemons_list[:] = []


    # read the created file
    content = open('pokemons.csv', 'r').read()

    # updating the file on the google spreadsheet
    gc.import_csv('1a553WahTMARx9Wt8bUki9S2lRZvCzPDYnaa-ICbsRUk', content)
    exit(0)

else:
    pokemons_names = []
    # opening file to read its content
    f = open('pokemons.csv', 'r')

    # start reading from line 1, line 0 contains titles and we don't want to modify them
    lines = f.readlines()[1:]

    # getting pokemons names in file
    for line in lines:
        pokemons_names.append(line.split(',')[0])


    for pokemon in pokemons["results"]:
        # append pokemon's info and current time to pokemons list.
        pokemons_list.append(pokemon["name"])
        pokemons_list.append(pokemon["url"])
        pokemons_list.append(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))

        for pokemon in pokemons_names:
            # if the pokemon is on the pokemons list, then update the row
            if pokemon in pokemons_list:

                # opening file and temporary file to start updating rows
                filename = 'pokemons.csv'
                tempfile = NamedTemporaryFile(mode='w', delete=False) 
                
                # opening file in read mode
                with open(filename, 'r') as csvfile, tempfile:

                    # creating reader and writer. NOTE: the reader is created for the original file and
                    # the writer is created for the temporary file.
                    reader = csv.DictReader(csvfile, fieldnames=titles)
                    writer = csv.DictWriter(tempfile, fieldnames=titles)

                    # for each row in the reader...
                    for row in reader:

                        # if the row in name equals to the current pokemon, the update the row.
                        if row['name'] == pokemon:
                            print('Updating pokemon: ', row['name'])

                            # assigning values, name and created_at keep their value, url will be replaced by the url given by the API just in case it was modified
                            # if it wasn't, it will just put the same again. Finally the modification date will be the time now.
                            row['name'], row['url'], row['created_at'], row['modified_at'] = row['name'], pokemons_list[2], row['created_at'],  datetime.now().strftime("%d/%m/%Y %H:%M:%S") 

                        # creation of the row and writing the row to the file
                        row = {'name': row['name'], 'url': row['url'], 'created_at': row['created_at'], 'modified_at': row['modified_at'] }
                        writer.writerow(row)
                
                # move the tempfile wich has the modification to the original file
                shutil.move(tempfile.name, filename)

            # in case that the pokemon is not in the file, append the pokemon's information
            # IMPORTANT: I just reached the 3 hours limit and could implement this part of the script ====> :(
            #else:
            #    with open('pokemons.csv', 'a', newline='') as csv_file:
            #        writer = csv.writer(csv_file)
    
            #        pokemons_list.append("No modifications yet")
    
            #        # write to file each row of pokemons.
            #        writer.writerow(pokemons_list)
            #        pokemons_list[:] = []

        # clearing the list to continue with the next one
        pokemons_list[:] = []

    # read the created file
    content = open('pokemons.csv', 'r').read()

    # updating the file on the google spreadsheet
    gc.import_csv('1a553WahTMARx9Wt8bUki9S2lRZvCzPDYnaa-ICbsRUk', content)
    
      
    exit(0)

    


