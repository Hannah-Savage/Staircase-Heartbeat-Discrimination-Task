# PSS - Heartbeat Discrimination Task (HDT)
# -----------------------------------
# Code written by Hannah Savage, October 2024

"""
This PsychoPy script implements the Staircase - Heartbeat Discrimination Task (S-HDT). 
The task assesses the participants' perception of the simultaneity between auditory stimuli and their own heartbeat.

Key Components:
- **Integration Options**: The script includes toggles to determine if it is integrated with external hardware (Spike2) or a larger toolkit (EM-BODY).
- **Staircase Methodology**: Utilizes the staircase method for adaptive psychophysical testing, allowing the experiment to adjust the difficulty based on the participant's responses.
- **Visual Stimuli**: Employs the PsychoPy `visual` module to present instructions, countdowns, and feedback.
- **Data Logging**: Records participant responses and other relevant data into a TSV file for later analysis.

Script Breakdown:
- **Setup Variables**: 
  - `is_integrated_external`: Toggle for integrating with external devices.
  - `is_integrated_toolbox`: Toggle for integration with the EM-BODY toolkit.
  - `save_dir` and `participant_id`: Specify save path and participant ID if not integrated.
  - `if_debug`: Debug mode toggle for troubleshooting.

- **Environment Setup**: 
  - Imports necessary modules, sets up the window and monitor parameters, and initializes the serial port for external device communication if applicable.

- **Logging Mechanism**: 
  - Opens a CSV file to log the participant's responses and relevant trial information, writing headers for clarity.

- **Experiment Flow**: 
  - Displays instructions and a countdown before starting the trials.
  - Executes a loop through the staircase trials, collecting synchrony judgement and confidence ratings, and adjusting difficulty based on the staircase methodology
  - logs data for each trial.

- **Post-Trial Procedures**: 
  - Closes the CSV file and window after completing all trials, ensuring clean exit from the experiment.

Usage Notes:
- **Configuration**: Adjust `save_dir` and `participant_id` as needed if not using the integrated toolbox.
- **Serial Port Settings**: Modify the `port` and `baud_rate` based on your specific hardware setup for external device integration.
- **Debugging**: Enable the `if_debug` toggle to print additional information for troubleshooting.

"""

### ------- SET ENVIRONMENT ----- ###
import os
import csv
from psychopy import visual, event, core, monitors, data
import logging
import random
import serial
import yaml

from s_hdt_functions import wait_for_key_press, run_set_delay_trial, ask_run_another, run_staircase_trial, \
    get_numeric_input, get_confidence_mouse, get_post_task_qs, show_instructions_list


