import state_machine
import user_input
import pythonosc
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server


IP = "127.0.0.1"

PORT_TO_MAX = 7980
client = udp_client.SimpleUDPClient(IP, PORT_TO_MAX)


global curr_window
global midi_in
all_midi_in = []
curr_window = []


# global sm
# global user_in
sm = state_machine.State_Machine()
user_in = user_input.User_Input()

# def print_test():
#     global curr_window
#     print("curr window is" + str(curr_window))
#     curr_window = []

def update_wrapper():
    # global sm
    # global user_in
    user_in.update_probabilities()
    sm.check_state(user_in.get_probabilities())
    user_in.update_window()
    

def process_midi(address, *args):
    global curr_window
    global all_midi_in
    # global sm
    # global user_in
    pitch = args[0]
    ms = args[1]
    vel = args[2]
    # fill the curr window and full turn
    user_in.fill_window(pitch, ms, vel)
    # all_midi_in.append((pitch, ms, vel))
    # curr_window.append((pitch, ms, vel))

# dispatcher to receive message
disp = dispatcher.Dispatcher()
disp.map('/listen', process_midi)

timer = state_machine.RepeatedTimer(interval=4, function=update_wrapper)
# server to listen
server = osc_server.ThreadingOSCUDPServer((IP,1980), disp)
print("Serving on {}".format(server.server_address))
server.serve_forever()