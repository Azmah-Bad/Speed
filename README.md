# for educational purpose 

we worked on this together with my awesome classmate @NoelieG

To run our project you need to run the file FREAKOUT.py in a Python interpreter
(we used v3.8 but should work on all python versions)
but first the user experience is enhanced when the module 
pygame is installed which plays a smooth and relaxing music
for the players during the game (to disable it delete lines 173-175 and 265) but moodle can't handle more than 10 mo so we got rid of it. the programme imports all the data structures in assets.py where we stored useful functions and classes(Deck, Hand...) so make sure they are on the same directory.

The User Interface needs the images and sound stored in the directory Assets.

PS :In Pycharm you would have the have the right configuration set up because it uses (venv) so it can find the directory Asset.

Once you run the program it askes for number of players then you can start playing 


Have Fun !

Note : the parent process is suppose to kill all the child processes when the game ends (Line 258) but it doesn't so please terminate them. (We tried terminating them using the terminate() method but it doesnt work, we think it's because of the UI)

