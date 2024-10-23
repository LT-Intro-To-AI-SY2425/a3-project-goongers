import os
import requests
from dotenv import load_dotenv
from typing import List, Callable, Any

load_dotenv()
OMDB_API_KEY = os.getenv('OMDB_API_KEY')
BASE_URL = "http://www.omdbapi.com/"

# utility function to make requests to omdb api shizzzz
def fetch_movie_data(params: dict) -> dict:
    params['apikey'] = OMDB_API_KEY
    response = requests.get(BASE_URL, params=params)
    print(response.json())
    return response.json() if response.status_code == 200 else None

def title_by_year(matches: List[str]) -> List[str]:
    year = matches[0]
    params = {'y': year, 'type': 'movie'}
    data = fetch_movie_data(params)
    
    return [data['Title']] if data and data['Response'] == 'True' else ['No answers']

def title_by_year_range(matches: List[str]) -> List[str]:
    start_year, end_year = matches[0], matches[1]
    results = []
    for year in range(int(start_year), int(end_year) + 1):
        params = {'y': str(year), 'type': 'movie'}
        data = fetch_movie_data(params)
        if data and data['Response'] == 'True':
            results.append(data['Title'])
    return results if results else ['No answers']

def title_before_year(matches: List[str]) -> List[str]:
    year = int(matches[0])
    results = []
    for current_year in range(1900, year):
        params = {'y': str(current_year), 'type': 'movie'}
        data = fetch_movie_data(params)
        if data and data['Response'] == 'True':
            results.append(data['Title'])
    return results if results else ['No answers']

def title_after_year(matches: List[str]) -> List[str]:
    year = int(matches[0])
    results = []
    for current_year in range(year + 1, 2024):
        params = {'y': str(current_year), 'type': 'movie'}
        data = fetch_movie_data(params)
        if data and data['Response'] == 'True':
            results.append(data['Title'])
    return results if results else ['No answers']

def director_by_title(matches: List[str]) -> List[str]:
    title = " ".join(matches)
    params = {'t': title}
    data = fetch_movie_data(params)
    return [data['Director']] if data and data['Response'] == 'True' else ['No answers']

def title_by_director(matches: List[str]) -> List[str]:
    director = " ".join(matches)
    params = {'s': director, 'type': 'movie'}
    data = fetch_movie_data(params)
    return [data['Title']] if data and data['Response'] == 'True' else ['No answers']

def actors_by_title(matches: List[str]) -> List[str]:
    title = " ".join(matches)
    params = {'t': title}
    data = fetch_movie_data(params)
    return data['Actors'].split(", ") if data and data['Response'] == 'True' else ['No answers']

def year_by_title(matches: List[str]) -> List[int]:
    title = " ".join(matches)
    params = {'t': title}
    data = fetch_movie_data(params)
    return [int(data['Year'])] if data and data['Response'] == 'True' else ['No answers']

def title_by_actor(matches: List[str]) -> List[str]:
    actor = " ".join(matches)
    params = {'s': actor, 'type': 'movie'}
    data = fetch_movie_data(params)
    return [data['Title']] if data and data['Response'] == 'True' else ['No answers']

def bye_action(dummy: List[str]) -> None:
    raise KeyboardInterrupt

# Pattern-action list for the query system
pa_list: List[tuple] = [
    (str.split("what movies were made in _"), title_by_year),
    (str.split("what movies were made between _ and _"), title_by_year_range),
    (str.split("what movies were made before _"), title_before_year),
    (str.split("what movies were made after _"), title_after_year),
    (str.split("who directed %"), director_by_title),
    (str.split("what movies were directed by %"), title_by_director),
    (str.split("who acted in %"), actors_by_title),
    (str.split("when was % made"), year_by_title),
    (str.split("in what movies did % appear"), title_by_actor),
    (["bye"], bye_action),
]

def match(pattern: List[str], source: List[str]) -> List[str]:
    """Match pattern to source using placeholders % and _."""
    sind = 0
    pind = 0
    result = []

    while pind != len(pattern) or sind != len(source):
        if pind == len(pattern):
            return None
        elif pattern[pind] == "%":
            if pind == (len(pattern) - 1):
                return result + [" ".join(source[sind:])]
            accum = ""
            pind += 1
            while pattern[pind] != source[sind]:
                accum += " " + source[sind]
                sind += 1
                if sind >= len(source):
                    return None
            result.append(accum.strip())
        elif sind == len(source):
            return None
        elif pattern[pind] == "_":
            result += [source[sind].strip()]
            pind += 1
            sind += 1
        elif pattern[pind] == source[sind]:
            pind += 1
            sind += 1
        else:
            return None
    return result

def search_pa_list(src: List[str]) -> List[str]:
    for pattern, action in pa_list:
        result = match(pattern, src)
        if result is not None:
            answers = action(result)
            return answers if answers else ["No answers"]
    return ["I don't understand"]

def query_loop() -> None:
    print("Welcome to the movie database")
    while True:
        try:
            query = input("Your query? ").replace("?", "").lower().split()
            answers = search_pa_list(query)
            for ans in answers:
                print(ans)
        except (KeyboardInterrupt, EOFError):
            break
    print("da")

if __name__ == "__main__":
    query_loop()
