import textwrap, os

def blendColors(color1, color2, weight):
    """
    Blends two RGB colors together based on a specified weight.

    Args:
        color1 (tuple): The first RGB color as a tuple (R, G, B).
        color2 (tuple): The second RGB color as a tuple (R, G, B).
        weight (int): The number of times to blend the colors. A higher weight
                      means color1 will shift closer to color2.

    Returns:
        tuple: The blended RGB color as a tuple (R, G, B).
    """
    for i in range(weight):
        # Calculates the average of each RGB component
        color1 = (((color1[0]+color2[0])//2),
                  ((color1[1]+color2[1])//2),
                  ((color1[2]+color2[2])//2))
    return color1

def wrapText(inputString):
    """
    Wraps the input string to a maximum line width of 50 characters,
    preserving original line breaks and handling empty lines.

    Args:
        inputString (str): The string to be wrapped.

    Returns:
        list: A list of strings, where each string is a wrapped line.
    """
    lines = inputString.splitlines()  # Split the input string into individual lines
    result = []  # Initialize an empty list to store the wrapped lines

    for originalLine in lines:
        words = originalLine.split()  # Split each original line into words
        line = ""  # Initialize an empty string for the current wrapped line
        
        for word in words:
            # Check if adding the next word exceeds the 50-character limit
            # (1 if line else 0) accounts for the space before the word if it's not the first word
            if len(line) + len(word) + (1 if line else 0) > 50:
                result.append(line)  # Add the current line to the result
                line = word  # Start a new line with the current word
            else:
                # Add a space before the word if it's not the first word on the line
                line += (" " if line else "") + word

        if line:
            result.append(line)  # Add any remaining text in 'line' to the result
        elif not words:
            result.append("")  # If an original line was empty, add an empty string to result

    return result

def cutFirstSections(text):
    """
    Extracts the first two paragraphs from a given text.

    Args:
        text (str): The input text.

    Returns:
        str: A string containing the first two paragraphs, separated by double newlines.
             Returns an empty string if there are no paragraphs.
    """
    # Split the text into paragraphs, strip leading/trailing whitespace from each,
    # and filter out any empty strings that result from multiple newlines.
    paragraphs = [p.strip() for p in text.strip().split("\n\n") if p.strip()]
    # Join the first two paragraphs (or fewer if less than two exist) with double newlines.
    return "\n\n".join(paragraphs[:2])

def checkImagesExist():
    """
    Checks if there are any image files present in the 'resources/images' directory.

    Returns:
        bool: True if the directory exists and contains at least one file, False otherwise.
    """
    # Checks if the 'resources/images' directory exists and if it contains any files.
    return len(os.listdir("resources/images")) > 0

def deleteSnap():
    """
    Deletes the 'image.jpg' file if it exists.
    Prints a message upon successful deletion. Silently handles FileNotFoundError.
    """
    try:
        os.remove("image.jpg")  # Attempt to remove the file
        print("TOOLS | Camera snap deleted")  # Confirm deletion
    except FileNotFoundError:
        pass  # Do nothing if the file does not exist

def loadSettings():
    """
    Loads settings from 'resources/settings.txt' file.
    Each line in the file is expected to be in 'key=value' format.
    Values are parsed into their appropriate types (boolean, int, float, or string).

    Returns:
        dict: A dictionary containing the loaded settings.
    """
    settings = {}  # Initialize an empty dictionary to store settings
    try:
        # Open the settings file in read mode
        with open("resources/settings.txt", 'r') as file:
            for line in file:
                # Process lines that contain an '=' sign
                if '=' in line:
                    # Split the line into key and value, stripping whitespace
                    key, value = line.strip().split('=', 1)
                    settings[key] = parseValue(value)  # Parse and store the value
    except FileNotFoundError:
        # If the file is not found, print a warning and return an empty settings dictionary
        print(f"Warning: file not found. Using defaults.")
    return settings

def saveSettings(settings):
    """
    Saves the provided settings dictionary to 'resources/settings.txt' file.
    Each key-value pair is written as 'key=value' on a new line.

    Args:
        settings (dict): The dictionary of settings to be saved.
    """
    # Open the settings file in write mode (creates if not exists, overwrites if exists)
    with open("resources/settings.txt", 'w') as file:
        for key, value in settings.items():
            file.write(f"{key}={value}\n")  # Write each key-value pair

def parseValue(value):
    """
    Attempts to parse a string value into a boolean, integer, float, or returns
    the original string if none of the conversions are successful.

    Args:
        value (str): The string value to parse.

    Returns:
        bool, int, float, or str: The parsed value.
    """
    # Check if the value can be interpreted as a boolean
    if value.lower() in ['true', 'false']:
        return value.lower() == 'true'
    try:
        return int(value)  # Attempt to convert to an integer
    except ValueError:
        try:
            return float(value)  # Attempt to convert to a float
        except ValueError:
            return value  # Return the original string if no conversion is possible

def updateSetting(key, newValue):
    """
    Updates a specific setting in the 'resources/settings.txt' file.
    It loads all settings, updates the specified key, and then saves all settings back.

    Args:
        key (str): The key of the setting to update.
        newValue: The new value for the setting.
    """
    # Load existing settings from the file
    settings = loadSettings() # Removed "resources/settings.txt" as it's not needed as an argument in loadSettings
    settings[key] = newValue  # Update the value for the specified key
    saveSettings(settings)  # Save the modified settings back to the file