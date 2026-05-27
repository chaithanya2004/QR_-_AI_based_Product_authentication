import random
import time
import os

WIDTH = 20
HEIGHT = 10
PATH_LENGTH = 80

SYMBOLS = {
    "robot": "🤖",
    "person": "👤",
    "wall": "🧱",
    "coin": "💰",
    "empty": "."
}

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def progress_bar(distance):
    bar_len = 30
    filled = int(bar_len * distance / PATH_LENGTH)
    return "[" + "█" * filled + "-" * (bar_len - filled) + "]"

def generate_world():
    world = []
    for y in range(HEIGHT):
        row = []
        for x in range(PATH_LENGTH + WIDTH):
            tile = random.choice([" ", " ", "P", "W", "C"])
            row.append(tile)
        world.append(row)
    return world

def safe(world, x, y):
    if 0 <= y < HEIGHT and 0 <= x < len(world[0]):
        return world[y][x]
    return " "

def draw(robot, world, offset, distance, score, status):
    clear()
    print(f"Progress: {progress_bar(distance)}  Distance: {distance}/{PATH_LENGTH}")
    print(f"Score: {score}  Status: {status}")
    print("-" * 40)

    for y in range(HEIGHT):
        for x in range(WIDTH):
            wx = offset + x
            if [x, y] == robot:
                print(SYMBOLS["robot"], end=" ")
            else:
                tile = safe(world, wx, y)
                if tile == "P": print(SYMBOLS["person"], end=" ")
                elif tile == "W": print(SYMBOLS["wall"], end=" ")
                elif tile == "C": print(SYMBOLS["coin"], end=" ")
                else: print(SYMBOLS["empty"], end=" ")
        print()
    print("-" * 40)

def countdown_wait(seconds, robot, world, offset, distance, score):
    # draw once, then only update status line (no flicker)
    for sec in range(seconds, 0, -1):
        clear()
        print(f"Progress: {progress_bar(distance)}  Distance: {distance}/{PATH_LENGTH}")
        print(f"Score: {score}  Status: waiting {sec}...")
        print("-" * 40)

        for y in range(HEIGHT):
            for x in range(WIDTH):
                wx = offset + x
                if [x, y] == robot:
                    print(SYMBOLS["robot"], end=" ")
                else:
                    tile = safe(world, wx, y)
                    if tile == "P": print(SYMBOLS["person"], end=" ")
                    elif tile == "W": print(SYMBOLS["wall"], end=" ")
                    elif tile == "C": print(SYMBOLS["coin"], end=" ")
                    else: print(SYMBOLS["empty"], end=" ")
            print()
        print("-" * 40)

        time.sleep(1)

def game():
    robot_name = input("Robot name: ") or "Robo"

    world = generate_world()
    robot = [0, HEIGHT//2]
    offset = 0
    score = 0
    distance = 0
    direction = "RIGHT"

    while True:

        draw(robot, world, offset, distance, score, "moving")

        x, y = robot
        wx = offset + x
        front = safe(world, wx + 1, y)

        # PERSON
        if front == "P":
            countdown_wait(5, robot, world, offset, distance, score)
            robot[0] += 1
            direction = "RIGHT"

        # WALL
        elif front == "W":
            draw(robot, world, offset, distance, score, "blocked")
            move = input("Wall! Move (up/down/back): ").lower()

            if move == "up":
                robot[1] -= 1
                direction = "UP"
            elif move == "down":
                robot[1] += 1
                direction = "DOWN"
            elif move == "back":
                robot[0] -= 1
                direction = "BACK"
            continue

        # NORMAL MOVE
        else:
            robot[0] += 1
            direction = "RIGHT"

        robot[1] = max(0, min(robot[1], HEIGHT-1))
        robot[0] = max(0, min(robot[0], WIDTH-1))

        wx = offset + robot[0]

        # coin
        if safe(world, wx, robot[1]) == "C":
            score += 20
            world[robot[1]][wx] = " "

        offset += 1
        distance += 1

        # END GAME when reach dot-end
        if distance >= PATH_LENGTH:
            break

        time.sleep(0.25)

    # FINAL SCREEN
    clear()
    print("🏁 GAME OVER 🏁")
    print(f"Robot name: {robot_name}")
    print(f"Final score: {score}")
    print(f"Total distance: {distance}")
    print(f"Final position: X={robot[0]}, Y={robot[1]}")
    print(f"Direction faced: {direction}")
    print("Mission complete!")

game()