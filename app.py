import streamlit as st
import random
from datetime import datetime
import pandas as pd
import time

# ----------------- Page config -----------------
st.set_page_config(page_title="Tic-Tac-Toe(AI)", layout="centered")

# ----------------- Theme Toggle -----------------
theme = st.sidebar.radio("🎨 Theme", ["Light", "Dark"], index=0)
if theme == "Dark":
    st.markdown("""
    <style>
    body, .stApp { background-color: #0e1117; color: white; }
    </style>
    """, unsafe_allow_html=True)

# ----------------- Emoji Symbol Options -----------------
EMOJIS = {"❌": "❌", "⭕": "⭕", "😺": "😺", "🐶": "🐶", "🌟": "🌟", "🔥": "🔥", " ": "⬜"}

# ----------------- Init session state -----------------
def init_state():
    defaults = {
        "board": [" "] * 9,
        "turn": "player1",
        "scores": {"player1": 0, "player2": 0, "draws": 0},
        "history": [],
        "player1_name": "Player 1",
        "player2_name": "Player 2",
        "symbols": {"player1": "❌", "player2": "⭕"},
        "streak": {"player1": 0, "player2": 0, "last_winner": None},
        "timer_start": None,
        "time_limit": 10,
        "winner": None
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ----------------- User Input -----------------
mode = st.sidebar.radio("🎮 Game Mode", ["Single Player", "Multiplayer"])
if mode == "Multiplayer":
    st.session_state.player1_name = st.sidebar.text_input("Player 1 Name", "Player 1")
    st.session_state.player2_name = st.sidebar.text_input("Player 2 Name", "Player 2")
else:
    st.session_state.player1_name = st.sidebar.text_input("Your Name", "Player")
    st.session_state.player2_name = "AI 🤖"

difficulty = st.sidebar.selectbox("🤖 AI Difficulty", ["Easy", "Medium", "Hard(Unbeatable)"], index=2)
st.session_state.symbols["player1"] = st.sidebar.selectbox("Player 1 Emoji", list(EMOJIS.keys()), index=0)
st.session_state.symbols["player2"] = st.sidebar.selectbox("Player 2 Emoji", list(EMOJIS.keys()), index=1)
st.session_state.time_limit = st.sidebar.slider("⏱️ Time Limit (sec)", 5, 30, 10)

# ----------------- Utility Functions -----------------
def check_winner(board, symbol):
    win_patterns = [[0,1,2],[3,4,5],[6,7,8],[0,3,6],[1,4,7],[2,5,8],[0,4,8],[2,4,6]]
    return any(all(board[i] == symbol for i in line) for line in win_patterns)

def is_full(board):
    return all(cell != " " for cell in board)

MAX_DEPTH = 4  # Limit minimax depth for speed
memo = {}

def board_to_tuple(board):
    return tuple(board)

def minimax_ab(board, depth, maximizing, ai, human, alpha, beta):
    if check_winner(board, ai):
        return 10 - depth
    elif check_winner(board, human):
        return depth - 10
    elif is_full(board):
        return 0

    if maximizing:
        max_eval = -float("inf")
        for i in range(9):
            if board[i] == " ":
                board[i] = ai
                eval = minimax_ab(board, depth + 1, False, ai, human, alpha, beta)
                board[i] = " "
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break  # beta cut-off
        return max_eval
    else:
        min_eval = float("inf")
        for i in range(9):
            if board[i] == " ":
                board[i] = human
                eval = minimax_ab(board, depth + 1, True, ai, human, alpha, beta)
                board[i] = " "
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break  # alpha cut-off
        return min_eval


def best_move(board, ai, human):
    best_score = -float("inf")
    move = None
    for i in range(9):
        if board[i] == " ":
            board[i] = ai
            score = minimax_ab(board, 0, False, ai, human, -float("inf"), float("inf"))
            board[i] = " "
            if score > best_score:
                best_score, move = score, i
    return move

def ai_move():
    board = st.session_state.board
    symbol, opponent = st.session_state.symbols["player2"], st.session_state.symbols["player1"]
    available = [i for i in range(9) if board[i] == " "]
    if difficulty == "Easy":
        move = random.choice(available)
    elif difficulty == "Medium":
        move = random.choice(available) if random.random() < 0.5 else best_move(board, symbol, opponent)
    else:
        move = best_move(board, symbol, opponent) or random.choice(available)
    board[move] = symbol

def render_board_snapshot(board):
    return ''.join([EMOJIS.get(c, c) + ("\n" if i % 3 == 2 else '') for i, c in enumerate(board)])

def play_sound(sfx):
    urls = {
        "win": "https://www.soundjay.com/button/sounds/button-4.mp3",
        "lose": "https://www.soundjay.com/button/sounds/button-10.mp3",
        "draw": "https://www.soundjay.com/button/sounds/button-3.mp3"
    }
    st.audio(urls.get(sfx, ""), format="audio/mp3", start_time=0)

# ----------------- Game UI -----------------
st.title("Tic-Tac-Toe(AI)")
turn_name = st.session_state.player1_name if st.session_state.turn == "player1" else st.session_state.player2_name
turn_emoji = "🟢" if st.session_state.turn == "player1" else "🔴"
st.markdown(f"### {turn_emoji} It's **{turn_name}**'s turn!")
st.markdown(f"**{st.session_state.player1_name} ({st.session_state.symbols['player1']}) vs {st.session_state.player2_name} ({st.session_state.symbols['player2']})**")

# Render Board
board = st.session_state.board
symbol_map = st.session_state.symbols
cols = st.columns(3)
for i in range(3):
    for j in range(3):
        idx = 3 * i + j
        with cols[j]:
            if st.button(EMOJIS[board[idx]], key=idx):
                if board[idx] == " " and not st.session_state.winner and st.session_state.turn == "player1":
                    board[idx] = symbol_map["player1"]
                    if check_winner(board, board[idx]):
                        st.session_state.winner = "player1"
                    elif is_full(board):
                        st.session_state.winner = "draw"
                    else:
                        st.session_state.turn = "player2"
                    st.session_state.timer_start = datetime.now()
                    st.rerun()
                elif mode == "Multiplayer" and board[idx] == " " and not st.session_state.winner and st.session_state.turn == "player2":
                    board[idx] = symbol_map["player2"]
                    if check_winner(board, board[idx]):
                        st.session_state.winner = "player2"
                    elif is_full(board):
                        st.session_state.winner = "draw"
                    else:
                        st.session_state.turn = "player1"
                    st.session_state.timer_start = datetime.now()
                    st.rerun()

# ----------------- AI Turn -----------------
if mode == "Single Player" and st.session_state.turn == "player2" and not st.session_state.winner:
    ai_move()
    if check_winner(board, symbol_map["player2"]):
        st.session_state.winner = "player2"
    elif is_full(board):
        st.session_state.winner = "draw"
    else:
        st.session_state.turn = "player1"
    st.session_state.timer_start = datetime.now()
    st.rerun()

# ----------------- Outcome Handling -----------------
if st.session_state.winner:
    if st.session_state.winner == "draw":
        st.info("🤝 It's a draw!")
        st.session_state.scores["draws"] += 1
        play_sound("draw")
        winner_name = "Draw"
    else:
        winner_name = st.session_state.player1_name if st.session_state.winner == "player1" else st.session_state.player2_name
        st.success(f"🎉 {winner_name} wins!")
        st.balloons()
        play_sound("win" if st.session_state.winner == "player1" else "lose")
        st.session_state.scores[st.session_state.winner] += 1
        # Streak logic
        if st.session_state.streak["last_winner"] == st.session_state.winner:
            st.session_state.streak[st.session_state.winner] += 1
        else:
            st.session_state.streak["player1"] = 1 if st.session_state.winner == "player1" else 0
            st.session_state.streak["player2"] = 1 if st.session_state.winner == "player2" else 0
        st.session_state.streak["last_winner"] = st.session_state.winner

    st.session_state.history.append({
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "winner": winner_name,
        "board": board.copy()
    })

# ----------------- New Round -----------------
if st.button("🔄 New Round"):
    st.session_state.board = [" "] * 9
    st.session_state.turn = "player1"
    st.session_state.timer_start = datetime.now()
    st.session_state.winner = None
    st.rerun()

# ----------------- Sidebar -----------------
st.sidebar.markdown("### 🏆 Scores")
st.sidebar.write(f"{st.session_state.player1_name}: {st.session_state.scores['player1']}")
st.sidebar.write(f"{st.session_state.player2_name}: {st.session_state.scores['player2']}")
st.sidebar.write(f"Draws: {st.session_state.scores['draws']}")

st.sidebar.markdown("### 🔥 Win Streaks")
st.sidebar.write(f"{st.session_state.player1_name}: {st.session_state.streak['player1']}")
st.sidebar.write(f"{st.session_state.player2_name}: {st.session_state.streak['player2']}")

if st.session_state.history:
    st.sidebar.markdown("### 📜 Game History")
    for game in reversed(st.session_state.history[-5:]):
        st.sidebar.write(f"🕒 {game['timestamp']} - {game['winner']}")
        st.sidebar.code(render_board_snapshot(game['board']))
    df = pd.DataFrame(st.session_state.history)
    csv = df.to_csv(index=False)
    st.sidebar.download_button("📥 Download History", csv, file_name="game_history.csv", mime="text/csv")

# ----------------- Move Timeout -----------------
if st.session_state.timer_start:
    elapsed = (datetime.now() - st.session_state.timer_start).total_seconds()
    if elapsed > st.session_state.time_limit and not st.session_state.winner:
        # Time's up for current player
        if mode == "Multiplayer" or st.session_state.turn == "player1":
            # Auto skip or forfeit turn
            st.warning(f"⏰ {turn_name} ran out of time! Turn forfeited.")
            st.session_state.turn = "player2" if st.session_state.turn == "player1" else "player1"
            st.session_state.timer_start = datetime.now()
            st.rerun()
        elif mode == "Single Player" and st.session_state.turn == "player2":
            # AI move immediately if time up
            ai_move()
            if check_winner(board, symbol_map["player2"]):
                st.session_state.winner = "player2"
            elif is_full(board):
                st.session_state.winner = "draw"
            else:
                st.session_state.turn = "player1"
            st.session_state.timer_start = datetime.now()
            st.rerun()