def run_s_hdt(is_integrated_external = True, is_integrated_toolbox = True, if_debug = False):
    logger = logging.getLogger(name=None)

    if is_integrated_toolbox:
        config_file_path = os.path.join(os.getcwd(), 'config.yaml')[2:]
        # Open and load the participants YAML file
        with open(config_file_path, 'r') as file:
            config_data = yaml.safe_load(file)

        # Access the 'Participant ID' from the loaded YAML data
        participant_id = config_data.get('Participant ID')
        save_dir = config_data.get('Behavioural Directory')
        print(save_dir)
    else:
        save_dir = directory
        participant_id = 'test01'
    logger.info(f'Participant ID loaded for s_hdt: {participant_id}')
    logger.info(f'Saving s_hdt data into: {save_dir}')

    ## ------Set Serial Port Parameters ------ ###
    if is_integrated_external:
        port = 'COM2'  # Adjust this to your specific COM port
        baud_rate = 9600  # Adjust baud rate as per your device's specification
        timeout = 1  # Timeout in seconds for reading the serial port
    # Initialize the serial port
        ser = serial.Serial(port, baud_rate, timeout=timeout)
        if ser.is_open:
            logger.info(f"Successfully connected to port {port}")
            print(f"Successfully connected to port {port}")
        else:
            logger.info(f"Failed to connect to port {port}")
            print(f"Failed to connect to port {port}")
            ser.open()
    else: 
        ser = None  # Dummy object in testing mode


    ### ------ LOGGING ----- ###
    # Open CSV file for writing (in append mode)
    base_name = f"sub-{participant_id}_s_hdt"
    base_path = os.path.join(save_dir, base_name)
    #csv_file_name = os.path.join(save_dir, 'sub-' +participant_id + '_s_hdt.tsv')

    # Check if the file already exists
    if os.path.exists(base_path + ".tsv"):
        # List all files in the directory
        existing_files = [f for f in os.listdir(save_dir) if f.startswith(base_name)]
        
        # Extract the suffixes to determine the next index
        indices = []
        for file in existing_files:
            if file == base_name + ".tsv":
                continue  # Skip the base file name
            if file.startswith(base_name + "_") and file.endswith(".tsv"):
                suffix = file[len(base_name) + 1 : -4]  # Extract the part after '_'
                if len(suffix) == 1 and suffix.isalpha():
                    indices.append(ord(suffix.lower()) - ord('a'))
        
        # Determine the next suffix (a/b/c...)
        next_index = 0 if not indices else max(indices) + 1
        next_suffix = chr(ord('a') + next_index)

        # Create the new file name
        csv_file_name = f"{base_name}_{next_suffix}.tsv"
        csv_file_name = os.path.join(save_dir, csv_file_name)

    else:
        # If no file exists, use the default name
        csv_file_name = base_name + ".tsv"
        csv_file_name = os.path.join(save_dir, csv_file_name)


    logger.info(f'CSV name: {csv_file_name}')
    print(csv_file_name)
    csv_file = open(csv_file_name, mode='a', newline='')
    csv_writer = csv.writer(csv_file, delimiter = '\t')
    # Write the header
    csv_writer.writerow(['Participant ID', participant_id])
    #csv_writer.writerow(['Date', datetime.now().strftime('%Y-%m-%d')])  
    #csv_writer.writerow(['Time', datetime.now().strftime('%H:%M:%S')]) 
    csv_writer.writerow(['Staircase_name', 'Trial', 'Current Delay', 'Button', 'Response_code', 'Confidence']) #Data columns
    csv_file.close()

    ### ------ WINDOW ----- ###
   ### ------ WINDOW ----- ###
    # Set up the window
    screen = monitors.Monitor('testMonitor')
    screen.setSizePix([1680, 1050])
    screen.setWidth(47.475)
    screen.setDistance(57)

    # Create a window
    desired_frame_rate = 60
    #win = visual.Window(size=(800, 600), color='white', units='pix')
    win = visual.Window(fullscr=True, color='white', units='pix')
    visual.text.Font = 'Arial'  

    ### ------ MODIFIABLE STAIRCASE PARAMETERS ----- ###
    """ Set up the staircase handler:
        data.StairHandler(
            startVal=X00.0,          # Initial value of the stimulus intensity for the first staircase.
            stepSizes=50,            # Size of each step in intensity; each adjustment will be 50 units.
            stepType='lin',          # Type of step changes; 'lin' indicates linear steps.
            nReversals=3,            # Number of reversals to conduct; aims for 3 points of direction change.
            nTrials=10,              # Total number of trials for this staircase.
            nUp=2,                   # Number of consecutive correct responses needed to increase intensity.
            nDown=2,                 # Number of consecutive incorrect responses needed to decrease intensity.
            minVal=0.0,              # Minimum allowed value for intensity; cannot go below 0.
            maxVal=1000.0,           # Maximum allowed value for intensity; cannot exceed 1000.
            originPath=-1,           # Identifier for the staircase path; -1 indicates undefined or placeholder.
            name='X00_1',            # Unique identifier for this staircase.
            applyInitialRule=False   # Whether to apply an initial adjustment rule before starting.
            MORE INFO: https://psychopy.org/_modules/psychopy/data/staircase.html
    """
    staircase_set = [data.StairHandler(startVal=400.0,
                                stepSizes=50, stepType='lin',
                                nReversals=3, 
                                nTrials=15, 
                                nUp=2, nDown=2,
                                minVal=0.0, maxVal=1000.0,
                                originPath=-1, name='400_1', 
                                applyInitialRule = False),
                    data.StairHandler(startVal=100.0,
                                stepSizes=50, stepType='lin',
                                nReversals=3, 
                                nTrials=15, 
                                nUp=2, nDown=2,
                                minVal=0.0, maxVal=1000.0,
                                originPath=-1, name='100_1',
                                applyInitialRule = False),
                   data.StairHandler(startVal=400.0,
                               stepSizes=50, stepType='lin',
                               nReversals=3, 
                               nTrials=15, 
                               nUp=2, nDown=2,
                               minVal=0.0, maxVal=1000.0,
                               originPath=-1, name='400_2', 
                               applyInitialRule = False),
                   data.StairHandler(startVal=100.0,
                               stepSizes=50, stepType='lin',
                               nReversals=3, 
                               nTrials=15, 
                               nUp=2, nDown=2,
                               minVal=0.0, maxVal=1000.0,
                               originPath=-1, name='100_2', 
                               applyInitialRule = False)
    ]
     
    ## ------ EXPERIMENT ----- ###
    instruction_text1 = ("In this task, we are interested in how well you can detect your heartbeats without manually feeling your pulse. "
                         "\n The computer will listen to 20 heartbeats at a time, and it will play a beep out loud on every second heartbeat, so it will skip a heartbeat, and you will hear 10 beeps. It either plays the beep at the same time as your heartbeat, slightly before, or slightly after." 
                         " \n \n Your task is to find out whether the beeps you hear happen before, at the same time, or after your heartbeat." )
    instruction_text2 = ("You will first see the heart on the screen which means the beeps are about to start." 
                         "\n If you'd like to close your eyes, you can use the heart as a sign to do that."
                         "\n\n Once the beeps have finished, please tell me whether you think the beeps were"
                         "\n “before”, “at the same time”, or “after” your heartbeat."
                        "\n Then, please tell me how confident you are in your decision on a scale from 0 (total Guess) to 100 (Certain).")
    instruction_text3 = ("The whole task takes about 30 minutes and you will be offered short breaks throughout."
                         "\n \n We will now do a practice trial, so you can hear some beeps and practice how to respond.")
    instruction_text4 = ("RESEARCHER:\nPress ENTER when you are ready to begin practice")
                                                
    instruction_1 = [win, instruction_text1, 'black', 20, 600, (0,0)]
    # wait_for_key_press(win, instruction_text)
    # win.flip()
    # logger.info("Instructions")
                          
    instruction_2 = [win, instruction_text2, 'black', 20, 600, (0,0)]
    # wait_for_key_press(win, instruction_text)
    # win.flip()
    # logger.info("Instructions")
                       
    instruction_3 = [win, instruction_text3, 'black', 20, 600, (0,0)]
    # wait_for_key_press(win, instruction_text)
    # win.flip()
    # logger.info("Instructions")

    #Wait for Enter press to start
    
    instruction_4 = [win, instruction_text4, 'black', 30, 800, (0,0)]
    # wait_for_key_press(win, instruction_text)
    # win.flip()

    instructions_list = [instruction_1, instruction_2, instruction_3, instruction_4]

    show_instructions_list(instructions_list, logger)

    ## TRAINING
    logger.info("Commencing Training")
    core.wait(0.5)
    # Start a 3-second countdown
    countdown_text = visual.TextStim(win, text='', color='black', height=20, pos=(0, 0))
    countdown_clock = core.Clock()
    while countdown_clock.getTime() < 3:
        countdown_text.setText(f"{3 - int(countdown_clock.getTime())}")
        countdown_text.draw()
        win.flip()
        core.wait(0.5)
        win.flip()
    
    train_values =  random.choices(range(0, 601, 50), k=20) # Random assortment of 20 values from 0 to 550
    # Run trials for each delay value
    for i, delay in enumerate(train_values):
        button, response_code = run_set_delay_trial(win, delay, ser, is_integrated_external, if_debug)
        confidence = get_numeric_input(win)
        #confidence = get_confidence_mouse(win)

        # Write trial information to the CSV file
        with open(csv_file_name, mode='a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter='\t')
                csv_writer.writerow(['Training', i + 1, delay, button, response_code, confidence])
                csv_file.close()
        logger.info(f"['Training', {i + 1}, {delay}, {button}, {response_code}, {confidence}]")

        # After the first trial, ask if they want to continue
        if i > 0:
            next_action = ask_run_another(win)
            if next_action == 'stop':
                print("Participant chose to stop training.")
                break  # Exit the loop if they choose to stop

    ### STAIRCASES
    # Wait for Enter press to start
    instruction_text = visual.TextStim(win, text="RESEARCHER:\nPress ENTER when you are ready to begin task.", color='black', height=30, wrapWidth=800, pos = (0,0))
    wait_for_key_press(win, instruction_text)
    win.flip()
    logger.info("Commencing Staircases")
    core.wait(0.5)
    # Start a 3-second countdown
    countdown_text = visual.TextStim(win, text='', color='black', height=20, pos=(0, 0))
    countdown_clock = core.Clock()
    while countdown_clock.getTime() < 3:
        countdown_text.setText(f"{3 - int(countdown_clock.getTime())}")
        countdown_text.draw()
        win.flip()
        core.wait(0.5)
        win.flip()
    
    # Loop through the staircases
    for index, staircase in enumerate(staircase_set):
        staircase_name = staircase.name

        #loop though the trials for that staircase
        for trial in range(staircase.nTrials):
            
            # Check for key presses
            keys = event.getKeys()
            # Exit if the Escape key is pressed
            if 'escape' in keys:
                csv_file.close()
                win.close()
                print("Escape key pressed. Exiting loop.")
                break
            # Exit if the staircase complete
            if staircase.finished:
                break

            current_delay = staircase.next()  # Get the next staircase value
            if if_debug:
                print(current_delay)
            button, response_code = run_staircase_trial(win, current_delay, ser, is_integrated_external, if_debug)
            if response_code == -1:
                # When response code is -1, repeat the trial by not calling addResponse
                # Optionally, you could choose to log this or handle it differently
                if if_debug:
                    print("Response code is -1: repeating the trial.")
                # This continues to the next iteration without modifying the staircase
            else:
                # If response is valid (0 or 1), add the response to the staircase
                staircase.addResponse(response_code)
            #confidence = get_confidence_mouse(win)
            confidence = get_numeric_input(win)

            # Write trial information to the CSV file
            with open(csv_file_name, mode='a', newline='') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter='\t')
                csv_writer.writerow([staircase_name, trial + 1, current_delay, button, response_code, confidence])
                csv_file.close()      
            logger.info(f"[{staircase_name}, {trial + 1}, {current_delay}, {button}, {response_code}, {confidence}]")

        if index < len(staircase_set) - 1:  # 
            #Break between staircases
            instruction_text = visual.TextStim(win, text="Press ENTER when you are ready to continue", color='black', height=30, wrapWidth=800, pos = (0,0))
            wait_for_key_press(win, instruction_text)
            staircase_text = visual.TextStim(win, text='Continuing', pos=(0, 0), color='black', height=20)
            staircase_text.draw()
            win.flip()
            core.wait(1)
            # Start a 3-second countdown
            countdown_text = visual.TextStim(win, text='', color='black', height=20, pos=(0, 0))
            countdown_clock = core.Clock()
            while countdown_clock.getTime() < 3:
                countdown_text.setText(f"{3 - int(countdown_clock.getTime())}")
                countdown_text.draw()
                win.flip()
                core.wait(0.5)

    ##Post - task questions 
    get_post_task_qs(win, csv_file_name, csv_writer, use_mouse=True)
    win.flip()
    task_complete = visual.TextStim(win, text='Task complete', pos=(0, 0), color='black', height=20) 
    task_complete.draw()
    win.flip()
    core.wait(2)

    # Close the window after the trials are completed
    win.close()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M',
                        filename='s_hdt.log',
                        filemode='w')
    logger = logging.getLogger(__name__)

    config_file_path = os.path.join('config.yaml')
    directory = os.getcwd()
    save_dir = directory
    # Format the data as a dictionary for structured output
    data_to_write = {
        'Participant ID': '001',
        'Home Directory': directory,
        'Behavioural Directory': directory,
        'Log Directory': directory}
    with open(config_file_path , 'w') as file:
        yaml.dump(data_to_write, file, sort_keys=False)

    run_s_hdt()