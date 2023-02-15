from tkinter import Tk, Canvas, Label, PhotoImage, Button, Menu, Text, Entry, Frame, OptionMenu, StringVar
from random import randint
import json

# define key events 


def moveLeft(event):
    global direction
    direction = "left"


def moveRight(event):
    global direction
    direction = "right"


def unpause(event):
    global pause, movement_speed
    pause = False
    movement_speed=15
    game_menu.place_forget()


def cheatKey(event):
    global movement_speed, max_bullets, lives
    movement_speed = 25
    max_bullets = 20
    lives += 5

# functions for ship, alien, and bullet movement


def move_ship():
    global direction, pause
    if game_over is True:
        return
    else:
        try:
            if direction == "left":
                playground.move(ship, -movement_speed, 0)
            elif direction == "right":
                playground.move(ship, movement_speed, 0)
            ship_position = playground.coords(ship)
            # if ship touches the edge, change direction:
            if ship_position[0] < 0:
                direction = "right"
            elif ship_position[0] > width:
                direction = "left"
        except (IndexError, TypeError):  # ignore errors which arise due to ship despawing
            pass

        window.after(30, move_ship)


def move_alien():
    global lives, game_over
    if round_over is True:
        return
    else:
        alien_position = []
        for i in range(len(aliens)):
            if pause is False:
                playground.move(aliens[i], randint(-20, 20), randint(0, alien_speed))  # create random,jittery movements
                alien_position.append(playground.coords(aliens[i]))
            try:
                if alien_position[i][1] > height:
                    lives -= 1
                    txt = f"Lives:{lives}"
                    lives_label.config(text=txt)
                    playground.coords(aliens[i], randint(50, width-50), 0)

                # if alien gets too close to edge, push it back in:
                if alien_position[i][0] < 50:
                    playground.move(aliens[i], 10, 0)
                elif alien_position[i][0] > width-50:
                    playground.move(aliens[i], -10, 0)
            except IndexError:
                pass

            if overlapping(playground.bbox(aliens[i]), playground.bbox(ship)):
                lives -= 1
                txt = f"Lives:{lives}"
                lives_label.config(text=txt)
                playground.coords(aliens[i], randint(50, width-50), 0)

        if lives == 0:
            game_over is True
            game_finish()
            return
            
        elif game_over is False:
            window.after(50, move_alien)


def shoot(event):
    global bullets, game_over, max_bullets
    if game_over is True:
        return
    elif round_over is False and pause is False:
        try: 
            ship_location = playground.bbox(ship)
            centre_x = (ship_location[0] + ship_location[2])/2
            centre_y = (ship_location[1] + ship_location[3])/2
            if len(bullets) < max_bullets:  # only allow max_bullets at any one time
                bullets.append(playground.create_image(centre_x, centre_y, image=bullet_image, tag="bullet"))
                counter = 0
                if counter <= 1:
                    return
                else:
                    counter += 1  # use of counter ensures move_bullet is only being looped through once.
                    move_bullet()
        except TypeError:
            pass


def move_bullet():
    global bullets, score, round_over, round
    if game_over is True:
        return
    for i in range(len(bullets)):
        try:
            playground.move(bullets[i], 0, -10)
            bullet_position = playground.bbox(bullets[i])
            # if bullets go too high, delete it and remove from array
            if bullet_position[1] < 0:
                playground.delete(bullets[i])
                bullets.pop(i)
         
            for j in range(len(aliens)):
                if overlapping(bullet_position, playground.bbox(aliens[j])):
                    score += 1
                    txt = f"Score:{score}"
                    score_label.config(text=txt)
                    playground.coords(aliens[j], randint(50, width-50), 0)
                    playground.delete(bullets[i])
                    bullets.pop(i)

        except (IndexError, TypeError):
            pass

    if round == 1 and score == 40:
        round_over = True
        round = 2
        txt = f"Round:{round}"
        round_label.config(text=txt)
        playground.delete("alien")
        aliens.clear()
        playground.delete("bullet")
        bullets.clear()
        playground.create_text(width/2,height/2,fill="white", font="Arial 30 bold", text="That was easy... get ready for round 2", tag="text1")
        return

    if round == 2 and score == 100:
        round_over = True
        round = 3
        txt = f"Round:{round}"
        round_label.config(text=txt)
        playground.delete("alien")
        aliens.clear()
        playground.delete("bullet")
        playground.create_text(width/2,height/2,fill="white", font="Arial 30 bold", text="Impressive, now try beat the final round!", tag="text2")
        bullets.clear()
        return

    if round == 3 and score == 200:
        round_over = True
        round = 4
        txt = f"Round:{round}"
        round_label.config(text=txt)
        playground.delete("alien")
        aliens.clear()
        playground.delete("bullet")
        bullets.clear()
        playground.create_text(width/2,height/2,fill="white", font="Arial 30 bold", text="Good job, you've made it past all the rounds. Now see how long you can last!", tag="text4")
        return
    
    window.after(10, move_bullet)

def overlapping(a, b):
    try:
        if a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]:
            return True
    except(IndexError, TypeError):
        return False
    return False

