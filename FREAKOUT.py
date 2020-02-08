import multiprocessing
import threading
import os
from tkinter import messagebox
import sysv_ipc
import signal
from assets import *  # a local file with all the data structures needed for everything to run
import time
import tkinter as tk
#from pygame import mixer  # game sound file was too big for moodle 
from tkinter import *

Key = 3001  # MQ key
CountDown = 20  # a seperate thread takes this variable and increment it every 1 sec if the player press a button


# it reset back to 10 if it gets to 0 tho notifies the parent process that this player times out so he punish the
# player


def player(ID, Pipe):
    print(f"Player {ID}")

    CDlock = threading.Lock()  # this lock protect CountDown, it needed because CountDown is shared between 2 threads
    # 1 that increment it and buttons that reset it

    mq = sysv_ipc.MessageQueue(Key)  # Father's Message Queue
    hand, top_deck = Pipe.recv()  # First hand and topdeck

    lock = threading.Lock()  # this lock protect hand and top_deck

    # GUI
    window = Tk()  # creating the window
    window.iconbitmap(
        r"Assets/icon.ico")  # window icon (i cant get it to work tho :()
    window.title(f"SPEED Player {ID}")
    # window.resizable(0, 0)  # make the window unexpandable

    # background image stuff
    background_image = tk.PhotoImage()
    background_image.config(
        file='Assets/2 background.png' if ID == 0 else 'Assets/player3.png')  # this is probably a copyrighted image too
    background_label = tk.Label(window, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

    # set the window as big as background image
    windowsize = str(background_image.width()) + "x" + str(background_image.height())
    window.geometry(windowsize)

    frame = Frame(window)

    ButtonFram = Frame(window)

    # display topdeck
    topdeck = Label(window, text="the card on the board :", font=("Courrier", 30), bg='#46ad15', fg="white")
    topdeck.pack(side=TOP)

    topdeckimg = tk.PhotoImage(file=top_deck.image)
    topdeckimg_label = tk.Label(window, image=topdeckimg)
    topdeckimg_label.pack(side=TOP)

    displayedhand = Label(frame, text="Your hand :", font=("Helvetica", 30), bg='#46ad15', fg='white')
    displayedhand.pack(expand=YES, fill=Y, side=LEFT)

    # Buttons part
    def move(card, CDlock):  # cards button command
        def played():
            with CDlock:
                global CountDown
                CountDown = 20
                CountdownWidget.config(text=CountDown)
            print(f"Player {ID} played {card}")
            mq.send(card.toBytes() + str(ID).encode())

        return played  # this weired implemntation is because the tkinter framwork only handles "callbacks" with no

    # arguments to get around this we made this function that return a function with no argument but before we set the
    # up the fonction context

    images = [tk.PhotoImage(file=card.image) for card in
              hand.hand]  # Buttons' images
    Buttons = [Button(ButtonFram, text=hand.hand[i], image=images[i], command=move(hand.hand[i], CDlock)) for i in
               range(len(hand.hand))]
    list(map(lambda x: x.pack(side=RIGHT), Buttons))  # pack the buttons

    # CountDown GUI
    CountdownWidget = Label(window, text=CountDown,
                            bg="#07f76f" if CountDown < 3 else "#ed3b7f",
                            font=("Helvetica", 30), fg="white")  # timers color turns red if <3sec left
    CountdownWidget.pack(side=TOP)

    frame.pack(expand=True)

    ButtonFram.pack(side=RIGHT, expand=True)

    timeoutstatus = True

    def timeout(lock):
        """"This function is called as a thread and it's role is to incriment CountDown every second
        if it notice that CountDown = 0 that means that the player hasn't played in 20 sec so it sends
        the borad process a message in it's MQ to notify it that this player has timedout the board then punishes the
         player"""
        while timeoutstatus:
            global CountDown
            time.sleep(1)
            try:
                with lock:
                    CountDown -= 1
                    CountdownWidget.config(text=CountDown, bg="#ed3b7f" if CountDown < 3 else "#07f76f")
                    if CountDown == 0:
                        mq.send(f"T{ID}".encode())
                        CountDown = 20
            except RuntimeError:
                # UI has been closed
                break

    threading.Thread(target=timeout, args=(CDlock,)).start()
    PipeWatchdogStatus = True

    def PipeWatchdog(
            lock,
            Buttons):
        """
        this thread updates  the topdeck and hand as soon as the parent process send new ones in the pipe
        """
        while PipeWatchdogStatus:
            currhand, currtop_deck = Pipe.recv()  # the recv methode stop the execution till there's something in the
            # pipe so to not keep the lock locked we store first the new data on a variable then wait for the lock
            # and then changing the actual hand and topdeck
            print(currhand, currtop_deck)
            with lock:
                hand, top_deck = currhand, currtop_deck  # update hand topdeck
                # update the UI
                try :
                    topdeckimg.config(file=top_deck.image)  # update the TopDeck image
                    i = 0
                    for button in Buttons:  # delete all previous buttons
                        button.pack_forget()

                        # load images of the new buttons
                    images = [tk.PhotoImage(file=card.image) for card in
                              hand.hand]
                    Buttons = [Button(ButtonFram, text=hand.hand[i], image=images[i], command=move(hand.hand[i], CDlock))
                               for i in
                               range(len(hand.hand))]
                    for button in Buttons:
                        button.pack(side=RIGHT)
                except RuntimeError: # the UI has been closed
                    break

    PipeWatchdogThread = threading.Thread(target=PipeWatchdog, args=(lock, Buttons))
    PipeWatchdogThread.start()  # starts the thread bellow 

    def handler(sig, frame):
        """ 
        this handles SIGUSR1 which is sent when a move has been terminated by the borad
        """
        if sig == signal.SIGUSR1:
            messagebox.showinfo(f"{ID}You move hasn't been registered", "Too slow")
            # notify the player of what happened 

    signal.signal(signal.SIGUSR1, handler)

    window.mainloop()  # WRAP IT UP
    # this is read after the UI is closed
    timeoutstatus = False
    PipeWatchdogStatus = False  # kills threads


if __name__ == '__main__':
    # delete this if pygame isn't installed
        
    #mixer.init()
    #mixer.music.load('Assets/game sound.wav')
    #mixer.music.play()  # this a copyrighted music btw

    PLAYERNUM = int(input("Number of players ?"))

    deck = Deck(PLAYERNUM)  # generate more cards if there's more too many players
    hands = []  # a list of all the hands
    Pipes = []  # a list of all the pipes needed for each process

    for _ in range(PLAYERNUM):
        hands.append(Hand(deck.pick(5)))
        Pipes.append(multiprocessing.Pipe())

    Process = [multiprocessing.Process(target=player, args=(ID, Pipes[ID][1])) for ID in range(PLAYERNUM)]


    def updateChildren():
        """mainly for clarity purposes, send all the children there hand and topdeck in there pipes"""
        for i in range(PLAYERNUM):
            Pipes[i][0].send((hands[i], top_deck))  # sends all the players there new hands and topdeck


    # Pipes is a list of tuples (ParentPipe,ChildPipe) so Pipes[ID][1] returns ChildPipe

    top_deck = deck.pick()[0]  # selecting the topdeck (note deck.pick() returns a list )

    print("Game starts!")
    print(f"first card is {str(top_deck)}")

    for pro in Process:
        pro.start()

    mq = sysv_ipc.MessageQueue(Key, sysv_ipc.IPC_CREAT)

    updateChildren()  # Once the children are born we send them there first hand and topdeck

    while mq.current_messages != 0:  # emptying the mq before the game starts
        mq.receive()

    while True:
        message, t = mq.receive()  # messages in mq are in the following format cardID if the player played a move
        # or TID if he time out 
        message = message.decode()  # bytes to string
        ID = int(message[-1])  # ID is the last digit on the string 
        message = message[:-1]  # left ove is the message 

        if message[0] == "T":  # one of the players didnt play in 10 sec
            hands[ID].add_cards(deck.pick())  # add to his hand a new card


        else:  # It's not a time out someone actually made a move 
            receivedCard = bytestoCard(message)
            # this function turns the string into a Card object
            print("received :", receivedCard, "from ", ID)  # Debugging purposes 

            if receivedCard in top_deck.nextvalidmove():  # the move is valid
                print("GOOD MOVE")
                FaultyIDs = []
                while mq.current_messages != 0:  # emptying the mq
                    message, t = mq.receive()
                    loserid = int(message.decode()[-1])  # getting all the ID's left on the mq
                    FaultyIDs.append(loserid)  # storing them in a list
                FaultyIDs = list(dict.fromkeys(FaultyIDs))  # removes duplicates
                if ID in FaultyIDs:
                    FaultyIDs.remove(ID)  # remove the winners id from this list

                # send faulty players SIGUSR1 to notify them they were slow

                for FaultyID in FaultyIDs:
                    os.kill(Process[FaultyID].pid, signal.SIGUSR1)

                hands[ID].discard_card(receivedCard)  # remove the played card from his hand
                if hands[ID].DidWin():  # check if he won
                    messagebox.showinfo("END GAME", f"PLayer {ID} has WON :)")
                    map(lambda x: x.terminate, Process)  # kill the CHILDREN
                    break

                top_deck = receivedCard  # updating the topdeck

            else:  # a player has made a mistake
                print(f"Mistakes have been made {ID}")

                if deck.AllLost():
                    messagebox.showinfo("GAME OVER", "All players lost")
                    map(lambda x: x.terminate, Process)  # kill the CHILDREN (it doesn't work tho)
                    Status = False
                    break

                hands[ID].add_cards(deck.pick())  # adding a random card to his hand

        updateChildren()
    #mixer.music.stop()  # pointless without pygame
    
