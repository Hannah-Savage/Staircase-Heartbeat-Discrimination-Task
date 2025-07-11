import random
from psychopy import visual, event, core, monitors, data
import csv

def wait_for_key_press(win, instruction_text):
    """
    Presents an instruction on the screen and waits for 'RETURN' key press to proceed

     Parameters
    ----------
    win : visual.Window() object
    
     Examples
    ----------
    win = visual.Window(fullscr=False, color='white', units='pix')
    
    """
    
    while True:
        instruction_text.draw()
        win.flip()
        # event.waitKeys(keyList=['return'])

        # Check for Enter key press to break the loop
        keys = event.getKeys()
        if 'return' in keys:
            break

        # Check for escape key press to exit
        if 'escape' in keys:
            core.quit() 


def show_instructions(win, instruction_text, color, height, wrapWidth, position):
    """
    Presents an instruction on the screen and waits for 'RETURN' key press to proceed

     Parameters
    ----------
    win : visual.Window() object

     Examples
    ----------
    win = visual.Window(fullscr=False, color='white', units='pix')

    """
    # Create the instruction text stimulus
    instructions = visual.TextStim(
        win=win,
        text=instruction_text,
        color=color,
        height=height,
        wrapWidth=wrapWidth,
        pos=position
    )

    while True:
        instructions.draw()
        win.flip()

        keys = event.getKeys()
        if 'escape' in keys:
            core.quit()

        if 'left' in keys:
            return 'previous'  # Exit loop if left arrow key is pressed

        if 'return' in keys:
            return 'next'  # Exit loop if enter is pressed

def show_instructions_list(instructions_list, logger):
    """
        Displays a list of instruction pages sequentially, moving to the next page when the right arrow key is pressed,
        and to the previous page when the left arrow key is pressed.

        Parameters:
        instructions_list (list): A list of tuples, each containing parameters for the show_instructions function.
        """
    index = 0  # Initialize the index to display the first instruction
    while index < len(instructions_list):
        result = show_instructions(*instructions_list[index])
        logger.info(f"Instructions_{index + 1}")
        if result == 'next':
            index += 1  # Move to the next instruction in the list
        elif result == 'previous' and index > 0:
            index -= 1  # Move to the previous instruction in the list

from psychopy import visual, event

def get_numeric_input(win):
    """
    Allows participants to enter a value between 0 and 100 in a text box.
    Press Enter to confirm the input.
    
    Args:
        win: PsychoPy visual.Window object.
    
    Returns:
        int: The value entered by the participant (0-100).
    """
    # Initialize an empty string to hold the input
    input_text = ''
    
    instructions = visual.TextStim(win, text="How confident are you from 0 (Guess) to 100 (Certain)?", pos=(0, 50), color="Black", height=20)
    
    # Create a TextStim to display the current input
    input_display = visual.TextStim(
        win,
        text="",
        pos=(0, 0),
        color='Black',
        height=20
    )
    
    # Create a rectangle to serve as the text box background
    text_box = visual.Rect(
        win,
        width=50,
        height=35,
        fillColor='lightgrey',  # Light grey box for contrast
        lineColor='black',  # Black border
        pos=(0, 0)
    )

    # Display the stimuli and handle input
    while True:
        # Draw the instructions and current input
        instructions.draw()
        text_box.draw()
        input_display.setText(input_text)
        input_display.draw()
        win.flip()
        
        keypad_mapping = {
        "num_0": "0", "num_1": "1", "num_2": "2", "num_3": "3",
        "num_4": "4", "num_5": "5", "num_6": "6", "num_7": "7",
        "num_8": "8", "num_9": "9"
        }
        
        # Get key presses
        keys = event.waitKeys(
            keyList=[
                "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",  # Main keyboard digits
                "num_0", "num_1", "num_2", "num_3", "num_4", "num_5", "num_6", "num_7", "num_8", "num_9",  # Numeric keypad digits
                "backspace", "return", 
                "escape" # To exit task
            ]
        )

        for key in keys:
            if key == "return":
                # Confirm the input when Enter is pressed
                if input_text.isdigit() and 0 <= int(input_text) <= 100:
                    return int(input_text)
                else:
                    # Display an error message if input is invalid
                    error_message = visual.TextStim(
                        win,
                        text="INVALID INPUT. \n Please enter a number between 0 and 100.",
                        pos=(0, -50),
                        color='red',
                        height=20
                    )
                    for _ in range(60):  # Show the error for a short duration (about 1 second at 60 Hz)
                        instructions.draw()
                        input_display.draw()
                        error_message.draw()
                        win.flip()
            elif key == "backspace":
                # Remove the last character when Backspace is pressed
                input_text = input_text[:-1]
            elif key in keypad_mapping:  # If the key is from the numeric keypad
                if len(input_text) < 3:  # Limit to 3 characters (max is "100")
                    input_text += keypad_mapping[key]
            elif key == "escape":
                core.quit()
            else:  # Handle regular digit keys
                if len(input_text) < 3:  # Limit to 3 characters (max is "100")
                    input_text += key


