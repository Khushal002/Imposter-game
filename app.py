import streamlit as st
import random
import string
import time
import json
import os

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Imposter Game",
    page_icon="🕵️",
    layout="centered"
)

# ---------------- CUSTOM CSS ----------------
st.markdown(
    """
    <style>

    .stButton button {
        background-color: #7c3aed;
        color: white;
        border-radius: 10px;
        border: none;
        height: 3em;
        width: 100%;
        font-size: 16px;
        font-weight: bold;
    }

    .stButton button:hover {
        background-color: #6d28d9;
        color: white;
    }

    </style>
    """,
    unsafe_allow_html=True
)

# ---------------- WORD PAIRS ----------------
word_pairs = [

    ("Forest", "Jungle"),
    ("Ocean", "Sea"),
    ("Teacher", "Professor"),
    ("Laptop", "Computer"),
    ("Bread", "Cake"),
    ("Coffee", "Tea"),
    ("Pizza", "Burger"),
    ("Football", "Basketball"),
    ("Tiger", "Lion"),
    ("Phone", "Tablet"),

]

# ---------------- DATABASE FILE ----------------
DB_FILE = "rooms.json"

if not os.path.exists(DB_FILE):

    with open(DB_FILE, "w") as f:
        json.dump({}, f)

# ---------------- LOAD ROOMS ----------------
def load_rooms():

    with open(DB_FILE, "r") as f:
        return json.load(f)

# ---------------- SAVE ROOMS ----------------
def save_rooms(rooms):

    with open(DB_FILE, "w") as f:
        json.dump(rooms, f)

# ---------------- ASSIGN WORDS ----------------
def assign_words(players):

    pair = random.choice(word_pairs)

    common_word = pair[0]
    imposter_word = pair[1]

    imposter = random.choice(players)

    assignments = {}

    for player in players:

        if player == imposter:
            assignments[player] = imposter_word

        else:
            assignments[player] = common_word

    return assignments, imposter

# ---------------- SESSION STATE ----------------
if "joined" not in st.session_state:
    st.session_state.joined = False

if "current_player" not in st.session_state:
    st.session_state.current_player = ""

if "current_room" not in st.session_state:
    st.session_state.current_room = ""

# ---------------- TITLE ----------------
st.title("🕵️ Imposter Game")

st.write("Play with friends on different devices.")

st.divider()

# ---------------- CREATE ROOM ----------------
st.subheader("Create Room")

if st.button("Create New Room"):

    rooms = load_rooms()

    room_code = ''.join(
        random.choices(string.ascii_uppercase, k=4)
    )

    while room_code in rooms:

        room_code = ''.join(
            random.choices(string.ascii_uppercase, k=4)
        )

    rooms[room_code] = {
        "players": [],
        "assignments": {},
        "imposter": "",
        "started": False,
        "ended": False,
        "votes": {},
        "winner": "",
        "last_result": ""
    }

    save_rooms(rooms)

    st.success(f"Room Created: {room_code}")

# ---------------- JOIN ROOM ----------------
st.subheader("Join Room")

room_code = st.text_input(
    "Enter Room Code"
).upper()

player_name = st.text_input(
    "Enter Your Name"
)

if st.button("Join Game"):

    rooms = load_rooms()

    player_name = player_name.strip()

    if room_code == "":
        st.error("Enter room code")

    elif player_name == "":
        st.error("Enter player name")

    elif room_code not in rooms:
        st.error("Room does not exist")

    else:

        if player_name not in rooms[room_code]["players"]:

            rooms[room_code]["players"].append(
                player_name
            )

            save_rooms(rooms)

        st.session_state.joined = True

        st.session_state.current_player = player_name

        st.session_state.current_room = room_code

        st.success(
            f"{player_name} joined room {room_code}"
        )