def game_finish():
    global username_entry, game_over, button
    game_over = True
    playground.create_text(width/2,height/2+100,fill="white", font="Arial 30 bold", text="Game Over!", tag="gameover")
   
    playground.delete("alien")
    aliens.clear()
    playground.delete("bullet")
    bullets.clear()

    username_entry = Entry(playground)
    username_entry.place(x=width/2-80, y=200)
    username_entry.focus_set()
    button = Button(text="Enter username", command=write_to_leaderboard)
    button.place(x=width/2-50, y=300)

def write_to_leaderboard():
    global restart_button, display_leaderboard
    playground.delete("gameover")
    username = username_entry.get()
    username_entry.place_forget()
    button.place_forget()

    restart_button = Button(playground, text="Start again!", bg="Green", fg="Black", font="Arial 40 bold", command=restart_game)
    restart_button.place(x=width/2-100, y=80)

    username_score = [username, score]

    leaderboard = []
    with open("leaderboard.json", "r") as f:
        leaderboard = json.load(f)

    leaderboard.append(username_score)
    sorted_leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)
    sorted_leaderboard.pop()
    
    with open("leaderboard.json", "w") as f:
        # delte contents of file and replace with leaderboard in descending order
        f.truncate()
        f.write(json.dumps(sorted_leaderboard))

    display_leaderboard = Text(playground, height=8, width=26, background="Black", font="Arial 30")
    display_leaderboard.place(x=400,y=150)

    # create a table fot the leaderboard using format()
    headings = ["Username", "Score"]
    format_row = "{:>12}" * (len(headings) + 1)
    top = format_row.format("", *headings)
    table = f"{top}\n"
    for i in range(5):
        table += format_row.format("", *sorted_leaderboard[i]) + "\n"
    display_leaderboard.insert("0.0",table)


def save_game():
    #save the game state to a json
    game_dict = {"round":round, "lives":lives}
    game_json = json.dumps(game_dict)
    with open("savegame.json", "w") as f:
        f.write(f"{game_json}")

def load_game():
    global lives, round, round_over, game_over
    f = open("savegame.json", "r")
    game_json = f.read()
    game_dict = json.loads(game_json)
    round = game_dict["round"]
    lives = game_dict["lives"]
    txt = f"Lives:{lives}"
    lives_label.config(text=txt)
    txt = f"Round:{round}"
    round_label.config(text=txt)
    playground.delete("alien")
    aliens.clear()
    playground.delete("bullet")
    bullets.clear()
    round_over = True
    playground.create_text(width/2,height/2,fill="white", font="Arial 30 bold", text=f"Continuing from round {round}. Press <u> when ready.", tag="text3")

def bossKey(event):
    global boss_image, pause #has to be global as tkinter images defined in functions will be discarded
    boss_image = PhotoImage(file="Media/boss.png")
    boss = playground.create_image(0,0,anchor="nw", image=boss_image)
    playground.tag_raise(boss, space)
    playground.delete("ship")
    playground.delete("alien")
    playground.delete("bullet")
    score_label.place_forget()
    round_label.place_forget()
    lives_label.place_forget()

def create_alien(number):
    for i in range(number):
        aliens.append(playground.create_image(-100,-100,image=alien_image, tag="alien"))
        playground.coords(aliens[i], randint(0, width), -100)

def set_window_dimensions(w, h):
    win = Tk()
    win.title("")
    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    centre_x = int(screen_width/2 - w/2) 
    centre_y = int(screen_height/2 - h/2) 
    win.geometry(f"{w}x{h}+{centre_x}+{centre_y}")
    return win

def key_bind():
    if game_over == True:
        return
    elif game_over == False:
        playground.focus_set()
    playground.bind(input_map["move left"], moveLeft)
    playground.bind(input_map["move right"], moveRight)
    playground.bind(input_map["shoot key"], shoot)
    playground.bind(input_map["boss key"], bossKey)
    playground.bind(input_map["menu key"], menuPopup)
    playground.bind(input_map["unpause key"], unpause)
    playground.bind(input_map["cheat key"], cheatKey)
    window.after(1000, key_bind)

def change_keybind():
    global clicked, clicked2, clicked3
    change_keybind_frame.place(x=100, y=100)

    #define default values for dropdown

    clicked = StringVar()
    clicked.set("<Left>")

    clicked2 = StringVar()
    clicked2.set("<Right>")

    clicked3 = StringVar()
    clicked3.set("<space>")

    left_label = Label(change_keybind_frame, text="Move ship left:", fg="white")
    left_label.grid(row=0, column=0, padx=10, pady=10)
    
    change_left_key = OptionMenu(change_keybind_frame, clicked, "<Left>", "<a>")
    change_left_key.grid(row=0, column=1, padx=10)

    right_label = Label(change_keybind_frame, text="Move ship right:", fg="white")
    right_label.grid(row=1, column=0, padx=10, pady=10)
    
    change_right_key = OptionMenu(change_keybind_frame, clicked2, "<Right>", "<d>")
    change_right_key.grid(row=1, column=1, padx=10)

    left_label = Label(change_keybind_frame, text="Shoot:", fg="white")
    left_label.grid(row=2, column=0, padx=10, pady=10)
    
    change_shoot_key = OptionMenu(change_keybind_frame, clicked3, "<space>", "Left click") #use "Left click" as it is not apparent what "<Button-1>" is
    change_shoot_key.grid(row=2, column=1, padx=10, pady=10)

    ok_button = Button(change_keybind_frame, text="Ok", command=set_new_keybind)
    ok_button.grid(row=3,column=1, padx=10,pady=10)
    
