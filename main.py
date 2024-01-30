import argparse
import datetime
import json
import os
import requests
import sys
import pandas as pd

CACHE_FILE = "cache.json"


def search(query, include_world=False):
    # Check if the query is already in the cache
    cache_data = load_cache()
    numOfSearches = cache_data["numOfSearches"]
    if query in cache_data:
        cache_data["numOfSearches"] += 1
        print_result(cache_data[query], include_world, cache_data["numOfSearches"])
        save_cache(cache_data)
        return
    result = get_character_data(query)
    if result["result"]==[]:
        print("The force is not strong within you")
        cache_data["numOfSearches"] += 1
        save_cache(cache_data)
        print(f"Number of searches: {cache_data['numOfSearches']}")
        print(f"You searched at: {datetime.datetime.now()}")
        return

    # Cache the result
    # print(result)
    result["Homeworld"] = get_world_data(
            result["result"][0]["properties"]["homeworld"])


    cache_data[query] = {"result": result,
                         "cached_at": str(datetime.datetime.now())}
    cache_data["numOfSearches"] +=1
    save_cache(cache_data)
    print_result(result, include_world, cache_data["numOfSearches"])


def print_result(response, include_world, numOfSearches):
    result = response['result']
    properties = 0
    homeworld  = 0
    if isinstance(result, list):
        properties = result[0]["properties"]
        homeworld = response["Homeworld"]
    else:
        properties = result["result"][0]["properties"]
        homeworld = result["Homeworld"]

    name = properties['name']
    height = properties['height']
    birth_year = properties['birth_year']
    mass = properties['mass']
    # Displaying the extracted information
    print("Character Info\n----------------")
    print(f"Name: {name}")
    print(f"Height: {height} cm")
    print(f"Mass: {mass} kg")
    print(f"Birth Year: {birth_year}")
    if include_world:
        print("\nHomeworld\n----------------")
        print(f"Name: {homeworld['result']['properties']['name']}")
        print(f"Population: {homeworld['result']['properties']['population']}")

    print("----------------")
    print(f"Number of searches: {numOfSearches}")
    print(f"You searched at: {datetime.datetime.now()}")


def load_cache():
    try:
        with open(CACHE_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return { "numOfSearches": 0 }


def save_cache(cache_data):
    with open(CACHE_FILE, "w") as file:
        json.dump(cache_data, file)


def clean_cache():
    if os.path.exists(CACHE_FILE):
        os.remove(CACHE_FILE)
        print("Removed cache")
    else:
        print("No cache found")


def get_world_data(world_url):
    try:
        response = requests.get(world_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse and print the response data
            data = response.json()
            return data
        else:
            print(
                f"Error: Unable to fetch data from API. Status code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Error: {e}")


def get_character_data(character):
    try:
        # Make a GET request to the API
        api_url = "https://www.swapi.tech/api/people/?name=" + character
        response = requests.get(api_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Parse and print the response data
            data = response.json()
            return data
        else:
            print(
                f"Error: Unable to fetch data from API. Status code: {response.status_code}")

    except requests.RequestException as e:
        print(f"Error: {e}")


def main():
    lengthOfArgs = len(sys.argv)
    action = ""
    if lengthOfArgs == 3:
        if sys.argv[1] == "search":
            action = "search"
            search(sys.argv[2])
        elif sys.argv[1] == "cache":
            action = "cache"
            if sys.argv[2] == "--clean":
                clean_cache()
            else:
                print("Invalid command for 'cache' action.")
    elif lengthOfArgs == 4:
        if sys.argv[1] == "search":
            action = sys.argv[2]
            search(action, True)
        else:
            print("Invalid command for 'search' action with world option.")

    # elif args.action == "cache":
    #     if args.query == "--clean":
    #         clean_cache()
    #     else:
    #         print("Invalid command for 'cache' action.")
    # else:
    #     print("Invalid command")
if __name__ == "__main__":
    main()
