import melee    # Package for everything related to smash bros melee
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
player = "/player"  # player address
enemy = "/enemy"    # opponent address
# Character info ordered as:
# x, y, on_ground, off_stage, on_platform
playerinfo = [0, 0, 0, 0, 0]
enemyinfo = [0, 0, 0, 0, 0]
# This will make more sense later, when a message is sent.

# Creates a console object that represents Slippi Online / Dolphin instance.
console = melee.Console(path="C:/Users/Michael/Documents/_Spring 2021/Music and Tech 2/FM-Slippi-2.2.5-Win")
# Note: File path must use forward slashes or double back slashes.
#       Single back slashes will result in unicode error.
# Creates controller objects for the bot (port 1) and the human (port 2).
controller_bot = melee.Controller(console=console, port=1)
controller_human = melee.Controller(console=console,
                                    port=2,
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
        #####################################
        # Sending OSC messages to Pure Data #
        #####################################        
        playerinfo[0] = int(gamestate.player[2].x)
        playerinfo[1] = int(gamestate.player[2].y)
        playerinfo[2] = int(gamestate.player[2].on_ground) # boolean
        playerinfo[3] = int(gamestate.player[2].off_stage) # boolean
        # I'm defining "on_platform" as having a Y position > 1 
        #  while still being considered "on_ground".
        if (playerinfo[1] > 1 and playerinfo[2] == 1): 
            playerinfo[4] = 1
        else:
            playerinfo[4] = 0
        # msg.add_arg(int(gamestate.player[2].percent))
        # msg.add_arg(int(gamestate.player[2].stock))

        enemyinfo[0] = int(gamestate.player[1].x)
        enemyinfo[1] = int(gamestate.player[1].y)
        enemyinfo[2] = int(gamestate.player[1].on_ground) # boolean
        enemyinfo[3] = int(gamestate.player[1].off_stage) # boolean
        # I'm defining "on_platform" as having a Y position > 1 
        #  while still being considered "on_ground".
        if (enemyinfo[1] > 1 and enemyinfo[2] == 1): 
            enemyinfo[4] = 1
        else:
            enemyinfo[4] = 0

        client.send( OSCMessage(player, playerinfo))
        client.send( OSCMessage(enemy, enemyinfo))

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