def get_confidence_mouse(win):
    """
    Collects the participant's confidence rating about their response.

    Parameters
    ----------
    win : visual.Window
        PsychoPy window object used to present stimuli.

    Returns
    -------
    float
        The final position of the slider, representing the participant’s confidence rating on a scale from 0 to 100.
    
    Notes
    -----
    This function displays a text prompt and a slider for the participant to indicate their confidence in their response. 
    The slider has three ticks at 0, 50, and 100, corresponding to "Guess," an empty label, and "Certain," respectively. 
    The initial slider position is randomized between 20% and 80%. 
    Participants can adjust the slider by moving the mouse, with the slider's position constrained between 0 and 100.
    """

    # Create a slider with a marker
    slider = visual.Slider(win, ticks=(0, 100), labels=["Guess", "Certain"], granularity=1,
                           style=['rating'], pos=(0, 0), size=(400, 20),
                           labelHeight=20, color="Black")

    # Randomize initial slider position between 20% and 80%
    initial_position = random.uniform(20, 80)
    slider.markerPos = initial_position
    line = visual.Line(win, start=(-200, -5), end=(200, -5), lineColor=(0.5, 0.5, 0.5), lineWidth=5)
    
    # Instruction text
    instruction = visual.TextStim(win, text="How confident are you? (0-100)", pos=(0, 50), color="Black", height=20)

    # Response collection loop
    response = None
    mouse = event.Mouse(win=win)

    while response is None:
        instruction.draw()
        line.draw() 
        slider.draw()
        win.flip()

        keys = event.getKeys()
        if 'escape' in keys:
            core.quit()

        # Check for mouse click
        if mouse.getPressed()[0]:  # Left mouse click
            response = slider.markerPos
            #print(f"Confidence rating = {response}")
            core.wait(1)  # Wait 1 second before ending
            break

        # Update the slider marker position with mouse movement
        mouse_x, _ = mouse.getPos()
        slider_value = (mouse_x + 300) / 6  # Mapping mouse_x to range 0-100
        if 0 <= slider_value <= 100:  # Ensure the value is within bounds
            slider.markerPos = slider_value

        event.clearEvents(eventType='keyboard')

    return response

