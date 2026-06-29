def get_action_prompt(instruction, clickable_infos, width, height, keyboard, summary_history, action_history, last_summary, last_action, add_info, error_flag, completed_content, memory):
    prompt = "### Background ###\n"
    prompt += f"This image is a phone screenshot. Its width is {width} pixels and its height is {height} pixels. The user\'s instruction is: {instruction}.\n\n"
    
    prompt += "### Screenshot information ###\n"
    prompt += "In order to help you better perceive the content in this screenshot, we extract some information on the current screenshot through system files. "
    prompt += "This information consists of two parts: coordinates; content. "
    prompt += "The format of the coordinates is [x, y], x is the pixel from left to right and y is the pixel from top to bottom; the content is a text or an icon description respectively. "
    prompt += "The information is as follow:\n"

    for clickable_info in clickable_infos:
        if clickable_info['text'] != "" and clickable_info['text'] != "icon: None" and clickable_info['coordinates'] != (0, 0):
            prompt += f"{clickable_info['coordinates']}; {clickable_info['text']}\n"
    
    prompt += "Please note that this information is not necessarily accurate. You need to combine the screenshot to understand."
    prompt += "\n\n"
    
    prompt += "### Keyboard status ###\n"
    prompt += "We extract the keyboard status of the current screenshot and it is whether the keyboard of the current screenshot is activated.\n"
    prompt += "The keyboard status is as follow:\n"
    if keyboard:
        prompt += "The keyboard has been activated and you can type."
    else:
        prompt += "The keyboard has not been activated and you can\'t type."
    prompt += "\n\n"
    
    if add_info != "":
        prompt += "### Hint ###\n"
        prompt += "There are hints to help you complete the user\'s instructions. The hints are as follow:\n"
        prompt += add_info
        prompt += "\n\n"
    
    if len(action_history) > 0:
        prompt += "### History operations ###\n"
        prompt += "Before reaching this page, some operations have been completed. You need to refer to the completed operations to decide the next operation. These operations are as follow:\n"
        for i in range(len(action_history)):
            prompt += f"Step-{i+1}: [Operation: " + summary_history[i].split(" to ")[0].strip() + "; Action: " + action_history[i] + "]\n"
        prompt += "\n"
    
    if completed_content != "":
        prompt += "### Progress ###\n"
        prompt += "After completing the history operations, you have the following thoughts about the progress of user\'s instruction completion:\n"
        prompt += "Completed contents:\n" + completed_content + "\n\n"
    
    if memory != "":
        prompt += "### Memory ###\n"
        prompt += "During the operations, you record the following contents on the screenshot for use in subsequent operations:\n"
        prompt += "Memory:\n" + memory + "\n"
    
    if error_flag:
        prompt += "### Last operation ###\n"
        prompt += f"You previously wanted to perform the operation \"{last_summary}\" on this page and executed the Action \"{last_action}\". But you find that this operation does not meet your expectation. You need to reflect and revise your operation this time."
        prompt += "\n\n"
    
    prompt += "### Response requirements ###\n"
    prompt += "Now you need to combine all of the above to perform just one action on the current page. "
    prompt += "The Action field must be exactly one of the following formats and must not contain any extra words, labels, explanations, or examples:\n"
    prompt += "Open app (app name)\n"
    prompt += "Tap (x, y)\n"
    prompt += "Swipe (x1, y1), (x2, y2)\n"
    if keyboard:
        prompt += "Type (text)\n"
    else:
        prompt += "Type is not available because the keyboard has not been activated. If you need to type, first choose a Tap (x, y) action on the target input box to activate the keyboard.\n"
    prompt += "Home\n"
    prompt += "Stop\n\n"
    prompt += "The following are format examples only. Do not copy their coordinates or text; replace them with the coordinates or text required by the current screenshot and task:\n"
    prompt += "Example: Tap (540, 930)\n"
    prompt += "Example: Swipe (540, 1200), (540, 0)\n"
    if keyboard:
        prompt += "Example: Type (Hugo)\n"
        prompt += "Example: Type (+13920741751)\n"
    prompt += "Do not output incomplete actions such as Tap, Type, or Unable to Type.\n"
    prompt += "Do not output actions with extra text such as Tap (x, y): Tap (540, 930) or Type (text): Type \"Hugo\".\n"
    prompt += "Use Stop only if you think all the requirements of the user's instruction have been completed and no further operation is required."
    prompt += "\n\n"
    
    prompt += "### Output format ###\n"
    prompt += "Your output consists of the following three parts:\n"
    prompt += "### Thought ###\nThink about the requirements that have been completed in previous operations and the requirements that need to be completed in the next one operation.\n"
    prompt += "### Action ###\nOutput exactly one action line using one of the allowed formats above. The coordinates or text must be inside the parentheses.\n"
    prompt += "### Operation ###\nPlease generate a brief natural language description for the operation in Action based on your Thought."
    
    return prompt


