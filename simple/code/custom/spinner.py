import sys
import time
import itertools
from colorama import init, Fore, Style


def animated_spinner(duration=5, speed=0.1):
    init(autoreset=True)
    spinner = itertools.cycle(['◐', '◓', '◑', '◒'])
    end_time = time.time() + duration
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN,
              Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

    while time.time() < end_time:
        sys.stdout.write("\\r" + next(itertools.cycle(colors)) +
                         next(spinner) + Style.RESET_ALL + " Loading... ")
        sys.stdout.flush()
        time.sleep(speed)

    sys.stdout.write("\\r" + Fore.GREEN + "✔ Done!          \\n")


if __name__ == "__main__":
    animated_spinner(10, 0.1)
