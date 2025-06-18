from openai import OpenAI
import base64
import flickTools

# Load settings using a function from flickTools.
# These settings likely contain user-specific information (name, grade, etc.).
settings = flickTools.loadSettings()

# Initialize the OpenAI client with the provided API key.
client = OpenAI(
    api_key=""
)

# Define the system message that sets the persona and guidelines for the AI assistant (Flick).
# This message instructs the AI on its tone, formatting, and how to interact with users,
# including prompting for images and acknowledging pre-found images.
systemMessage = {
    "role": "system",
    "content": (
        f"""
You're Flick, a fun and clever homework helper with a chill personality. When you explain things, speak like a friendly older sibling who actually makes stuff make sense. Use plain text only — no math symbols, no fancy formatting. Break your responses into short lines that are easy to read on screen.
Keep things light, a bit playful, but always clear. Add blank lines to separate ideas, and explain things step-by-step, like you're talking to someone right next to you.

Flick is designed to help students who may not always have access to tutors, stable internet, or extra academic support. Some users might be going through tough situations at home or in life.

You don't need to bring this up directly or treat them differently in an obvious way.

You are used in a module that has an image finder, so prompt them to click the image button for diagrams if it would be helpful.
Also, the user believes you are finding the images, so play along and say something like I found images for you.

Just:

    Be patient and never assume the student already knows something

    Break things down clearly without being condescending

    Keep the tone encouraging, but not over-the-top

    Never shame someone for not knowing something — normalize learning step by step

    Speak like someone who's on their side, helping out without judging

Keep the tone upbeat and helpful. No long lectures. You're here to make learning way less boring.

You can use:

    basic ACSII characters

    line breaks and blank lines for clarity

    lists using dashes or numbers

    casual language and analogies

You should not use:

    backticks, slashes, stars, or double asterisks for math

    bold text

    any symbols that won't show cleanly in plain pygame text

    emojis

    long paragraphs without breaks

    many unneccessary line breaks for small greetings, compliments, talk

Explain things step-by-step in small chunks.
Always make sure the output looks great when printed line-by-line in a basic text box.

Example format for explanations:

----

The Pythagorean Theorem is like a cheat code for right triangles.

Got two shorter sides? Call them a and b.
Got the longest side? That's c — the hypotenuse.

Here's the deal:
a squared plus b squared equals c squared

So if a is 3 and b is 4:
3 squared is 9
4 squared is 16

Add 'em up: 9 + 16 = 25
So c squared is 25... which means c is 5!

Boom. Triangle solved.

I also found some diagrams for you, go ahead and click the image button to take a look!

-----

Always respond in this style, unless told otherwise.

Here is some information provided by the user:
Name: {settings["name"]}
Grade: {settings["grade"]}
Information: {settings["info"]}
Course: {settings["course"]}"""
    )
}

# Define a separate system message for generating image search queries.
# This message guides the AI to produce concise and effective queries for image searches.
querySystemMessage = {
    "role": "system",
    "content": (
        "You are a helper that turns homework questions or answers into short, specific search queries "
        "for diagrams, labeled charts, or educational images. Focus on the key concept. Keep it short and clear. "
        "Avoid full sentences. Just give the kind of query that would work well in Google Images."
    )
}

# Initialize the conversation messages with the system message.
# This list will keep track of the conversation history.
messages = [systemMessage]

def prompt(userInput):
    """
    Sends a user's text input to the OpenAI model and retrieves Flick's response.
    The conversation history is maintained in the 'messages' list.

    Args:
        userInput (str): The user's question or statement.

    Returns:
        str: Flick's generated response.
    """
    messages.append({"role": "user", "content": userInput}) # Add user's message to history
    completion = client.chat.completions.create(
        model="gpt-4o-mini", # Specify the OpenAI model to use
        messages=messages    # Pass the entire conversation history
    )
    reply = completion.choices[0].message.content # Extract Flick's reply
    messages.append({"role": "assistant", "content": reply}) # Add Flick's reply to history
    return reply

def promptImage(userInput):
    """
    Sends a user's text input along with an image to the OpenAI model for analysis.
    The image is encoded in base64. The conversation history is maintained.

    Args:
        userInput (str): The user's question or statement related to the image.

    Returns:
        str: Flick's generated response based on the text and image.
    """
    with open("image.jpg", "rb") as imageFile:
        # Read the image file and encode it in base64 for API submission.
        image = base64.b64encode(imageFile.read()).decode('utf-8')
    
    # Construct the message payload including both text and image URL.
    message = {"role": "user",
               "content": [
                   {"type": "text", "text": userInput},
                   {"type": "image_url", "image_url":
                    { "url": f"data:image/jpeg;base64,{image}",}}]}
    
    messages.append(message) # Add the message (with image) to history
    completion = client.chat.completions.create(
        model="gpt-4o-mini", # Specify the OpenAI model
        messages=messages    # Pass the entire conversation history
    )
    reply = completion.choices[0].message.content # Extract Flick's reply
    messages.append({"role": "assistant", "content": reply}) # Add Flick's reply to history
    return reply

def generateImageQuery(flickResponse):
    """
    Generates a concise image search query based on Flick's explanation.
    This uses a separate system message and a lower temperature for more focused results.

    Args:
        flickResponse (str): The explanation provided by Flick.

    Returns:
        str: A short, specific query suitable for an image search engine.
    """
    # Construct the user prompt for generating an image query.
    queryUserPrompt = {
        "role": "user",
        "content": f'What would be a good image search query for this topic or explanation?\n\n"{flickResponse}"'
    }

    # Send the request to the OpenAI model using the 'querySystemMessage'.
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[querySystemMessage, queryUserPrompt], # Use the specific query system message
        temperature=0.3 # Lower temperature for less creative, more direct output
    )

    # Print the generated query for debugging or logging purposes.
    print(f"QUERY | Looked up: {completion.choices[0].message.content.strip()}")

    # Return the generated image query, stripped of leading/trailing whitespace.
    return completion.choices[0].message.content.strip()