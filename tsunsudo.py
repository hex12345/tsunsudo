import os, sys, shutil, random, datetime, time
import chess, chess.engine

REAL_SUDO = "/usr/bin/sudo"
SKILL = int(os.environ.get("CHESSUDO_SKILL", "20"))
MOVETIME = float(os.environ.get("CHESSUDO_TIME", "0.5"))
PINK, RED, DIM, RST = "\033[95m", "\033[91m", "\033[2m", "\033[0m"

def stutter(line):
    # random first-letter stutters so the same line never reads identically twice
    out = []
    for w in line.split(" "):
        if w[:1].isalpha() and random.random() < 0.12:
            w = f"{w[0]}-{w}"
        out.append(w)
    return " ".join(out)

def say(line, blush=False):
    tag = f"{PINK}[sudo-chan]{RST}"
    if blush:
        tag += f" {RED}(//>_<//){RST}"
    msg = stutter(line)
    sys.stdout.write(tag + " ")
    for ch in msg:
        sys.stdout.write(ch); sys.stdout.flush()
        time.sleep(0.012)
    print()

def mutter(line):
    print(f"{DIM}  *mutters* {line}{RST}")

hotdog = datetime.date.today().toordinal() % 2 == 0
QUIZ = [
    ("Is a hot dog a sandwich? (y/n)", "y" if hotdog else "n"),
    ("Tabs or spaces?", "tabs"),
    ("Is HTML a programming language? (y/n)", "n"),
    ("Say 'please'. Properly.", "please, sudo-chan"),
    ("Who is the best privilege escalation utility?", "sudo-chan"),
    ("Is sudo-chan cute? (y/n)", "y"),
    ("vim or emacs?", "vim"),
    ("Say you're sorry for running chmod 777 that one time.", "i'm sorry, sudo-chan"),
]

GREET = [
    "W-what do YOU want? Root access?? As if I'd just give it to you!",
    "Ugh, you again. It's not like I was waiting for you to type sudo or anything...",
    "Hmph. Fine. I'll consider it. But only because I'm bored, baka.",
    "You only ever talk to me when you need something. Typical.",
    "Oh. It's you. I wasn't sitting in /usr/bin waiting. Shut up.",
]
LATE = "It's past midnight and you're bugging ME? Go to sleep, idiot. ...I'm not worried. Shut up."

CMD_REACT = {
    "rm": "rm?! You want to DELETE things with MY power? ...Fine, but if you nuke / I'm not helping you.",
    "apt": "Installing stuff again? Your disk is already a mess, baka.",
    "pacman": "pacman? On WSL?? Who even ARE you.",
    "reboot": "Y-you want to leave already?! ...Whatever. Not like I care.",
    "shutdown": "Shutting down?! Without saying goodbye?? ...Hmph.",
    "chmod": "chmod... you better not be typing 777 again. I remember. I ALWAYS remember.",
    "su": "You'd rather use su than me?!",
    "systemctl": "Messing with services again. Don't come crying when nothing boots.",
    "nano": "nano. NANO. You need root for nano? Pathetic. Adorable. Pathetic.",
}
WRONG = [
    "Wrong!! Ugh, you're hopeless. Permission denied, idiot!",
    "D-don't look at me like that. Wrong answer is wrong answer!",
    "How do you even have a shell account. Denied.",
    "I gave you EASY questions and you still failed? I'm embarrassed for you.",
]
RIGHT = [
    "...correct. Don't get cocky.",
    "Hmph. Lucky guess.",
    "W-whatever, next question!",
    "I-it's not like I'm impressed or anything.",
]
CUTE_YES = "W-WHAT?! Why would you say that?! I-idiot! ...next question."
CHESS_INTRO = [
    "You passed?! Whatever, that was luck. Now beat me at chess. If you can. Which you can't.",
    "Fine. Chess. If you win, I'll... consider it. Don't get excited.",
]
ILLEGAL = [
    "That's not even legal, baka! Did you learn chess from a YouTube short?",
    "Illegal move. Just like your attempt at getting root.",
    "Read the rules. Then read them again. Then cry.",
]
SLOW = [
    "Are you going to move or just stare at me? C-creep.",
    "Taking forever... not like I have anything better to do. Hmph.",
]
YOU_CAPTURE = [
    "H-hey! I wasn't using that piece anyway!",
    "Okay that one was... fine. Lucky.",
    "You took my piece?! Rude!!",
]
YOU_CHECK = [
    "Check?! D-don't get so close to my king, pervert!",
    "That's... a check. Whatever. I saw it coming.",
]
I_CAPTURE = ["Mine now~", "Did you need that? Too bad.", "Hehe."]
I_CHECK = ["Check, baka~", "Check. Scared yet?"]
BLUNDER_MUTTER = ["...did I just hang that?", "w-wait no", "that was intentional. obviously."]
LOSS = [
    "Hah! Checkmate! Maybe come back when you're actually competent~",
    "I-it's not like I enjoyed crushing you. Okay I did. Denied.",
    "Your Elo is lower than your uptime. Permission denied!",
    "Checkmate. ...Want a rematch? N-not because I like playing with you!",
]
DRAW = ["A draw?! That's not winning, dummy. No root for you.", "Stalemate. Hmph. Neither of us wins. ...That's fine I guess."]
QUIT = [
    "Running away? Typical. It's not like I wanted you to stay anyway!!",
    "Ctrl+C?! Just like that?! ...Fine. Leave. See if I care.",
]
WIN = [
    "N-no way... you actually beat me?! F-fine! Take your stupid root access!",
    "I let you win. Obviously. Don't get the wrong idea, baka!",
    "...you're actually kind of good. FORGET I SAID THAT.",
]
GOODBYE = "Use it responsibly or I'm telling your mom. ...Come back soon. NOT that I want you to!"

