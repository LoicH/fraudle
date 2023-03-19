from flask import Flask, render_template, redirect, url_for, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import os
import logging
import uuid
import main

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

# Flask-WTF requires an encryption key - the string can be anything
app.config["SECRET_KEY"] = "C2HWGVoMGfNTBsrYQg8EcMrdTimkZfAb"
app.config["UPLOAD_FOLDER"] = "data"
Bootstrap(app)

N_LETTERS = 5


class GuessForm(FlaskForm):
    guess = StringField("Your guess  ", validators=[DataRequired()])
    submit = SubmitField("Submit")


def validate_guess(s):
    return len(s) == N_LETTERS


def get_temp_filename(file_id):
    return f"words_{file_id}.txt"


def get_temp_filepath(file_id):
    filename = get_temp_filename(file_id)
    return os.path.join(app.config["UPLOAD_FOLDER"], filename)


def write_temp_file(file_id, words):
    filepath = get_temp_filepath(file_id)
    with open(filepath, "w") as fp:
        fp.write("\n".join(words))
    return


def read_temp_file(file_id):
    filepath = get_temp_filepath(file_id)
    return main.load_corpus(filepath)


@app.route("/", methods=["GET", "POST"])
@app.route("/fr", methods=["GET", "POST"])
def play():
    if "id" not in session:
        session["id"] = str(uuid.uuid4())
        logging.info(f"New game with id {session['id']}")
        try:
            candidates = main.load_corpus(f"data/mots_fr_{N_LETTERS}.txt")
        except FileNotFoundError as e:
            return str(e)
        write_temp_file(session["id"], candidates)
    else:
        logging.info(f"Continuing game with id {session['id']}")
        candidates = read_temp_file(session["id"])

    form = GuessForm()
    message = "message"
    if form.validate_on_submit():
        guess = form.guess.data.upper()
        logging.info(f"Guess = {guess}")
        if validate_guess(guess):
            form.guess.data = ""
            message = "valid guess"
            display, candidates = main.play_round(guess, candidates)
            write_temp_file(session["id"], candidates)
            if "guesses" in session:
                session["guesses"].append(guess)
                session["display"].append(display)
                # Flagging the session as modified because a mutable object is changed
                session.modified = True
            else:
                session["guesses"] = [guess]
                session["display"] = [display]
        else:
            logging.info(f"Invalid guess: {guess}")
            message = "invalid guess"
    message += f"\n{len(candidates)} words"
    return render_template(
        "index.html",
        form=form,
        message=message,
        guesses=session.get("guesses"),
        display=session.get("display"),
    )


@app.route("/reset")
def reset():
    if "id" in session:
        file_id = session.get("id")
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], get_temp_filename(file_id))
        try:
            os.remove(filepath)
        except FileNotFoundError:
            pass

    session.clear()
    return redirect(url_for("play"))


@app.route("/en")
def hello():
    return "<p>Hello!</p>"
