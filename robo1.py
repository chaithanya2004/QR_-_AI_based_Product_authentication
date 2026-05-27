import random
import time
import os
import sys

# ------------------ CONFIGURATION ------------------
WIDTH = 20
HEIGHT = 10
PATH_LENGTH = 80
SPEED = 0.25

# Symbols
PERSON_SYMBOL = "👤"
WALL_SYMBOL = "🧱"
COIN_SYMBOL = "💰"
ROBOT_SYMBOL = "🤖"
GOAL_SYMBOL = "🏁"
EMPTY_SYMBOL = "·"

# Colors (ANSI)
COLOR_PERSON = "\033[33m"
COLOR_WALL = "\033[31m"
COLOR_ROBOT = "\033[36m"
COLOR_COIN = "\033[32m"
COLOR_GOAL = "\033[35m"
COLOR_RESET = "\033[0m"

# ------------------ UTILITY FUNCTIONS ------------------
def clear():
    sys.stdout.flush()
    os.system("cls" if os.name == "nt" else "clear")

def draw_scene(robot_pos, view, distance, score, direction, status, goal_pos):
    """Draw the visible screen with robot, goal, coins, walls, persons"""
    clear()
    print(f"Distance: {distance}  Score: {score}  Direction: {direction}  Status: {status}")
    print("-" * (WIDTH * 2))

    for y in range(HEIGHT):
        for x in range(WIDTH):
            if [x, y] == robot_pos:
                print(f"{COLOR_ROBOT}{ROBOT_SYMBOL}{COLOR_RESET}", end=" ")
            elif [x, y] == goal_pos:
                print(f"{COLOR_GOAL}{GOAL_SYMBOL}{COLOR_RESET}", end=" ")
            elif view[y][x] == "P":
                print(f"{COLOR_PERSON}{PERSON_SYMBOL}{COLOR_RESET}", end=" ")
            elif view[y][x] == "W":
                print(f"{COLOR_WALL}{WALL_SYMBOL}{COLOR_RESET}", end=" ")
            elif view[y][x] == "C":
                print(f"{COLOR_COIN}{COIN_SYMBOL}{COLOR_RESET}", end=" ")
            else:
                print(EMPTY_SYMBOL, end=" ")
        print()
    print("-" * (WIDTH * 2))

def safe_world(world, wx, wy):
    """Return tile at world position or 'W' if out of bounds"""
    if 0 <= wy < HEIGHT and 0 <= wx < len(world[0]):
        return world[wy][wx]
    return "W"

def generate_world():
    """Create a random world map"""
    world = []
    for y in range(HEIGHT):
        row = []
        for x in range(PATH_LENGTH + WIDTH):
            row.append(random.choice([" ", " ", " ", "P", "W", "C"]))
        world.append(row)
    return world

def get_view(world, offset):
    """Return visible 20x10 portion of the world"""
    return [world[y][offset:offset + WIDTH] for y in range(HEIGHT)]