def set_new_keybind():
    playground.focus_set()
    playground.unbind("<space>")
    playground.unbind("<Left>")
    playground.unbind("<Right>")
    input_map["move left"] = clicked.get()
    input_map["move right"] = clicked2.get()
    if clicked3.get() == "<space>":
        input_map["shoot key"] = clicked3.get()
    else:
        input_map["shoot key"] = "<Button-1>"
    change_keybind_frame.place_forget()

def menuPopup(event):
    global pause, movement_speed
    pause = True
    movement_speed = 0
    game_menu.tk_popup(800, 500, 0)

def round1():
    global round, round_over
    playground.delete("text3")
    create_alien(3)
    round_over = False
    move_bullet()
    move_alien()
    move_ship()
    return

def round2():
    global round, round_over
    playground.delete("text1")
    playground.delete("text3")
    create_alien(5)
    round_over = False
    move_bullet()
    move_alien()
    return

def round3():
    global round, round_over
    playground.delete("text2")
    playground.delete("text3")
    create_alien(8)
    round_over = False
    move_bullet()
    move_alien()
    return

def round4():
    global round, round_over
    playground.delete("text4")
    playground.delete("text3")
    create_alien(20)
    round_over = False
    move_bullet()
    move_alien()
    return

def restart_game():
    global game_over, score, lives, round, round_over
    restart_button.place_forget()
    display_leaderboard.place_forget()
    score = 0
    txt = f"Score:{score}"
    score_label.config(text=txt)
    lives = 5
    txt = f"Lives:{lives}"
    lives_label.config(text=txt)
    round = 1
    txt = f"Round:{round}"
    round_label.config(text=txt)
    game_over = False
    round_over = True
    main_game()

def main_game():
    global round_over
    if game_over == True:
        return
    start_button.place_forget()
    T.place_forget()
    key_bind()
    if round_over == True:
        if round == 1:
            round1()
        if round == 2:
            round2()
        if round == 3:
            round3()
        if round == 4:
            round4()
    window.after(10000, main_game)


#game variables
width = 1280
height = 720
movement_speed = 15
alien_speed = 8
max_bullets = 8
input_map = {"move left": "<Left>", "move right": "<Right>", "shoot key": "<space>","boss key":"<b>", "menu key": "<p>", "unpause key":"<u>", "cheat key":"<c>"}
direction = "right"
round_over = True
game_over = False
pause = False

window = set_window_dimensions(width, height)

#split root window into 2 canvases, top is info bar
top = Canvas(window, width=width, height=50, bg="Black")
top.grid(column=0, row=0)

playground = Canvas(window, width=width, height=height-50, bg="Black")
playground.grid(column=0, row=1)

space_image = PhotoImage(file="Media/space.png")
space = playground.create_image(0,0,anchor="nw", image=space_image)

score = 0
score_label = Label(top, width = 7, height = 1, text= f"Score:{score}",font="Arial 18 bold", bg="Black", fg="White")
score_label.place(x=60, y=20)

lives = 5
lives_label = Label(top, width = 7, height = 1, text= f"Lives:{lives}",font="Arial 18 bold", bg="Black", fg="White")
lives_label.place(x=width-140, y=20)

round = 1
round_label = Label(top, width = 7, height = 1, text= f"Round:{round}",font="Arial 18 bold", bg="Black", fg="White")
round_label.place(x=width/2-50, y=20)

T = Text(playground, height=4, width=185, background="Black", font="Arial 30")
T.place(x=0,y=200)
text = "Your job is to protect the Earth from the aliens by shooting them using <space>. You can use \nthe arrow keys to change direction of the ship. Once you have enough points you can progress \nto the next level. <p> = pause/menu. <u> = unpause. <b> = boss. Keybinds can be changed via \nthe menu. There are 3 main levels, the 4th round continues until you die. Good luck!"
T.insert("1.0",text)
start_button = Button(playground, text="Start game!", bg="Green", fg="Black", font="Arial 40 bold", command=main_game)
start_button.place(x=width/2-100, y=500)

ship_image = PhotoImage(file="Media/ship.png")
ship = playground.create_image(600, 560, image=ship_image, tag="ship")

alien_image = PhotoImage(file="Media/alien.png")
aliens = []

bullet_image = PhotoImage(file="Media/bullet.png")
bullet_image.image = bullet_image
bullets = []

change_keybind_frame = Frame(playground, width=500, height=1000, bg="white")

game_menu = Menu(playground, font="Arial 20 bold", relief="raised")
game_menu.add_command(label="Load game", command=load_game)
game_menu.add_command(label="Save game", command=save_game)
game_menu.add_separator()
game_menu.add_cascade(label="Change Keybind", command=change_keybind)

window.mainloop()