def run_set_delay_trial(win, current_delay, ser, is_integrated_external, if_debug):
    """
    Runs a single trial in the Heartbeat Discrimination Task (HDT), allowing the participant to judge the timing of auditory beeps relative to their heartbeat based on a given delay (current_delay).

    Parameters
    ----------
    win : visual.Window
        The PsychoPy window used for displaying visual stimuli and capturing participant responses.
        
    current_delay : float
        The delay (in milliseconds) between the participant's heartbeat and the auditory beep.
        
    is_integrated_external : bool
        A flag indicating if the experiment is integrated with external hardware (e.g., Spike2) for real-time stimulus presentation.
        
    if_debug : bool
        A flag for enabling debug mode, providing additional information and output (e.g., displaying the current delay value).

    Returns
    -------
    tuple
        A tuple containing:
        - str: The label of the button selected by the participant ('before', 'same time', or 'after').
        - int: The response code corresponding to the selected button:
            - 0: The beep is perceived before the heartbeat.
            - -1: The beep is perceived at the same time as the heartbeat.
            - 1: The beep is perceived after the heartbeat.

    Notes
    -----
    - If the participant presses 'escape' or 'q', the trial is terminated, and the function returns 'NA' for both the button and response code.
    - If the task is integrated with external hardware (e.g., Spike2), delay and start commands are sent via a serial port to trigger and synchronize auditory stimuli.
    - If in debug mode, the current delay value is displayed on the screen during the trial.
    - The participant is asked to judge the timing of the beeps relative to their heartbeat using one of three buttons: 'before', 'same time', or 'after'.
    - Button colors change to red when hovered over with the mouse, and the selection is confirmed upon a left mouse button click.
    - The function keeps refreshing the window with updated button states until a response is recorded.
    """
    # Display the heart image
    heart_image = visual.ImageStim(win, image=r'../tasks_helpers/Heart-icon.png', pos=(0, 0.5))
    heart_image.draw()    
    if if_debug:
        delay_text = visual.TextStim(win, text=f'Value {current_delay}', pos=(0, 0.5), color='black', height=20) # Display the current delay (staircase value)
        delay_text.draw()
    win.flip()
    core.wait(0.5)
    
    fixation_text = visual.TextStim(win, text='+', pos=(0, 0), color='grey', height=50)
    fixation_text.draw()
    win.flip()
    
    if is_integrated_external:
        # Send DELAY VALUE  to Spike2
        delay_command = 'DELAY' + str(current_delay) +';'
        ser.write(delay_command.encode('utf-8'))
        #print(f"Sent: {delay_command}")

        # Send START code to Spike2
        start_command = "START;"
        ser.write(start_command.encode('utf-8'))
        print(f"Sent: {start_command}")
        
        print("Tones starting")

        while True:
            received_data = ser.read(6).decode('utf-8')  # Read incoming data from the serial port
            #print("Received message: " + str(received_data))

            # Check if the received data is "ENDED;"
            if received_data.strip() == "ENDED;":
                print("Received message: " + str(received_data))
                print("Tones complete")
                break  # Exit the loop once "ENDED" is received

            # Check for escape key press to exit
            keys = event.getKeys()
            if 'escape' in keys:
                core.quit()

            core.wait(0.1)  # Wait for a short interval before checking again
        core.wait(1)
    else: 
        print('TESTING MODE ON: No beeps will play')
        core.wait(2)
        
    # Define the buttons and their properties
    buttons = ['before', 'same time', 'after']
    button_positions = [(-200, 0),(0, 0), (200, 0)]  # x, y positions for the buttons
    button_colors = [(0.5, 0.5, 0.5)] * len(buttons)  # Initial button colors (light grey)

    # Create button visual components
    button_visuals = []
    for i, button in enumerate(buttons):
        # Rectangle for each button
        rect = visual.Rect(win, width=150, height=50, pos=button_positions[i], fillColor=button_colors[i])
        button_visuals.append(rect)
        # Text for each button
        button_text = visual.TextStim(win, text=button, pos=button_positions[i], color=(-1,-1,-1))
        button_visuals.append(button_text)

    # Create question text
    question = visual.TextStim(win, text="Are the beeps \n\n\n\n\n\n your heartbeat?", pos=(0, 0), color=(-1,-1,-1))

    # Function to update button colors
    def update_button_colors(selected_index):
        for i in range(len(buttons)):
            if i == selected_index:
                button_visuals[i * 2].fillColor = (1, 0, 0)  # Red for selected
            else:
                button_visuals[i * 2].fillColor = (0.5, 0.5)  # Light grey for unselected

    # Draw the question and buttons
    question.draw()
    for button in button_visuals:
        button.draw()
    win.flip()

    # Record response
    response = None
    mouse = event.Mouse(win=win)
    while response is None:
        pos = mouse.getPos()

        # Check which button is hovered over
        buttons_clicked = [button_rect.contains(pos) for button_rect in button_visuals[::2]]
        
        # Determine selected button
        selected_button_index = None
        for i, clicked in enumerate(buttons_clicked):
            if clicked:
                selected_button_index = i
                break
        # Update button colors
        if selected_button_index is not None:
            update_button_colors(selected_button_index)
        
        # Draw question and buttons again to update colors
        question.draw()
        for button in button_visuals:
            button.draw()
        win.flip()

        # Check for mouse click
        if mouse.getPressed()[0]:  # Left mouse button
            if selected_button_index is not None:
                response = selected_button_index

        # Check for escape key press to exit
        keys = event.getKeys()
        if 'escape' in keys:
            core.quit()

    core.wait(2)

    # Code the response
    if response is not None:
        response_code = [0, -1, 1][response]  # Map to 0, 1: before (move up), in-sync (don't move), after (move down)
        if if_debug:
            print("Participant Response:", response_code, buttons[response])
    
    return  buttons[response], response_code