# ---------------- ROOM DATA ----------------
if st.session_state.joined:

    rooms = load_rooms()

    room_code = st.session_state.current_room

    player_name = st.session_state.current_player

    room = rooms[room_code]

    # ---------------- KICKED PLAYER CHECK ----------------
    if player_name not in room["players"]:

        st.error("You were kicked from the game.")

        st.session_state.joined = False

        st.stop()

    # ---------------- SHOW PLAYERS ----------------
    st.subheader("Players")

    for player in room["players"]:

        st.write(f"✅ {player}")

    # ---------------- START GAME ----------------
    if len(room["players"]) >= 3:

        if not room["started"] and not room["ended"]:

            if st.button("Start Game"):

                assignments, imposter = (
                    assign_words(room["players"])
                )

                room["assignments"] = assignments

                room["imposter"] = imposter

                room["started"] = True

                room["ended"] = False

                room["votes"] = {}

                room["winner"] = ""

                room["last_result"] = ""

                save_rooms(rooms)

                st.success("Game Started!")

    else:

        st.warning("Need at least 3 players")

    # ---------------- REVEAL WORD ----------------
    if room["started"]:

        st.divider()

        st.subheader("Reveal Your Secret Word")

        if st.button("Reveal My Word"):

            secret_word = (
                room["assignments"][player_name]
            )

            placeholder = st.empty()

            placeholder.success(
                f"Your word is: {secret_word}"
            )

            time.sleep(5)

            placeholder.empty()

            st.info("Word hidden again")

    # ---------------- VOTING ----------------
    if room["started"]:

        st.divider()

        st.subheader("Vote To Kick A Player")

        alive_players = [
            p for p in room["players"]
            if p != player_name
        ]

        voted_player = st.selectbox(
            "Who should be kicked?",
            alive_players,
            key="vote_box"
        )

        if player_name in room["votes"]:

            st.success(
                f"You voted against "
                f"{room['votes'][player_name]}"
            )

        else:

            if st.button("Submit Vote"):

                room["votes"][
                    player_name
                ] = voted_player

                save_rooms(rooms)

                st.success(
                    f"You voted against "
                    f"{voted_player}"
                )

    # ---------------- VOTE COUNT ----------------
    if room["started"]:

        total_votes = len(room["votes"])

        total_players = len(room["players"])

        st.info(
            f"Votes: {total_votes}/{total_players}"
        )

    # ---------------- PROCESS VOTES ----------------
    if room["started"]:

        total_votes = len(room["votes"])

        total_players = len(room["players"])

        # everyone voted
        if total_votes == total_players:

            vote_count = {}

            for voted_player in (
                room["votes"].values()
            ):

                if voted_player not in vote_count:

                    vote_count[voted_player] = 0

                vote_count[voted_player] += 1

            highest_votes = max(
                vote_count.values()
            )

            top_players = []

            for player, count in (
                vote_count.items()
            ):

                if count == highest_votes:

                    top_players.append(player)

            # ---------------- TIE ----------------
            if len(top_players) > 1:

                room["last_result"] = (
                    "Tie vote! Nobody was kicked."
                )

            else:

                kicked_player = top_players[0]

                room["last_result"] = (
                    f"{kicked_player} was kicked out!"
                )

                room["players"].remove(
                    kicked_player
                )

                imposter = room["imposter"]

                # ---------------- PLAYERS WIN ----------------
                if kicked_player == imposter:

                    room["started"] = False

                    room["ended"] = True

                    room["winner"] = "Players"

                else:

                    remaining_players = len(
                        room["players"]
                    )

                    # ---------------- IMPOSTER WIN ----------------
                    if remaining_players <= 2:

                        room["started"] = False

                        room["ended"] = True

                        room["winner"] = "Imposter"

            # reset votes
            room["votes"] = {}

            save_rooms(rooms)

    # ---------------- ROUND RESULT ----------------
    if room["last_result"] != "":

        st.warning(room["last_result"])

    # ---------------- FINAL RESULT ----------------
    if room["ended"]:

        st.divider()

        if room["winner"] == "Players":

            st.success("Players Win!")

        else:

            st.error("Imposter Wins!")

        st.info(
            f"The imposter was: "
            f"{room['imposter']}"
        )

    # ---------------- NEW GAME ----------------
    if room["ended"]:

        if st.button("New Game"):

            assignments, imposter = (
                assign_words(room["players"])
            )

            room["assignments"] = assignments

            room["imposter"] = imposter

            room["started"] = True

            room["ended"] = False

            room["votes"] = {}

            room["winner"] = ""

            room["last_result"] = ""

            save_rooms(rooms)

            st.success("New Game Started!")

    # ---------------- LEAVE ROOM ----------------
    st.divider()

    if st.button("Leave Room"):

        st.session_state.joined = False

        st.session_state.current_player = ""

        st.session_state.current_room = ""

        st.success("You left the room.")