# ------------------ MAIN GAME ------------------
def main():
    robot_name = input("Enter Robot Name: ") or "Robo"

    start_x = int(input("Enter starting X (0 to 5): "))
    start_y = int(input("Enter starting Y (0 to 9): "))
    goal_x = int(input("Enter destination X (10 to 19): "))
    goal_y = int(input("Enter destination Y (0 to 9): "))

    # Clamp positions
    start_x = max(0, min(start_x, 5))
    start_y = max(0, min(start_y, HEIGHT - 1))
    goal_x = max(10, min(goal_x, WIDTH - 1))
    goal_y = max(0, min(goal_y, HEIGHT - 1))

    robot_pos = [start_x, start_y]
    goal_pos = [goal_x, goal_y]

    # Log file
    log_file = open("journey_log.txt", "w", encoding="utf-8")
    log_file.write(f"Robot Name: {robot_name}\n")
    log_file.write(f"Start Position: {robot_pos}\n")
    log_file.write(f"Goal Position: {goal_pos}\n")
    log_file.write("Journey Log:\n")

    world = generate_world()
    offset = 0
    score = 0
    distance = 0
    direction = "right"
    status = "moving"
    stuck_counter = 0  # detect if stuck

    try:
        while True:
            view = get_view(world, offset)
            draw_scene(robot_pos, view, distance, score, direction, status, goal_pos)

            # Check if goal reached
            if robot_pos == goal_pos:
                status = "stopped"
                print(f"{robot_name} reached the destination! 🏁")
                log_file.write("Robot reached the destination!\n")
                break

            x, y = robot_pos
            wx = offset + x
            front = safe_world(world, wx + 1, y)

            # ---------------- PERSON / WALL LOGIC ----------------
            if front == "P":
                status = "stopped"
                wait_seconds = 5  # countdown duration
                for sec in range(wait_seconds, 0, -1):
                    draw_scene(robot_pos, view, distance, score, direction,
                               f"Person ahead! Waiting {sec}s", goal_pos)
                    time.sleep(1)
                print("Person passed! Resuming movement.")
                log_file.write(f"Waited for person {wait_seconds} seconds.\n")
                direction = "right"

            elif front == "W":
                status = "stopped"
                print("Wall ahead! 🧱")
                log_file.write("Wall ahead! Asking user for direction.\n")

                # ---------------- USER INPUT ----------------
                print("Choose direction to avoid wall:")
                print("Type: right / left / up / down")
                choice = input("Your choice: ").strip().lower()

                if choice in ["right", "left", "up", "down"]:
                    direction = choice
                else:
                    print("Invalid choice! Staying in the same direction.")
                    log_file.write("Invalid direction entered by user.\n")

            else:
                direction = "right"  # default

            # ---------------- MOVE ROBOT ----------------
            old_pos = robot_pos.copy()

            if direction == "right":
                robot_pos[0] += 1
                offset += 1
                distance += 1
                log_file.write(f"Moved right. Distance: {distance}\n")
            elif direction == "up":
                robot_pos[1] -= 1
                log_file.write("Moved up to avoid obstacle.\n")
            elif direction == "down":
                robot_pos[1] += 1
                log_file.write("Moved down to avoid obstacle.\n")
            elif direction == "left":
                robot_pos[0] -= 1
                log_file.write("Moved left to avoid obstacle.\n")

            # Clamp bounds
            robot_pos[0] = max(0, min(robot_pos[0], WIDTH - 1))
            robot_pos[1] = max(0, min(robot_pos[1], HEIGHT - 1))

            # Check if stuck
            if robot_pos == old_pos:
                stuck_counter += 1
            else:
                stuck_counter = 0
            if stuck_counter > 10:
                print("Robot is stuck! No path found. Stopping simulation.")
                log_file.write("Robot is stuck! No path found.\n")
                break

            wx = offset + robot_pos[0]

            # Collect coin
            if safe_world(world, wx, robot_pos[1]) == "C":
                score += 20
                world[robot_pos[1]][wx] = " "
                log_file.write(f"Coin collected! Score: {score}\n")

            status = "moving"
            time.sleep(SPEED)

    except KeyboardInterrupt:
        print("\nSimulation interrupted by user!")
        log_file.write("Simulation interrupted by user.\n")

    # ---------------- FINAL SUMMARY ----------------
    print("\n--- FINAL TRIP SUMMARY ---")
    print(f"Robot Name: {robot_name}")
    print(f"Start Position: {(start_x, start_y)}")
    print(f"Goal Position: {(goal_x, goal_y)}")
    print(f"Total Distance: {distance}")
    print(f"Score: {score}")

    log_file.write("\n--- FINAL TRIP SUMMARY ---\n")
    log_file.write(f"Total Distance: {distance}\n")
    log_file.write(f"Score: {score}\n")
    log_file.close()
    print("Journey saved to journey_log.txt")

# ------------------ RUN GAME ------------------
if __name__ == "__main__":
    main()