def ask_run_another(win):
    """
    Displays a question asking whether the participant would like to run another training trial or stop, and collects their response via mouse click on one of two buttons.

    Parameters
    ----------
    win : visual.Window
        The PsychoPy window used for displaying visual stimuli and capturing participant input.

    Returns
    -------
    str
        The selected option by the participant, either:
        - 'again': indicating the participant wants to run the task again.
        - 'stop': indicating the participant wants to stop the task.

    Notes
    -----
    - Two options are presented: 'again' (run another trial) and 'stop' (end the task).
    - Buttons for these options are displayed as rectangles, each with an associated text label.
    - The button colors are initially set to light grey and turn red when hovered over by the mouse.
    - The function captures the participant's selection through mouse interaction. The selected option is returned when the left mouse button is clicked on a button.
    - The function keeps redrawing the window with updated button colors based on mouse hover status until a valid response is recorded.
    """

    # Define options for the follow-up question
    options = ['again', 'stop']
    button_positions = [(-200, 0), (200, 0)]  # x, y positions for the buttons
    button_colors = [(0.5, 0.5, 0.5)] * len(options)  # Initial button colors (light grey)

    # Create button visual components
    button_visuals = []
    for i, option in enumerate(options):
        # Rectangle for each button
        rect = visual.Rect(win, width=150, height=50, pos=button_positions[i], fillColor=button_colors[i])
        button_visuals.append(rect)
        # Text for each button
        button_text = visual.TextStim(win, text=option, pos=button_positions[i], color=(-1, -1, -1))
        button_visuals.append(button_text)

    # Create question text
    question = visual.TextStim(win, text="Would you like to:\n\n\n\n\n\n", pos=(0, 0), color=(-1, -1, -1))

    # Function to update button colors
    def update_button_colors(selected_index):
        for i in range(len(options)):
            if i == selected_index:
                button_visuals[i * 2].fillColor = (1, 0, 0)  # Red for selected
            else:
                button_visuals[i * 2].fillColor = (0.5, 0.5, 0.5)  # Light grey for unselected

    # Draw the question and buttons
    question.draw()
    for button in button_visuals:
        button.draw()
    win.flip()

    # Record response
    response = None
    mouse = event.Mouse(win=win)
    while response is None:
        pos = mouse.getPos()

        # Check which button is hovered over
        buttons_clicked = [button_rect.contains(pos) for button_rect in button_visuals[::2]]
        
        # Determine selected button
        selected_button_index = None
        for i, clicked in enumerate(buttons_clicked):
            if clicked:
                selected_button_index = i
                break

        # Update button colors
        if selected_button_index is not None:
            update_button_colors(selected_button_index)
        
        # Draw question and buttons again to update colors
        question.draw()
        for button in button_visuals:
            button.draw()
        win.flip()

        # Check for mouse click
        if mouse.getPressed()[0]:  # Left mouse button
            if selected_button_index is not None:
                response = selected_button_index

        # Check for escape key press to exit
        keys = event.getKeys()
        if 'escape' in keys:
            core.quit()
    core.wait(2)

    return options[response]  # Return the selected option