def get_reflect_prompt(instruction, clickable_infos1, clickable_infos2, width, height, keyboard1, keyboard2, summary, action, add_info):
    prompt = f"These images are two phone screenshots before and after an operation. Their widths are {width} pixels and their heights are {height} pixels.\n\n"
    
    prompt += "In order to help you better perceive the content in this screenshot, we extract some information on the current screenshot through system files. "
    prompt += "The information consists of two parts, consisting of format: coordinates; content. "
    prompt += "The format of the coordinates is [x, y], x is the pixel from left to right and y is the pixel from top to bottom; the content is a text or an icon description respectively "
    prompt += "The keyboard status is whether the keyboard of the current page is activated."
    prompt += "\n\n"
    
    prompt += "### Before the current operation ###\n"
    prompt += "Screenshot information:\n"
    for clickable_info in clickable_infos1:
        if clickable_info['text'] != "" and clickable_info['text'] != "icon: None" and clickable_info['coordinates'] != (0, 0):
            prompt += f"{clickable_info['coordinates']}; {clickable_info['text']}\n"
    prompt += "Keyboard status:\n"
    if keyboard1:
        prompt += f"The keyboard has been activated."
    else:
        prompt += "The keyboard has not been activated."
    prompt += "\n\n"
            
    prompt += "### After the current operation ###\n"
    prompt += "Screenshot information:\n"
    for clickable_info in clickable_infos2:
        if clickable_info['text'] != "" and clickable_info['text'] != "icon: None" and clickable_info['coordinates'] != (0, 0):
            prompt += f"{clickable_info['coordinates']}; {clickable_info['text']}\n"
    prompt += "Keyboard status:\n"
    if keyboard2:
        prompt += f"The keyboard has been activated."
    else:
        prompt += "The keyboard has not been activated."
    prompt += "\n\n"
    
    prompt += "### Current operation ###\n"
    prompt += f"The user\'s instruction is: {instruction}. You also need to note the following requirements: {add_info}. In the process of completing the requirements of instruction, an operation is performed on the phone. Below are the details of this operation:\n"
    prompt += "Operation thought: " + summary.split(" to ")[0].strip() + "\n"
    prompt += "Operation action: " + action
    prompt += "\n\n"
    
    prompt += "### Response requirements ###\n"
    prompt += "Now you need to output the following content based on the screenshots before and after the current operation:\n"
    prompt += "Whether the result of the \"Operation action\" meets your expectation of \"Operation thought\"?\n"
    prompt += "A: The result of the \"Operation action\" meets my expectation of \"Operation thought\".\n"
    prompt += "B: The \"Operation action\" results in a wrong page and I need to return to the previous page.\n"
    prompt += "C: The \"Operation action\" produces no changes."
    prompt += "\n\n"
    
    prompt += "### Output format ###\n"
    prompt += "Your output format is:\n"
    prompt += "### Thought ###\nYour thought about the question\n"
    prompt += "### Answer ###\nA or B or C"
    
    return prompt


def get_memory_prompt(insight):
    if insight != "":
        prompt  = "### Important content ###\n"
        prompt += insight
        prompt += "\n\n"
    
        prompt += "### Response requirements ###\n"
        prompt += "Please think about whether there is any content closely related to ### Important content ### on the current page? If there is, please output the content. If not, please output \"None\".\n\n"
    
    else:
        prompt  = "### Response requirements ###\n"
        prompt += "Please think about whether there is any content closely related to user\'s instrcution on the current page? If there is, please output the content. If not, please output \"None\".\n\n"
    
    prompt += "### Output format ###\n"
    prompt += "Your output format is:\n"
    prompt += "### Important content ###\nThe content or None. Please do not repeatedly output the information in ### Memory ###."
    
    return prompt

def get_process_prompt(instruction, thought_history, summary_history, action_history, completed_content, add_info):
    prompt = "### Background ###\n"
    prompt += f"There is an user\'s instruction which is: {instruction}. You are a mobile phone operating assistant and are operating the user\'s mobile phone.\n\n"
    
    if add_info != "":
        prompt += "### Hint ###\n"
        prompt += "There are hints to help you complete the user\'s instructions. The hints are as follow:\n"
        prompt += add_info
        prompt += "\n\n"
    
    if len(thought_history) > 1:
        prompt += "### History operations ###\n"
        prompt += "To complete the requirements of user\'s instruction, you have performed a series of operations. These operations are as follow:\n"
        for i in range(len(summary_history)):
            operation = summary_history[i].split(" to ")[0].strip()
            prompt += f"Step-{i+1}: [Operation thought: " + operation + "; Operation action: " + action_history[i] + "]\n"
        prompt += "\n"
        
        prompt += "### Progress thinking ###\n"
        prompt += "After completing the history operations, you have the following thoughts about the progress of user\'s instruction completion:\n"
        prompt += "Completed contents:\n" + completed_content + "\n\n"
        
        prompt += "### Response requirements ###\n"
        prompt += "Now you need to update the \"Completed contents\". Completed contents is a general summary of the current contents that have been completed based on the ### History operations ###.\n\n"
        
        prompt += "### Output format ###\n"
        prompt += "Your output format is:\n"
        prompt += "### Completed contents ###\nUpdated Completed contents. Don\'t output the purpose of any operation. Just summarize the contents that have been actually completed in the ### History operations ###."
        
    else:
        prompt += "### Current operation ###\n"
        prompt += "To complete the requirements of user\'s instruction, you have performed an operation. Your operation thought and action of this operation are as follows:\n"
        prompt += f"Operation thought: {thought_history[-1]}\n"
        operation = summary_history[-1].split(" to ")[0].strip()
        prompt += f"Operation action: {operation}\n\n"
        
        prompt += "### Response requirements ###\n"
        prompt += "Now you need to combine all of the above to generate the \"Completed contents\".\n"
        prompt += "Completed contents is a general summary of the current contents that have been completed. You need to first focus on the requirements of user\'s instruction, and then summarize the contents that have been completed.\n\n"
        
        prompt += "### Output format ###\n"
        prompt += "Your output format is:\n"
        prompt += "### Completed contents ###\nGenerated Completed contents. Don\'t output the purpose of any operation. Just summarize the contents that have been actually completed in the ### Current operation ###.\n"
        prompt += "(Please use English to output)"
        
    return prompt
