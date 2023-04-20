import state_machine
import user_input
import genetic_alg
import pythonosc
from pythonosc import udp_client
from pythonosc import dispatcher
from pythonosc import osc_server
import time
import threading


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

ga_flag = False
switch_flag = False
state_flag = "follower"

# def print_test():
#     global curr_window
#     print("curr window is" + str(curr_window))
#     curr_window = []

def update_wrapper():
    # global sm
    # global user_in
    global ga_flag
    global state_flag
    global switch_flag
    global client
    if user_in.curr_user_turn == []:
        print("waiting for user")
        user_in.update_probabilities()
        # user_in.update_window()
    if switch_flag:
        print("waiting role switch")
        user_in.reset_windows()
        # user_in.update_probabilities()
        # user_in.update_window()
        switch_flag = False
    else:
        user_in.update_probabilities()
        print('Current state is: ' + str(state_flag))
        state_change = sm.check_state(user_in.get_probabilities())
        if state_change == 'leader':
            ga_flag = True
            switch_flag = True
            state_flag = 'leader'
            print("Starting GA")
            call_ga(user_in.prev_window, client)
            user_in.update_window()
        elif state_change == 'follower':
            ga_flag = False
            switch_flag = True
            state_flag = 'follower'
            print("stop ga")
            # user_in.curr_user_turn = []
            user_in.reset_windows()
        else:
            user_in.update_window()


timer = state_machine.RepeatedTimer(interval=5, function=update_wrapper)

def call_ga(ga_target, client):
    #TODO: Fix the need for pitch options and rhythm options
    pitch_options = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    tpb = 200
    bpm = 120
    # 32nd note, triplet 16th, 16th note, triplet 8th, 8th note, triplet quarter, quarter note, dotted quarter, half note, dotted half, whole
    rhythm_options = [tpb/8, int((tpb/4) * .66), tpb/4, int(tpb/2 * .66), tpb/2, int(tpb * .66), tpb, (tpb + tpb/2), tpb * 2, (tpb * 2) + tpb, tpb * 4]
    
    global ga_flag
    # start_ind = 0
    # ga_target_len = len(ga_target)
    # loop over each window of the user's last turn
    world_ga = genetic_alg.world(ga_target, "jazz_licks.txt", pitch_options, rhythm_options)
    gen = 0
    while ga_flag:
        print("Running GA")
        world_ga.run()
        world_ga.play_melodies(client=client, gen=gen)
        gen = gen + 1
        # start_ind = (start_ind + 1) % (ga_target_len - 1)
        # world_ga.reinit(ga_target, "jazz_licks.txt", pitch_options, rhythm_options)

def process_midi(address, *args):
    global curr_window
    global all_midi_in
    # global sm
    # global user_in
    pitch = int(args[0])
    ms = args[1]
    vel = args[2]
    # fill the curr window and full turn
    user_in.fill_window(pitch, ms, vel)
    # all_midi_in.append((pitch, ms, vel))
    # curr_window.append((pitch, ms, vel))

# dispatcher to receive message
disp = dispatcher.Dispatcher()
disp.map('/listen', process_midi)
print("Dispatcher mapped to listen to user")

# timer = state_machine.call_repeatedly(interval=5, func=update_wrapper)
# server to listen
server = osc_server.ThreadingOSCUDPServer((IP,1980), disp)
print("User Listenining serving on {}".format(server.server_address))
server.serve_forever()