def run_staircase_trial(win, current_delay, ser, is_integrated_external, if_debug):
    
    """
    Runs a single trial in the Heartbeat Discrimination Task (HDT), assessing the participant's perception of 
    auditory beeps in relation to their heartbeat.

    Parameters
    ----------
    win : visual.Window
        The PsychoPy window used for displaying visual stimuli and collecting participant responses.

    current_delay : float
        The delay value (in milliseconds) representing the timing of the auditory beep relative to the 
        participant's heartbeat.

    is_integrated_external : bool
        A flag indicating whether the experiment is integrated with external hardware (e.g., Spike2) for real-time 
        stimulus presentation.

    if_debug : bool
        A flag for enabling debug mode, which provides additional output for troubleshooting and display of 
        current delay values.

    Returns
    -------
    tuple
        A tuple containing:
        - str: The label of the button selected by the participant ('before', 'same time', or 'after').
        - int: The corresponding response code mapped to:
            - 0: "before" (the beep is perceived before the heartbeat).
            - -1: "same time" (the beep is perceived at the same time as the heartbeat).
            - 1: "after" (the beep is perceived after the heartbeat).
    """
    # Display the heart image
    heart_image = visual.ImageStim(win, image=r'../tasks_helpers/Heart-icon.png', pos=(0, 0.5))
    heart_image.draw()    
    if if_debug:
        delay_text = visual.TextStim(win, text=f'Value {current_delay}', pos=(0, 0.5), color='black', height=20) # Display the current delay (staircase value)
        delay_text.draw()
    win.flip()
    core.wait(0.5)
    
    fixation_text = visual.TextStim(win, text='+', pos=(0, 0), color='grey', height=50)
    fixation_text.draw()
    win.flip()
    
    if is_integrated_external:
        # Send DELAY VALUE  to Spike2
        delay_command = 'DELAY' + str(current_delay) +';'
        ser.write(delay_command.encode('utf-8'))
        #print(f"Sent: {delay_command}")

        # Send START code to Spike2
        start_command = "START;"
        ser.write(start_command.encode('utf-8'))
        print(f"Sent: {start_command}")
        
        print("Tones starting")

        while True:
            received_data = ser.read(6).decode('utf-8')  # Read incoming data from the serial port
            #print("Received message: " + str(received_data))

            # Check if the received data is "ENDED;"
            if received_data.strip() == "ENDED;":
                print("Received message: " + str(received_data))
                print("Tones complete")
                break  # Exit the loop once "ENDED" is received

            # Check for escape key press to exit
            keys = event.getKeys()
            if 'escape' in keys:
                core.quit()

            core.wait(0.1)  # Wait for a short interval before checking again
        core.wait(1)
    else: 
        print('TESTING MODE ON: No beeps will play')
        core.wait(2)

    # Define the buttons and their properties
    buttons = ['before', 'same time', 'after']
    button_positions = [(-200, 0),(0, 0), (200, 0)]  # x, y positions for the buttons
    button_colors = [(0.5, 0.5, 0.5)] * len(buttons)  # Initial button colors (light grey)

    # Create button visual components
    button_visuals = []
    for i, button in enumerate(buttons):
        # Rectangle for each button
        rect = visual.Rect(win, width=150, height=50, pos=button_positions[i], fillColor=button_colors[i])
        button_visuals.append(rect)
        # Text for each button
        button_text = visual.TextStim(win, text=button, pos=button_positions[i], color=(-1,-1,-1))
        button_visuals.append(button_text)

    # Create question text
    question = visual.TextStim(win, text="Are the beeps \n\n\n\n\n\n your heartbeat?", pos=(0, 0), color=(-1,-1,-1))
    
    # Function to update button colors
    def update_button_colors(selected_index):
        for i in range(len(buttons)):
            if i == selected_index:
                button_visuals[i * 2].fillColor = (1, 0, 0)  # Red for selected
            else:
                button_visuals[i * 2].fillColor = (0.5, 0.5)  # Light grey for unselected

    # Draw the question and buttons
    question.draw()
    for button in button_visuals:
        button.draw()
    win.flip()

    # Record response
    response = None
    mouse = event.Mouse(win=win)
    while response is None:
        pos = mouse.getPos()

        # Check which button is hovered over
        buttons_clicked = [button_rect.contains(pos) for button_rect in button_visuals[::2]]
        
        # Determine selected button
        selected_button_index = None
        for i, clicked in enumerate(buttons_clicked):
            if clicked:
                selected_button_index = i
                break
        # Update button colors
        if selected_button_index is not None:
            update_button_colors(selected_button_index)
        
        # Draw question and buttons again to update colors
        question.draw()
        for button in button_visuals:
            button.draw()
        win.flip()

        # Check for mouse click
        if mouse.getPressed()[0]:  # Left mouse button
            if selected_button_index is not None:
                response = selected_button_index
        
        ## Check for escape key press to exit
        keys = event.getKeys()
        if 'escape' in keys:
            core.quit()

    core.wait(2)

        # Code the response
    if response is not None:
        response_code = [0, -1, 1][response]  # Map to 0, 1: before (move up), in-sync (don't move), after (move down)
        if if_debug:
            print("Participant Response:", response_code, buttons[response])
    return buttons[response], response_code


