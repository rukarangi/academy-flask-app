from flask import Flask, request
import json

from db import DBSession
from models import Movie, Person, Vote

# Setup

app = Flask(__name__)

HOST = "0.0.0.0"
PORT = 8000

# GET methods

@app.route("/")
@app.route("/movies")
def hello():
    """
    Get list of all movies
    """
    movies = DBSession.query(Movie).order_by(Movie.name)

    json_data = {"movies": [movie.as_dict() for movie in movies]}
    return json.dumps(json_data)

@app.route("/people")
def list_people():
    """
    Get list of all people
    """
    people = DBSession.query(Person).order_by(Person.name)

    json_data = {"people": [person.as_dict() for person in people]}
    return json.dumps(json_data)

@app.route("/votes")
def list_votes():
    """
    Get list of all votes
    """
    votes = DBSession.query(Vote).order_by(Vote.id)

    json_data = {"votes": [vote.as_dict() for vote in votes]}
    return json.dumps(json_data)

# POST methods

@app.route("/vote/<int:person_id>/<int:movie_id>", methods=["POST"])
def cast_vote(person_id, movie_id):
    """
    Submit a vote from one user, check if duplicate
    """

    exists = DBSession.query(Vote).filter_by(person_id=person_id, movie_id=movie_id).first()

    if exists:
        result = {
            "result": "ERROR",
            "message": "This person has already voted for this movie."
        }
        return json.dumps(result), 409
    else:
        vote = Vote(person_id=person_id, movie_id=movie_id)
        DBSession.add(vote)
        DBSession.commit()
        result = {"result": "OK", "message": "Vote cast."}
        return json.dumps(result)

@app.route("/movie/add_movie", methods=["POST"])
def add_movie():
    content = request.json
    print(content)

    exists = DBSession.query(Movie).filter_by(name=content["name"]).first()

    if exists:
        result = {
            "result": "ERROR",
            "message": "This movie is already in the database."
        }
        return json.dumps(result), 409
    else:
        movie = Movie(name=content["name"], length=content["length"], category=content["category"])
        DBSession.add(movie)
        DBSession.commit()
        result = {"result": "OK", "message": "Movie added to database."}

        return json.dumps(result)

# DELETE methods

@app.route("/votes", methods=["DELETE"])
def delete_all_votes():
    """
    WARNING: will remove all votes cast
    """
    DBSession.query(Vote).delete()

    DBSession.commit()

    result = {"result": "OK", "message": "All votes have been deleted."}
    return json.dumps(result)

@app.route("/people/<int:person_id>/votes", methods=["DELETE"])
def delete_person_votes(person_id):
    """
    Delete all votes cast by a person
    """

    person = DBSession.query(Person).filter_by(id=person_id).first()

    if person:
        DBSession.query(Vote).filter_by(person_id=person_id).delete()
        DBSession.commit()
        result = {
            "result": "OK",
            "message": "All votes for person {} have been deleted.".format(person)
        }
        return json.dumps(result)
    else:
        result = {
            "result": "ERROR",
            "message": "Person with id {} does not exist.".formate(person_id)
        }
        return json.dumps(result), 404


app.run(host = HOST, port = PORT, debug = True)
