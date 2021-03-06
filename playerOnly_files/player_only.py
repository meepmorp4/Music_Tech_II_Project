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

# OSC addresses
playerAdd = "/playerState"          # for gamestate info
enemyAdd = "/enemyState"            # for gamestate info
playerInputAdd = "/playerInput"     # for actual inputs
enemyInputAdd = "/enemyInput"       # for actual inputs

# Character gamestate info ordered as:
# x, y, percent, shield_strength, stock, 
# facing, action, action_frame, invulnerable, invulnerability_left
# hitlag_left, hitstun_frames_left, jumps_left, on_ground, on_platform
# speed_air_x_self, speed_x_ground_self, speed_y_self, speed_x_attack, speed_y_attack
playerState = [ 0, 0, 0, 0, 0,
                0, 0, 0, 0, 0,
                0, 0, 0, 0, 0,
                0, 0, 0, 0, 0]

# Get gamestate 
def get_gamestate(states_list, port):
    states_list[0] = int(gamestate.player[port].x)  # position_x
    states_list[1] = int(gamestate.player[port].y)  # position_y
    states_list[2] = int(gamestate.player[port].percent)  # percent
    states_list[3] = int(gamestate.player[port].shield_strength)  # shield_strength
    states_list[4] = int(gamestate.player[port].stock)  # stock
    
    states_list[5] = int(gamestate.player[port].facing)  # facing (bool; L=False, R=True)
    #states_list[6] = gamestate.player[port].action  # action (enum.Action)
    states_list[7] = int(gamestate.player[port].action_frame)  # action_frame
    states_list[8] = int(gamestate.player[port].invulnerable)  # invulnerable (bool)
    states_list[9] = int(gamestate.player[port].invulnerability_left)  # invulnerability_left
    
    #states_list[10] = int(gamestate.player[port].hitlag_left)  # hitlag_left (bool)
    states_list[11] = int(gamestate.player[port].hitstun_frames_left)  # hitstun_frames_left
    states_list[12] = int(gamestate.player[port].jumps_left)  # jumps_left
    states_list[13] = int(gamestate.player[port].on_ground)  # on_ground (bool)
    states_list[14] = int(states_list[1] > 1 and states_list[2] == 1)  # on_platform (bool)

    states_list[15] = gamestate.player[port].speed_air_x_self  # speed_air_x_self
    states_list[16] = gamestate.player[port].speed_ground_x_self  # speed_ground_x_self
    states_list[17] = gamestate.player[port].speed_y_self  # speed_y_self
    states_list[18] = gamestate.player[port].speed_x_attack  # speed_x_attack
    states_list[19] = gamestate.player[port].speed_y_attack # speed_y_attack

# Button inputs ordered as:
# A, B, X, Y, Z, L, R, D_UP, D_DOWN, D_LEFT, D_RIGHT, (11 booleans)
# main_stick_x, main_stick_y, c_sticK_x, c_stick_y, l_shoulder, r_shoulder (6 floats)
playerInput = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
enemyInput = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
def get_inputs(input_list, port):
    input_list[0] = int(gamestate.player[port].controller_state.button[Button.BUTTON_A])
    input_list[1] = int(gamestate.player[port].controller_state.button[Button.BUTTON_B])
    input_list[2] = int(gamestate.player[port].controller_state.button[Button.BUTTON_X])
    input_list[3] = int(gamestate.player[port].controller_state.button[Button.BUTTON_Y])
    input_list[4] = int(gamestate.player[port].controller_state.button[Button.BUTTON_Z])
    input_list[5] = int(gamestate.player[port].controller_state.button[Button.BUTTON_L])
    input_list[6] = int(gamestate.player[port].controller_state.button[Button.BUTTON_R])
    input_list[7] = int(gamestate.player[port].controller_state.button[Button.BUTTON_D_UP])     # D-pad up
    input_list[8] = int(gamestate.player[port].controller_state.button[Button.BUTTON_D_DOWN])   # D-pad down
    input_list[9] = int(gamestate.player[port].controller_state.button[Button.BUTTON_D_LEFT])   # D-pad left
    input_list[10] = int(gamestate.player[port].controller_state.button[Button.BUTTON_D_RIGHT]) # D-pad right
    input_list[11] = (gamestate.player[port].controller_state.main_stick[0]) # main stick x value (0 to 1)
    input_list[12] = (gamestate.player[port].controller_state.main_stick[1]) # main stick y value (0 to 1)
    input_list[13] = (gamestate.player[port].controller_state.c_stick[0]) # c stick x value (0 to 1)
    input_list[14] = (gamestate.player[port].controller_state.c_stick[1]) # c stick y value (0 to 1)
    input_list[15] = (gamestate.player[port].controller_state.l_shoulder) # l shoulder bumper (0 to 1)
    input_list[16] = (gamestate.player[port].controller_state.r_shoulder) # r shoulder bumper (0 to 1)

# THESE ONLY APPLY TO BATTLEFIELD
# Stage ledge positions [X,Y]
ledge_left = [-68.4, 0]
ledge_right = [68.4, 0]
# Platform CENTER positions [X,Y], calculated using left edge and width
width = 37.6
plat_left = [-57.6+(width/2), 27.2]
plat_top = [0, 54.4]
plat_right = [20+(width/2), 27.2]

def plat_check (input_list, state_list, port):
    if (input_list[8]):     # if D-pad down is pressed
        if (state_list[0] < 0): # character is on left side of stage
            ordered = [plat_left[0], plat_left[1],
                        plat_top[0], plat_top[1],
                        plat_right[0], plat_right[1]]
        else: # player is on right side of the screen
            ordered = [plat_right[0], plat_right[1],
                        plat_top[0], plat_top[1],
                        plat_left[0], plat_left[1]]
        client.send( OSCMessage("/platforms", ordered) )
        # print(ordered)


# Port assignment
playerPort = 2
enemyPort = 1

# Creates a console object that represents Slippi Online / Dolphin instance.
console = melee.Console(path="C:/Users/Michael/Documents/_Spring 2021/Music and Tech 2/FM-Slippi-2.2.5-Win")
# Note: File path must use forward slashes or double back slashes.
#       Single back slashes will result in unicode error.
# Creates controller objects for the bot (port 1) and the human (port 2).
controller_bot = melee.Controller(console=console, port=enemyPort)
controller_human = melee.Controller(console=console, port=playerPort,
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
        get_gamestate(playerState, playerPort)
        get_inputs(playerInput, playerPort)

        client.send( OSCMessage(playerAdd, playerState))
        client.send( OSCMessage(playerInputAdd, playerInput))

        plat_check(playerInput, playerState, playerPort)

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