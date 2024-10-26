import curses
from curses import wrapper
import locale
import time
from collections import defaultdict

# Set the locale to support Unicode
locale.setlocale(locale.LC_ALL, "")


def next_generation(live_cells):
    neighbor_counts = defaultdict(int)

    # Count neighbors for all live cells
    for cell in live_cells:
        y, x = cell
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dy == 0 and dx == 0:
                    continue  # Skip the cell itself
                neighbor = (y + dy, x + dx)
                neighbor_counts[neighbor] += 1

    new_live_cells = set()

    for cell, count in neighbor_counts.items():
        if count == 3 or (count == 2 and cell in live_cells):
            new_live_cells.add(cell)

    return new_live_cells


def main(stdscr):
    # Clear screen and hide the cursor
    stdscr.clear()
    curses.curs_set(0)  # Hide the cursor

    # Initialize starting position for the cursor
    x, y = 5, 5  # Starting at (5, 5) for better visibility
    speed = 1  # Movement speed

    generation_count = 0
    generation_stale_string = ""
    generation_death = 0
    history_stack = []
    # Define the Unicode block character
    block_char = "█"  # Represents a live cell

    # Set to store live cells
    live_cells = set()

    # Game modes: 'setup' or 'simulation'
    mode = "setup"
    interval = 0.1

    # Configure input settings

    stdscr.nodelay(True)  # Make getch non-blocking
    stdscr.timeout(10)  # Refresh every 100 milliseconds

    # Initialize color pairs
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)  # Live cells
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Cursor

    # Instructions
    instructions_setup = "W/A/S/D: Move | Space: Toggle Cell | F: Start Simulation | Q: Quiti | 1: set interval to 100ms | 2: 25ms | 3: 1ms | C: Clear"
    instructions_simulation = "Simulation Running. Press 'F' to Pause | Q: Quit"

    while True:
        try:
            # Attempt to get a key press
            key = stdscr.getkey()
        except curses.error:
            # No input received
            key = None

        if mode == "setup":
            # Handle inputs in Setup Mode
            if key:
                if key.lower() == "q":
                    break  # Quit the application
                elif key.lower() == "f":
                    if live_cells:
                        mode = "simulation"  # Start simulation only if there are live cells
                elif key == " ":
                    generation_death = 0
                    generation_stale_string = ""
                    # Toggle cell state at cursor position
                    if (y, x) in live_cells:
                        live_cells.remove((y, x))
                    else:
                        live_cells.add((y, x))
                elif key.lower() == "a":
                    x -= speed
                elif key.lower() == "d":
                    x += speed
                elif key.lower() == "w":
                    y -= speed
                elif key.lower() == "s":
                    y += speed
                elif key == "1":
                    interval = 0.1
                elif key == "2":
                    interval = 0.025
                elif key == "3":
                    interval = 0.001
                elif key.lower() == "c":
                    live_cells = set()

            # Boundary checks
            max_y, max_x = stdscr.getmaxyx()
            y = max(2, min(y, max_y - 1))
            x = max(0, min(x, max_x - 1))

            # Clear the screen
            stdscr.erase()

            # Display instructions
            stdscr.addstr(0, 0, instructions_setup)

            # Display cursor position
            stdscr.addstr(1, 0, f"Cursor Position: ({y}, {x})")

            # Draw all live cells
            for cell in live_cells:
                cell_y, cell_x = cell
                if 0 <= cell_y < max_y and 0 <= cell_x < max_x:
                    try:
                        stdscr.addstr(cell_y, cell_x, block_char, curses.color_pair(1))
                    except curses.error:
                        pass  # Ignore if out of bounds

            # Draw the cursor
            try:
                stdscr.addstr(y, x, block_char, curses.color_pair(2) | curses.A_BOLD)
            except curses.error:
                pass  # Ignore if out of bounds

        elif mode == "simulation":
            # Handle inputs in Simulation Mode
            if key:
                if key.lower() == "q":
                    break  # Quit the application
                elif key.lower() == "f":
                    mode = "setup"  # Pause simulation
            #
            # Compute next generation
            copy_list = live_cells.copy()  # Use copy() to create a shallow copy
            history_stack.append(copy_list)
            if len(history_stack) > 4:
                history_stack.pop(
                    0
                )  # Pop from the start to remove the oldest generation

            if len(history_stack) >= 4 and not generation_death:
                if history_stack[-1] in history_stack[:-1]:
                    generation_death = generation_count
                    generation_stale_string = (
                        f" | Generation died at {generation_death}"
                    )

            live_cells = next_generation(live_cells)
            generation_count += 1

            # Clear the screen
            stdscr.erase()

            # Display instructions
            stdscr.addstr(0, 0, instructions_simulation)
            stdscr.addstr(
                1, 0, f"Generation: {generation_count}{generation_stale_string}"
            )

            # Draw all live cells
            for cell in live_cells:
                cell_y, cell_x = cell
                if 0 <= cell_y < max_y and 0 <= cell_x < max_x:  # pyright: ignore
                    try:
                        stdscr.addstr(cell_y, cell_x, block_char, curses.color_pair(1))
                    except curses.error:
                        pass  # Ignore if out of bounds

            # Optional: Display generation count
            # Implement a generation counter if desired

            stdscr.refresh()
            time.sleep(interval)

        # Refresh the screen to update changes
        stdscr.refresh()

    # Optional: Add a goodbye message before exiting
    stdscr.erase()
    stdscr.addstr(0, 0, "Now you live on...")
    stdscr.refresh()
    time.sleep(1)  # Wait for 1 second before exiting


# Run the curses application
wrapper(main)
