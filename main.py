import eyes, flickTools, imageScrape, prompt, voiceRecognition, speech
import threading

def main():
    """
    The main function that orchestrates the interaction loop of the AI assistant.
    It handles listening for user input, transcribing it, generating responses,
    finding and displaying images, and playing back speech.
    """
    while True: # Main loop for continuous interaction
        # Wait until the 'eyes' module indicates it's listening for voice input.
        while not eyes.listening: 
            pass
        
        # Start recording user's voice input.
        voiceRecognition.startRecording()
        
        # Wait while the 'eyes' module indicates it's still listening.
        while eyes.listening: 
            pass
        
        # Stop recording once listening mode is off.
        voiceRecognition.endRecording()

        # Update the status displayed on the 'eyes' (GUI) to "Thinking...".
        eyes.setStatus("Thinking...")
        # Set the GUI page to display the status.
        eyes.setPage("status")

        # Transcribe the recorded voice input into text.
        userPrompt = voiceRecognition.transcribe()

        # Update the status to indicate the AI is processing the response.
        eyes.setStatus("Figuring out what to say...")

        # Determine whether to include an image in the prompt based on a 'snapped' flag.
        if eyes.snapped:
            # If an image was snapped, prompt the AI with both text and the image.
            response = prompt.promptImage(userPrompt)
            # Delete the snapped image after it's been used.
            flickTools.deleteSnap()
            # Reset the snapped flag.
            eyes.snapped = False
        else: 
            # If no image was snapped, prompt the AI with text only.
            response = prompt.prompt(userPrompt)
        
        # Generate an audio file of the AI's response.
        # It cuts down the response to its first sections for speech generation.
        speech.generateFile(flickTools.cutFirstSections(response))

        # Print the character count of the AI's response for debugging/monitoring.
        print(f"FLICK | Characters in response: {len(response)}")

        # Clear any existing images in the 'resources/images' directory.
        print("MAIN  | Cleared images")
        imageScrape.clearImages()

        # Check if the AI's response suggests that an image or diagram would be helpful.
        if "image" in response or "diagram" in response:
            # Update status to indicate image search is in progress.
            eyes.setStatus("Finding images...")
            
            def download():
                """
                Helper function to handle image downloading in a separate thread.
                Encapsulates the image search and download logic.
                """
                try:
                    # Generate an image search query based on the AI's response.
                    query = prompt.generateImageQuery(response)
                    # Download 10 images based on the generated query.
                    imageScrape.getImage(query, 10)
                except Exception as e:
                    # Log any errors encountered during image download.
                    print(f"IMG   | Download thread error: {e}")

            # Create and start a new thread for downloading images to avoid blocking the main thread.
            imgThread = threading.Thread(target=download)
            imgThread.start()
            # Wait for the image download thread to complete before proceeding.
            imgThread.join()
       
            # Refresh the images displayed on the GUI.
            eyes.refreshImages()

        # Determine whether to display the full text response or return to the 'eyes' page.
        if len(response) > 150:
            # If the response is long, set it as the text to be displayed.
            eyes.setText(response)
            # Refresh the text display on the GUI.
            eyes.refreshText()
            # Set the GUI page to display the text.
            eyes.setPage("text")
        else:
            # If the response is short, revert to the 'eyes' display.
            eyes.setPage("eyes")
            # Reset the eye animation/state.
            eyes.resetEyes()

        # Play the generated speech of the AI's response.
        speech.playSpeech()

# Clear images at the start of the application.
imageScrape.clearImages()

# Create and start a separate thread for the main interaction loop.
# This allows the GUI (if run separately) to remain responsive.
mainThread = threading.Thread(target=main)
mainThread.start()

# Run the GUI. This call is typically blocking and keeps the application window open.
eyes.runGUI()