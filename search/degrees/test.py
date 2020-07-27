import csv
import sys
from queue import Queue
from util import Node, QueueFrontier

names = {}
people = {}
movies = {}

def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass

def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = "small" #sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")
    #print(names)
    #print(people)
    #print(movies)
    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)
    #print(path)
    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    Queue = QueueFrontier()
    explored_state = set()
    source_node = Node(source, None, None)
    Queue.add(source_node)

    while not Queue.empty() and target not in explored_state:
        node = Queue.remove()
        explored_state.add(node.state)
        for action, state in neighbors_for_person(node.state):
            if not Queue.contains_state(state) and state not in explored_state:
                child = Node(state, node, action)
                if child.state == target:
                    path = []
                    while child.parent is not None:
                        path.insert(0,(child.action, child.state))
                        child = child.parent
                    return path
                else:
                    Queue.add(child)
    if len(explored_state)==0:
        return None
    """parents = find_path(source, target)
    #print(parents)
    path = []
    for i,j in parents.items():
        ids= [(k,v) for k,v in neighbors_for_person(j) if v==i][0]
        path.append(ids)
    
    return path    

def find_path(source, target):
    Q = Queue()
    parents = {}
    source_node = Node(source, None, people[source]["movies"])
    Q.put(source_node)
    while not Q.empty() and target not in parents:
        node = Q.get()
        for movie in node.action:
            for id in movies[movie]["stars"]:
                if id not in parents:
                    Q.put(Node(id, node.state, people[id]["movies"]))
                    parents[id]=node.state
    return parents"""

def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors

if __name__ == "__main__":
    main()