def get_post_task_qs(win, csv_file_name, csv_writer, use_mouse=True):
    """
    Displays a series of questions with sliders for post-task feedback and collects responses using either mouse clicks or arrow keys.

    Parameters
    ----------
    win : visual.Window
        PsychoPy window object used to present stimuli.

    use_mouse : bool
        Flag to determine whether to use mouse click or keyboard for responses.

    Returns
    -------
    list of dict
        A list of dictionaries containing the responses to each question.
    """
    
    # Define questions and response options
    questions = [
        ('TaskGeneral', 'I find the task', ['Very unpleasant', 'Very pleasant']),
        ('Difficulty', 'I find the task', ['Very easy', 'Very hard']),
        ('Breathless', 'I feel breathless / have trouble breathing.', ['Not at all', 'Completely'])
    ]

    for label, question, scale in questions:
        # Create text stimulus for the question
        question_text = visual.TextStim(win, text=question, pos=(0, 0.5), height=20)
        # Instruction text
        instruction = visual.TextStim(win, text=f"{question}", pos=(0, 100), color="Black", height=20)

         # Create a slider with a marker
        slider = visual.Slider(win, ticks=(0, 50, 100), labels=scale, granularity=1,
                               style=['rating'], pos=(0, 0), size=(600, 20),
                               labelHeight=20, color="Black")
        line = visual.Line(win, start=(-300, -5), end=(300, -5), lineColor=(0.5, 0.5, 0.5), lineWidth=5)

        # Randomize initial slider position between 20% and 80%
        initial_position = random.uniform(20, 80)
        slider.markerPos = initial_position

   
        # Display question and slider
        response = None
        mouse = event.Mouse(win=win)

        while response is None:
            win.flip()
            instruction.draw()
            question_text.draw()
            line.draw()
            slider.draw()

            # Check for escape key press to exit
            keys = event.getKeys()
            if 'escape' in keys:
                core.quit()            

            if use_mouse:
                # Mouse click response
                # Check for mouse click
                if mouse.getPressed()[0]:  # Left mouse click
                    response = slider.markerPos
                    #print(f"Confidence rating = {response}")
                    core.wait(1)  # Wait 1 second before ending
                    break

                # Update the slider marker position with mouse movement
                mouse_x, _ = mouse.getPos()
                slider_value = (mouse_x + 300) / 6  # Mapping mouse_x to range 0-100
                if 0 <= slider_value <= 100:  # Ensure the value is within bounds
                    slider.markerPos = slider_value

                event.clearEvents(eventType='keyboard')
            else:
                # Keyboard response
                keys = event.getKeys()
                if 'left' in keys:
                    response = 0  # Corresponding to the first option in the scale
                elif 'right' in keys:
                    response = len(scale) - 1  # Corresponding to the last option in the scale
                if response is not None:
                    core.wait(1)  # Wait 1 second before ending

            event.clearEvents(eventType='keyboard')
        

        with open(csv_file_name, mode='a', newline='') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter='\t')
            csv_writer.writerow(['Post_task_question', label, response, 'NA', 'NA', 'NA']) 
            csv_file.close()