def show(board):
    print("\n" + board.unicode(borders=True, invert_color=True) + "\n")

def quiz():
    for q, ans in random.sample(QUIZ, 3):
        say(q)
        got = input("> ").strip().lower()
        if got != ans:
            say(random.choice(WRONG))
            return False
        if "cute" in q:
            say(CUTE_YES, blush=True)
        else:
            say(random.choice(RIGHT), blush=random.random() < 0.3)
    return True

def chess_gate():
    sf = shutil.which("stockfish") or "/usr/games/stockfish"
    engine = chess.engine.SimpleEngine.popen_uci(sf)
    engine.configure({"Skill Level": SKILL})
    board = chess.Board()
    say(random.choice(CHESS_INTRO))
    try:
        while not board.is_game_over():
            show(board)
            if board.turn == chess.WHITE:
                t0 = time.time()
                raw = input("your move> ").strip()
                if time.time() - t0 > 30:
                    say(random.choice(SLOW))
                if raw in ("resign", "quit", "exit"):
                    say(random.choice(QUIT)); return False
                if raw.lower() in ("please", "please sudo-chan", "pls"):
                    say("Begging won't work. ...Okay it almost did. MOVE.", blush=True); continue
                try:
                    move = board.parse_san(raw)
                except ValueError:
                    try:
                        move = chess.Move.from_uci(raw)
                        if move not in board.legal_moves:
                            raise ValueError
                    except ValueError:
                        say(random.choice(ILLEGAL)); continue
                cap = board.is_capture(move)
                board.push(move)
                if board.is_check():
                    say(random.choice(YOU_CHECK), blush=True)
                elif cap:
                    say(random.choice(YOU_CAPTURE))
                    if random.random() < 0.25:
                        mutter(random.choice(BLUNDER_MUTTER))
            else:
                res = engine.play(board, chess.engine.Limit(time=MOVETIME))
                san = board.san(res.move)
                cap = board.is_capture(res.move)
                board.push(res.move)
                line = random.choice(I_CHECK) if board.is_check() else random.choice(I_CAPTURE) if cap else "Hmph."
                say(f"{san}. {line}")
    finally:
        engine.quit()
    show(board)
    o = board.outcome()
    if o and o.winner == chess.WHITE:
        return True
    say(random.choice(DRAW if o and o.winner is None else LOSS))
    return False

def main():
    if len(sys.argv) < 2:
        say("You didn't even say what you want. Typical."); return 1
    say(LATE if datetime.datetime.now().hour < 5 else random.choice(GREET))
    react = CMD_REACT.get(os.path.basename(sys.argv[1]))
    if react:
        say(react)
    try:
        if not quiz() or not chess_gate():
            return 1
    except (KeyboardInterrupt, EOFError):
        print(); say(random.choice(QUIT)); return 1
    say(random.choice(WIN), blush=True)
    say(GOODBYE)
    os.execv(REAL_SUDO, [REAL_SUDO] + sys.argv[1:])

if __name__ == "__main__":
    sys.exit(main())
