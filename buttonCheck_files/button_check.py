import melee    # Package for everything related to smash bros melee
from melee.enums import Button # to make life easier
import argparse # Used for command-line interactions
import signal   # Used to detect KeyboardInterrupt (Ctrl+C) and then 
                #  doing something with that. In this case, we want to
                #  exit the program cleanly.
import sys      # Needed for the exiting command
# Import stuff for sending osc messages.
from pyOSC3 import OSCClient
from pyOSC3 import OSCMessage

####################################
########## Start-up Stuff ##########
####################################
# Exits Dolphin when Ctrl+C is pressed in the terminal.
def signal_handler(sig, frame):
    console.stop() # Stops Dolphin
    print("Shutting down cleanly...")
    sys.exit(0)
signal.signal(signal.SIGINT, signal_handler)

# Construct OSC client
client = OSCClient()
ip = "127.0.0.1"    # Localhost
port = 6449
client.connect( (ip, port) )
playerAdd = "/playerButtons"  # player address
# Buttons ordered as:
# A, B, X, Y, Z, L, R, D_UP, D_DOWN, D_LEFT, D_RIGHT, (11 booleans)
# main_stick_x, main_stick_y, c_sticK_x, c_stick_y, l_shoulder, r_shoulder (6 floats)
playerButtons = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Creates a console object that represents Slippi Online / Dolphin instance.
console = melee.Console(path="C:/Users/Michael/Documents/_Spring 2021/Music and Tech 2/FM-Slippi-2.2.5-Win")
# Note: File path must use forward slashes or double back slashes.
#       Single back slashes will result in unicode error.
# Creates controller objects for the bot (port 1) and the human (port 2).
controller_bot = melee.Controller(console=console, port=1)
controller_human = melee.Controller(console=console, port=2,
                                    type=melee.ControllerType.GCN_ADAPTER)
# Runs the Dolphin instance and connects the program code to it.
console.run()
console.connect()   
# "Plugs in" the controllers for the bot and human.
controller_bot.connect()
controller_human.connect()

###############################
########## Main Loop ##########
###############################
while True:
    gamestate = console.step() # Steps to the next frame.
    # If we're not in any gamestate yet, no need to run rest of loop for now.
    if gamestate is None:
        continue
    # Checks whether we're in a match.
    if (gamestate.menu_state in [melee.Menu.IN_GAME, melee.Menu.SUDDEN_DEATH]):

        # Changes values in playerButtons
        playerButtons[0] = int(gamestate.player[2].controller_state.button[Button.BUTTON_A])
        playerButtons[1] = int(gamestate.player[2].controller_state.button[Button.BUTTON_B])
        playerButtons[2] = int(gamestate.player[2].controller_state.button[Button.BUTTON_X])
        playerButtons[3] = int(gamestate.player[2].controller_state.button[Button.BUTTON_Y])
        playerButtons[4] = int(gamestate.player[2].controller_state.button[Button.BUTTON_Z])
        playerButtons[5] = int(gamestate.player[2].controller_state.button[Button.BUTTON_L])
        playerButtons[6] = int(gamestate.player[2].controller_state.button[Button.BUTTON_R])
        playerButtons[7] = int(gamestate.player[2].controller_state.button[Button.BUTTON_D_UP])
        playerButtons[8] = int(gamestate.player[2].controller_state.button[Button.BUTTON_D_DOWN])
        playerButtons[9] = int(gamestate.player[2].controller_state.button[Button.BUTTON_D_LEFT])
        playerButtons[10] = int(gamestate.player[2].controller_state.button[Button.BUTTON_D_RIGHT])
        playerButtons[11] = (gamestate.player[2].controller_state.main_stick[0]) # main stick x value (0 to 1)
        playerButtons[12] = (gamestate.player[2].controller_state.main_stick[1]) # main stick y value (0 to 1)
        playerButtons[13] = (gamestate.player[2].controller_state.c_stick[0]) # c stick x value (0 to 1)
        playerButtons[14] = (gamestate.player[2].controller_state.c_stick[1]) # c stick y value (0 to 1)
        playerButtons[15] = (gamestate.player[2].controller_state.l_shoulder) # l shoulder bumper (0 to 1)
        playerButtons[16] = (gamestate.player[2].controller_state.r_shoulder) # r shoulder bumper (0 to 1)

        # # Send OSC message to Pure Data
        client.send( OSCMessage(playerAdd, playerButtons))

        # print(gamestate.player[2].controller_state)  # This will print a snapshot of all inputs (string)

    # If we're not in a match (e.g. menu, score screen)
    else:
        # If we're in the menu, then control is passed to the menu helper.
        # This allows us to quickly navigate to the character select screen.
        melee.MenuHelper.menu_helper_simple(gamestate, # The current gamestate.
            controller_bot,                 # The bot's "controller".
            melee.Character.FOX,            # The bot's character.
            melee.Stage.BATTLEFIELD,  # Which stage to select.
            "",             # Connect code (left blank for local play).
            costume=1,      # The bot's color palette.
            autostart=False,# Whether player must press start to begin match.
            swag=False) # Whether bot annoys you while you choose your character.