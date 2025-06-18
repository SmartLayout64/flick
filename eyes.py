import pygame
import time
import random
import cv2
import numpy as np
from glob import glob
import os
import subprocess
import flickTools

# Load settings using flickTools.
settings = flickTools.loadSettings()

# Global variable to track if the system is listening.
global listening
listening = False

# Global variable to track if a picture has been snapped.
global snapped
snapped = False

# Global variable to store text content.
global text
text = ""

def initPygame(width=800, height=480):
    """
    Initializes Pygame, sets up the display, camera, and fonts.
    """
    global screen, cam, font, page, text, statusFont
    pygame.init()
    screen = pygame.display.set_mode((800, 480))
    pygame.display.set_caption("Flick")
    
    # Initialize camera.
    cam = cv2.VideoCapture(0)
    ret, frame = cam.read()
    
    # Load fonts for different text elements.
    font = pygame.font.Font('resources/outfit.ttf', 30)
    statusFont = pygame.font.Font('resources/outfit.ttf', 50)

    # Set initial page and clear text.
    page = "eyes"
    text = ""

    return screen, width, height

def loadIcon(icon):
    """
    Loads an icon image from the resources folder.
    """
    return pygame.image.load(f"resources/icons/{icon}.png").convert_alpha()

def applyRoundedCorners(surface, radius):
    """
    Applies rounded corners to a given Pygame surface.
    """
    width, height = surface.get_size()
    roundedMask = pygame.Surface((width, height), pygame.SRCALPHA)
    pygame.draw.rect(roundedMask, (255, 255, 255, 255), (0, 0, width, height), border_radius=radius)
    surface = surface.convert_alpha()
    roundedSurface = pygame.Surface((width, height), pygame.SRCALPHA)
    roundedSurface.blit(surface, (0, 0))
    roundedSurface.blit(roundedMask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
    return roundedSurface

def setColor(key, color):
    """
    Sets the color for a specified key in the global colors dictionary.
    """
    global colors
    colors[key] = color

def setStatus(statusTo):
    """
    Sets the global status text.
    """
    global status
    status = statusTo

def setMode(selectedMode):
    """
    Sets the global mode.
    """
    global mode
    mode = selectedMode

def setPage(pageTo):
    """
    Sets the current global page.
    """
    global page
    page = pageTo

def setText(textTo):
    """
    Sets the global text content and refreshes the text display.
    """
    global text
    text = textTo

def refreshText():
    """
    Refreshes text-related variables for display, including wrapping text
    and calculating scroll parameters.
    """
    global lines, initialScrollY, scrollY, lineSize, lineBezel, totalHeight, isDragging, dragStartY, showTextButton, showImageButton

    if len(text) > 0:
        showTextButton = True

    lines = flickTools.wrapText(text) # Wraps text to fit display.

    initialScrollY = 0
    scrollY = 0
    lineSize = 30
    lineBezel = 3
    totalHeight = (len(lines) + 5) * (lineSize + lineBezel)

    isDragging = False
    dragStartY = 0

    showImageButton = flickTools.checkImagesExist()

def refreshImages():
    """
    Reloads images and updates the image button visibility.
    """
    global images, showImageButton
    images = loadImages()
    if flickTools.checkImagesExist(): showImageButton = True
    else: showImageButton = False

def loadImages():
    """
    Loads images from the resources/images directory.
    """
    if flickTools.checkImagesExist():
        imagePaths = sorted(glob(os.path.join("resources/images", "*.*")))
        supportedExts = [".png", ".jpg", ".jpeg", ".bmp", ".gif"]
        imagePaths = [p for p in imagePaths if os.path.splitext(p)[1].lower() in supportedExts]
        images = [pygame.image.load(p).convert_alpha() for p in imagePaths]
        return images
    else: return "Empty"

def drawEyes(screen, eyeColor, eyePositions, eyeSize, offsetX, blinkIntensity):
    """
    Draws the animated eyes on the screen.
    """
    leftEyeX, rightEyeX, eyeY = eyePositions
    eyeHeight = int(eyeSize * blinkIntensity)
    maxStretch = 1
    stretchExponent = 10
    stretchFactor = pow(1 - blinkIntensity, stretchExponent)
    eyeWidth = int(eyeSize * (1 + maxStretch * stretchFactor))
    eyeTopY = eyeY + (eyeSize // 2) - (eyeHeight // 2)
    eyeLeftX = lambda x: x + offsetX - (eyeWidth - eyeSize) // 2
    pygame.draw.rect(screen, eyeColor, (eyeLeftX(leftEyeX), eyeTopY, eyeWidth, eyeHeight), border_radius=15)
    pygame.draw.rect(screen, eyeColor, (eyeLeftX(rightEyeX), eyeTopY, eyeWidth, eyeHeight), border_radius=15)

def resetEyes():
    """
    Resets the blink intensity of the eyes.
    """
    global blinkIntensity
    blinkIntensity = 1

def createButton(centerX, centerY, icon, radius):
    """
    Creates a circular button with an icon.
    """
    rect = pygame.Rect(centerX - radius, centerY - radius, radius * 2, radius * 2)
    icon = pygame.transform.smoothscale(icon, (radius * 2, radius * 2))
    return rect, icon, (centerX, centerY, radius)

def createSlider(x, y, width, height, min_val, max_val, step, initial_value):
    """
    Creates a dictionary representing a slider control.
    """
    slider = {
        "x": x,
        "y": y,
        "width": width,
        "height": height,
        "min": min_val,
        "max": max_val,
        "step": step,
        "value": initial_value,
        "dragging": False
    }
    return slider

def exit():
    """
    Sets the running flag to False to exit the GUI loop.
    """
    global running
    running = False

# Easing function for smoother eye movement.
def ease_in_out_quint(t):
    """
    Quintic ease-in-out easing function for smooth animations.
    """
    t *= 2
    if t < 1:
        return 0.5 * t**5
    t -= 2
    return 0.5 * (t**5 + 2)

def runGUI():
    """
    Main function to run the Pygame GUI.
    Handles events, updates game state, and draws elements.
    """
    global colors, width, height, running, mode, listening, snapped, page, text, lines, initialScrollY, scrollY, lineSize, lineBezel, totalHeight, isDragging, dragStartY, images, showImageButton, showTextButton, status, blinkIntensity
    screen, width, height = initPygame()
    clock = pygame.time.Clock()

    # --- Initialization of GUI Elements --- #

    # Global settings for colors and button radii.
    if True:
        # --- Global Colors and Buttons --- #
        if True:
            colors = {
                "bg": (20, 20, 20), # Background color
                "eye": (109, 230, 254), # Eye color (light blue)
                "text": (255, 255, 255), # Text color (white)
            }

            buttonInitalColor = (30, 30, 30) # Initial button color (dark gray)

            buttonColors = {
                "back": buttonInitalColor,
                "toCamera" : buttonInitalColor,
                "toImages" : buttonInitalColor,
                "toText" : buttonInitalColor,
                "cameraSnap": buttonInitalColor,
                "cameraExit": buttonInitalColor,
                "viewerLeft": buttonInitalColor,
                "viewerRight": buttonInitalColor,
                "sliderKnob": (80, 80, 200) # Slider knob color (blue)
            }

            trayButtonRadius = 40

            # Create common navigation buttons.
            backRect, backIcon, backCircleParams = createButton(20+trayButtonRadius, height - (20+trayButtonRadius), loadIcon("back"), trayButtonRadius)
            toTextRect, toTextIcon, toTextParams = createButton(width-((40+trayButtonRadius)*2), height - (20+trayButtonRadius), loadIcon("textview"), trayButtonRadius)
            toImagesRect, toImagesIcon, toImagesParams = createButton(width-((46+trayButtonRadius)*3), height - (20+trayButtonRadius), loadIcon("imageview"), trayButtonRadius)

            showImageButton = False # Flag to control image button visibility.
            showTextButton = False # Flag to control text button visibility.

            status = "Thinking..." # Initial status message.
            
        # --- Eye Animation Variables --- #
        if True:
            eyeSize = 150
            eyeSpacing = 50
            eyeY = height // 2 - eyeSize // 2 - 50

            leftEyeX = width // 2 - eyeSpacing // 2 - eyeSize
            rightEyeX = width // 2 + eyeSpacing // 2
            eyePositions = (leftEyeX, rightEyeX, eyeY)
            eyeOffset = 0 # Initial eye offset for movement.

            blinkIntensity = 1 # Controls eye open/close state (1 = fully open).

            listening = False # State for listening mode.
            mode = "neutral" # Current eye mode.

            # Blink animation timing.
            blinkInterval = (120, 180) # Ticks between blinks.
            nextBlink = random.randint(blinkInterval[0], blinkInterval[1])
            ticksSinceBlink = 0
            blinkTicks = 0

            # Eye movement timing.
            eyeMoveInterval = (100, 200) # Ticks between eye movements.
            nextEyeMove = random.randint(eyeMoveInterval[0], eyeMoveInterval[1])
            ticksSinceEyeMove = 0
            eyeMoveDuration = 30 # Ticks for eye movement animation.
            eyeMoveTicks = 0
            targetEyeOffset = 0 # Target position for eye movement.
            startEyeOffset = 0 # Starting position for eye movement.
            
            # Camera and settings buttons on the "eyes" page.
            toCameraRect, toCameraIcon, toCameraParams = createButton(width-20-trayButtonRadius, height - (20+trayButtonRadius), loadIcon("flash"), trayButtonRadius)
            settingsRect, settingsIcon, settingsParams = createButton(trayButtonRadius+20, trayButtonRadius+20, loadIcon("gear"), trayButtonRadius)

            showSettingsButton = False # Flag to control settings button visibility.

        # --- Camera Page Variables --- #
        if True:
            snapped = False # Flag to indicate if a picture has been taken.
            iconSize = 130

            cameraButton = pygame.Rect(width - 170, height - 230, 140, 200) # Area for snap/retake button.
            cameraFlashIcon = loadIcon("flash")
            cameraFlashIcon = pygame.transform.smoothscale(cameraFlashIcon, (iconSize, iconSize))
            cameraRetakeIcon = loadIcon("retake")
            cameraRetakeIcon = pygame.transform.smoothscale(cameraRetakeIcon, (iconSize, iconSize))

            exitButtonCamera = pygame.Rect(width - 170, height - 450, 140, 190) # Area for exit button.
            exitButtonIcon = loadIcon("back")
            exitButtonIcon = pygame.transform.smoothscale(exitButtonIcon, (iconSize, iconSize))

            snapPulse = 30 # Used for visual feedback on snap button.

        # --- Image Viewer Variables --- #
        if True:
            padding = 80
            yOffset = -35
            images = loadImages() # Load initial images.
            index = 0 # Current image index.
            buttonRadius = 55
            centerY = height // 2

            # Left and right navigation buttons for image viewer.
            leftRect, arrowLeftIcon, leftCircleParams = createButton(padding, centerY + yOffset, loadIcon("left"), buttonRadius)
            rightRect, arrowRightIcon, rightCircleParams = createButton(width - padding, centerY + yOffset, loadIcon("right"), buttonRadius)

            rightPulse = buttonInitalColor[0] # Used for visual feedback on right arrow.
            leftPulse = buttonInitalColor[0] # Used for visual feedback on left arrow.

            # Button to switch from image viewer to text viewer.
            imagesToTextRect, imagesToTextIcon, imagesToTextParams = createButton(width-20-trayButtonRadius, height - (20+trayButtonRadius), loadIcon("textview"), trayButtonRadius)

        # --- Text Viewer Variables --- #
        if True:
            refreshText() # Initialize text display.

            # Button to switch from text viewer to image viewer.
            textToImagesRect, textToImagesIcon, textToImagesParams = createButton(width-20-trayButtonRadius, height - (20+trayButtonRadius), loadIcon("imageview"), trayButtonRadius)

        # --- Settings Page Variables --- #
        if True:
            launchButton = pygame.Rect(width-260, height-70, 240, 50) # Button to launch external settings.
            launchText = font.render("Launch Settings", True, colors["text"])

            # Sliders for various settings.
            volumeSlider = createSlider(100, 100, 600, 6, 0, 100, 2, (settings["volumeIncr"]/1.2)+100)
            speedSlider = createSlider(100, 220, 600, 6, 0, 100, 2, settings["speed"]*100)
            gradeSlider = createSlider(100, 340, 600, 6, 1, 12, 1, settings["grade"])

    running = True
    while running:
        # --- Eyes Page Logic --- #
        if page == "eyes":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    keyPress = event.key
                    if keyPress == pygame.K_ESCAPE:
                        running = False
                    elif keyPress == pygame.K_SPACE:
                        listening = not listening
                        setColor("eye", (209, 254, 183) if listening else (109, 230, 254)) # Change eye color based on listening state.
                        eyeOffset = 0 # Reset eye offset when listening state changes.
                    elif keyPress == pygame.K_1:
                        page = "camera"
                    elif keyPress == pygame.K_2:
                        page = "image"
                    elif keyPress == pygame.K_3:
                        page = "text"
                    elif keyPress == pygame.K_4:
                        page = "status"
                    
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if toCameraRect.collidepoint(event.pos):
                        page = "camera"
                    elif toTextRect.collidepoint(event.pos):
                        page = "text"
                    elif toImagesRect.collidepoint(event.pos):
                        page = "image"
                    elif settingsRect.collidepoint(event.pos):
                        if showSettingsButton:
                            page = "settings"
                        else:
                            showSettingsButton = True # Show settings button on first click.
                    else:
                        listening = not listening
                        setColor("eye", (209, 254, 183) if listening else (109, 230, 254))
                        eyeOffset = 0 # Reset eye offset when listening state changes.

            screen.fill(colors["bg"]) # Fill background.
            
            # Blink animation update.
            ticksSinceBlink += 1
            maxBlinkTicks = 10
            halfBlink = maxBlinkTicks // 2

            if ticksSinceBlink > nextBlink:
                if blinkTicks == 0:
                    ticksSinceBlink = 0
                    blinkTicks = 1
                elif blinkTicks <= maxBlinkTicks:
                    # Calculate blink intensity based on current blink tick.
                    t = blinkTicks / halfBlink if blinkTicks <= halfBlink else (blinkTicks - halfBlink) / halfBlink
                    blinkIntensity = 1 - pow(t, 3) if blinkTicks <= halfBlink else pow(t, 0.5)
                    blinkTicks += 1
                else:
                    blinkTicks = 0
                    blinkIntensity = 1
                    nextBlink = random.randint(blinkInterval[0], blinkInterval[1])

            # Eye movement logic (only when not listening).
            if not listening:
                ticksSinceEyeMove += 1
                if eyeMoveTicks == 0:
                    if ticksSinceEyeMove > nextEyeMove:
                        startEyeOffset = eyeOffset
                        targetEyeOffset = random.choice([-40, -30, -20, 0, 0, 0, 0, 0, 20, 30, 40]) # Random eye target.
                        eyeMoveTicks = 1
                        ticksSinceEyeMove = 0
                        nextEyeMove = random.randint(eyeMoveInterval[0], eyeMoveInterval[1])
                elif eyeMoveTicks <= eyeMoveDuration:
                    t = eyeMoveTicks / eyeMoveDuration
                    eased_t = ease_in_out_quint(t) # Apply easing for smooth movement.
                    eyeOffset = startEyeOffset + (targetEyeOffset - startEyeOffset) * eased_t
                    eyeMoveTicks += 2
                else:
                    eyeMoveTicks = 0
                    eyeOffset = targetEyeOffset

            drawEyes(screen, colors["eye"], eyePositions, eyeSize, eyeOffset, blinkIntensity)

            # Draw camera button.
            pygame.draw.circle(screen, buttonColors["toCamera"], toCameraParams[:2], toCameraParams[2])
            screen.blit(toCameraIcon, toCameraRect)

            # Draw settings button if visible.
            if showSettingsButton:
                pygame.draw.circle(screen, buttonColors["toCamera"], settingsParams[:2], settingsParams[2])
                screen.blit(settingsIcon, settingsRect)

            # Draw text view button if text exists.
            if showTextButton:
                pygame.draw.circle(screen, buttonColors["toText"], toTextParams[:2], toTextParams[2])
                screen.blit(toTextIcon, toTextRect)

            # Draw image view button if images exist.
            if showImageButton:
                pygame.draw.circle(screen, buttonColors["toImages"], toImagesParams[:2], toImagesParams[2])
                screen.blit(toImagesIcon, toImagesRect)

            # Display snapped image preview if available.
            if snapped:
                try:
                    frame = pygame.image.load("temp/image.jpg").convert()
                    frame = pygame.transform.scale(frame, (160, 120))
                    frame = applyRoundedCorners(frame, radius=15)
                    screen.blit(frame, (20, height - 140))
                except:
                    pass

            pygame.display.flip()
            clock.tick(30)

        # --- Camera Page Logic --- #
        elif page == "camera":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    keyPress = event.key
                    if keyPress == pygame.K_ESCAPE:
                        running = False
                    elif keyPress == pygame.K_1:
                        page = "eyes"
                        showSettingsButton = False # Hide settings button when returning to eyes page.
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if cameraButton.collidepoint(event.pos):
                        snapPulse = 100 # Visual feedback for snap.
                        snapped = not snapped # Toggle snapped state.
                        if snapped:
                            pygame.image.save(frameSurface, "temp/image.jpg") # Save captured image.
                    if exitButtonCamera.collidepoint(event.pos):
                        page = "eyes"
                        showSettingsButton = False

            screen.fill(colors["bg"])
            
            if snapPulse > 30: snapPulse -= 10 # Fade snap pulse.

            buttonColors["cameraSnap"] = (snapPulse, snapPulse, snapPulse)

            pygame.draw.rect(screen, buttonColors["cameraSnap"], cameraButton, border_radius=20)
            pygame.draw.rect(screen, buttonColors["back"], exitButtonCamera, border_radius=20)

            # Display appropriate icon for snap/retake button.
            screen.blit(cameraRetakeIcon if snapped else cameraFlashIcon, cameraFlashIcon.get_rect(center=cameraButton.center))
            screen.blit(exitButtonIcon, exitButtonIcon.get_rect(center=exitButtonCamera.center))

            # Display live camera feed or snapped image.
            if snapped:
                frame = pygame.image.load("temp/image.jpg").convert()
                frame = pygame.transform.scale(frame, (560, 420))
            else:
                ret, frame = cam.read()
                frame = cv2.cvtColor(cv2.flip(frame, 1), cv2.COLOR_BGR2RGB) # Flip and convert color.
                frameSurface = pygame.surfarray.make_surface(np.rot90(frame)) # Rotate for Pygame.
                frameSurface = pygame.transform.scale(frameSurface, (560, 420))
                frame = frameSurface

            frame = applyRoundedCorners(frame, radius=20)
            screen.blit(frame, (((height - 420) // 2) + 10, (height - 420) // 2)) # Position camera feed.

            pygame.display.flip()
            clock.tick(30)

        # --- Image Viewer Page Logic --- #
        elif page == "image":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    keyPress = event.key
                    if keyPress == pygame.K_ESCAPE:
                        running = False
                    elif keyPress == pygame.K_2:
                        page = "eyes"
                        showSettingsButton = False
                    elif keyPress == pygame.K_r: # 'r' to refresh images.
                        images = loadImages()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if leftRect.collidepoint(event.pos):
                        index = (index - 1) % len(images) # Cycle through images.
                        leftPulse = 100
                    elif rightRect.collidepoint(event.pos):
                        index = (index + 1) % len(images)
                        rightPulse = 100
                    elif backRect.collidepoint(event.pos):
                        page = "eyes"
                        showSettingsButton = False
                    elif imagesToTextRect.collidepoint(event.pos):
                        page = "text"

            if leftPulse > 30: leftPulse -= 10
            if rightPulse > 30: rightPulse -= 10

            buttonColors["viewerLeft"] = (leftPulse, leftPulse, leftPulse)
            buttonColors["viewerRight"] = (rightPulse, rightPulse, rightPulse)

            screen.fill(colors["bg"])

            if images != "Empty": # Display current image if available.
                imgWidth, imgHeight = images[index].get_size()
                maxWidth = width - 2 * padding
                maxHeight = height - 2 * padding
                scaleFactor = min(maxWidth / imgWidth, maxHeight / imgHeight)
                newWidth = int(imgWidth * scaleFactor)
                newHeight = int(imgHeight * scaleFactor)
                scaledImage = pygame.transform.smoothscale(images[index], (newWidth, newHeight))
                frame = applyRoundedCorners(scaledImage.convert(), radius=15)
                screen.blit(frame, ((width - newWidth) // 2, ((height - newHeight) // 2) + yOffset))

            # Draw navigation and text view buttons.
            pygame.draw.circle(screen, buttonColors["viewerLeft"], leftCircleParams[:2], leftCircleParams[2])
            pygame.draw.circle(screen, buttonColors["viewerRight"], rightCircleParams[:2], rightCircleParams[2])
            screen.blit(arrowLeftIcon, leftRect)
            screen.blit(arrowRightIcon, rightRect)

            pygame.draw.circle(screen, buttonColors["toText"], imagesToTextParams[:2], imagesToTextParams[2])
            screen.blit(imagesToTextIcon, imagesToTextRect)

            pygame.draw.circle(screen, buttonColors["back"], backCircleParams[:2], backCircleParams[2])
            screen.blit(backIcon, backRect)

            pygame.display.flip()
            clock.tick(30)

        # --- Text Viewer Page Logic --- #
        elif page == "text":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    keyPress = event.key
                    if keyPress == pygame.K_ESCAPE:
                        running = False
                    elif keyPress == pygame.K_3:
                        page = "eyes"
                        showSettingsButton = False
                elif event.type == pygame.MOUSEBUTTONDOWN:        
                    isDragging = True # Enable scrolling by dragging.
                    dragStartY = pygame.mouse.get_pos()[1]
                    initialScrollY = scrollY
                    
                    if backRect.collidepoint(event.pos):
                        page = "eyes"
                        showSettingsButton = False
                    elif textToImagesRect.collidepoint(event.pos):
                        page = "image"
                        
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        isDragging = False

                elif event.type == pygame.MOUSEMOTION:
                    if isDragging:
                        currentY = pygame.mouse.get_pos()[1]
                        scrollY = initialScrollY + (currentY - dragStartY) # Update scroll position.

            screen.fill(colors["bg"])

            # Draw back and image view buttons.
            pygame.draw.circle(screen, buttonColors["back"], backCircleParams[:2], backCircleParams[2])
            screen.blit(backIcon, backRect)

            if showImageButton:
                pygame.draw.circle(screen, buttonColors["toText"], textToImagesParams[:2], textToImagesParams[2])
                screen.blit(textToImagesIcon, textToImagesRect)

            # Clamp scroll position to prevent scrolling out of bounds.
            scrollY = max(min(scrollY, 0), height - totalHeight)

            y = scrollY + 20
            for line in lines: # Draw each line of text.
                if len(lines) < 7: # Simple check, can be refined for better text rendering.
                    rendered = font.render(line, True, colors["text"])
                    screen.blit(rendered, (20, y))
                    y += lineSize + lineBezel
                else:
                    rendered = font.render(line, True, colors["text"])
                    screen.blit(rendered, (20, y))
                    y += lineSize + lineBezel

            pygame.display.flip()
            clock.tick(30)

        # --- Status Page Logic --- #
        elif page == "status":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.KEYDOWN:
                    keyPress = event.key
                    if keyPress == pygame.K_4:
                        blinkIntensity = 1.2 # Make eyes wide open when returning to eyes page.
                        page = "eyes"
                        showSettingsButton = False
            
            screen.fill(colors["bg"])

            # Gradually close eyes on the status page.
            if blinkIntensity > 0.3:
                blinkIntensity -= 0.3
            
            if blinkIntensity < 0.3:
                blinkIntensity = 0.3

            drawEyes(screen, colors["eye"], eyePositions, eyeSize, eyeOffset, blinkIntensity)

            # Display status text.
            renderedText = statusFont.render(status, True, colors["text"])
            lineRect = renderedText.get_rect(center=(width // 2, (height // 2) + 110))
            screen.blit(renderedText, lineRect)

            pygame.display.flip()
            clock.tick(30)

        # --- Settings Page Logic --- #
        elif page == "settings":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    keyPress = event.key
                    if keyPress == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if backRect.collidepoint(event.pos):
                        page = "eyes"
                        showSettingsButton = False
                    
                    if launchButton.collidepoint(event.pos):
                        subprocess.run("notepad resources/settings.txt") # Open settings file in notepad.

                    # Check if slider knobs are clicked.
                    sliderKnobX_volume = volumeSlider["x"] + int((volumeSlider["value"] - volumeSlider["min"]) / (volumeSlider["max"] - volumeSlider["min"]) * volumeSlider["width"])
                    sliderKnobRect_volume = pygame.Rect(sliderKnobX_volume - 20, volumeSlider["y"] - 20, 40, 40)
                    if sliderKnobRect_volume.collidepoint(event.pos):
                        volumeSlider["dragging"] = True

                    sliderKnobX_speed = speedSlider["x"] + int((speedSlider["value"] - speedSlider["min"]) / (speedSlider["max"] - speedSlider["min"]) * speedSlider["width"])
                    sliderKnobRect_speed = pygame.Rect(sliderKnobX_speed - 20, speedSlider["y"] - 20, 40, 40)
                    if sliderKnobRect_speed.collidepoint(event.pos):
                        speedSlider["dragging"] = True

                    sliderKnobX_grade = gradeSlider["x"] + int((gradeSlider["value"] - gradeSlider["min"]) / (gradeSlider["max"] - gradeSlider["min"]) * gradeSlider["width"])
                    sliderKnobRect_grade = pygame.Rect(sliderKnobX_grade - 20, gradeSlider["y"] - 20, 40, 40)
                    if sliderKnobRect_grade.collidepoint(event.pos):
                        gradeSlider["dragging"] = True

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        # Stop dragging and save settings when mouse button is released.
                        volumeSlider["dragging"] = False
                        speedSlider["dragging"] = False
                        gradeSlider["dragging"] = False

                        settings["volumeIncr"] = ((volumeSlider["value"]-100)*1.2) # Update volume setting.
                        settings["speed"] = speedSlider["value"]/100 # Update speed setting.
                        settings["grade"] = gradeSlider["value"] # Update grade setting.

                        flickTools.saveSettings(settings) # Save updated settings.

                elif event.type == pygame.MOUSEMOTION:
                    # Update slider values while dragging.
                    if volumeSlider["dragging"]:
                        mouseX = event.pos[0]
                        newValue = (mouseX - volumeSlider["x"]) / volumeSlider["width"] * (volumeSlider["max"] - volumeSlider["min"]) + volumeSlider["min"]
                        newValue = max(volumeSlider["min"], min(newValue, volumeSlider["max"]))
                        volumeSlider["value"] = round(newValue / volumeSlider["step"]) * volumeSlider["step"]
                    
                    if speedSlider["dragging"]:
                        mouseX = event.pos[0]
                        newValue = (mouseX - speedSlider["x"]) / speedSlider["width"] * (speedSlider["max"] - speedSlider["min"]) + speedSlider["min"]
                        newValue = max(speedSlider["min"], min(newValue, speedSlider["max"]))
                        speedSlider["value"] = round(newValue / speedSlider["step"]) * speedSlider["step"]

                    if gradeSlider["dragging"]:
                        mouseX = event.pos[0]
                        newValue = (mouseX - gradeSlider["x"]) / gradeSlider["width"] * (gradeSlider["max"] - gradeSlider["min"]) + gradeSlider["min"]
                        newValue = max(gradeSlider["min"], min(newValue, gradeSlider["max"]))
                        gradeSlider["value"] = round(newValue / gradeSlider["step"]) * gradeSlider["step"]

            screen.fill(colors["bg"])

            # Draw launch settings button.
            pygame.draw.rect(screen, buttonColors["toCamera"], launchButton, border_radius=25)
            screen.blit(launchText, launchText.get_rect(center=launchButton.center))

            # Draw volume slider.
            pygame.draw.rect(screen, (100, 100, 100), (volumeSlider["x"], volumeSlider["y"], volumeSlider["width"], volumeSlider["height"]), border_radius=3)
            knobX_volume = volumeSlider["x"] + int((volumeSlider["value"] - volumeSlider["min"]) / (volumeSlider["max"] - volumeSlider["min"]) * volumeSlider["width"])
            pygame.draw.circle(screen, buttonColors["sliderKnob"], (knobX_volume, volumeSlider["y"] + volumeSlider["height"] // 2), 10)
            sliderValueText_volume = font.render(f"Volume: {int(volumeSlider['value'])}%", True, colors["text"])
            text_rect_volume = sliderValueText_volume.get_rect(center=(width // 2, volumeSlider["y"] - 30))
            screen.blit(sliderValueText_volume, text_rect_volume)

            # Draw speed slider.
            pygame.draw.rect(screen, (100, 100, 100), (speedSlider["x"], speedSlider["y"], speedSlider["width"], speedSlider["height"]), border_radius=3)
            knobX_speed = speedSlider["x"] + int((speedSlider["value"] - speedSlider["min"]) / (speedSlider["max"] - speedSlider["min"]) * speedSlider["width"])
            pygame.draw.circle(screen, buttonColors["sliderKnob"], (knobX_speed, speedSlider["y"] + speedSlider["height"] // 2), 10)
            sliderValueText_speed = font.render(f"Speed: {int(speedSlider['value'])}%", True, colors["text"])
            text_rect_speed = sliderValueText_speed.get_rect(center=(width // 2, speedSlider["y"] - 30))
            screen.blit(sliderValueText_speed, text_rect_speed)

            # Draw grade level slider.
            pygame.draw.rect(screen, (100, 100, 100), (gradeSlider["x"], gradeSlider["y"], gradeSlider["width"], gradeSlider["height"]), border_radius=3)
            knobX_grade = gradeSlider["x"] + int((gradeSlider["value"] - gradeSlider["min"]) / (gradeSlider["max"] - gradeSlider["min"]) * gradeSlider["width"])
            pygame.draw.circle(screen, buttonColors["sliderKnob"], (knobX_grade, gradeSlider["y"] + gradeSlider["height"] // 2), 10)
            sliderValueText_grade = font.render(f"Grade Level: {int(gradeSlider['value'])}", True, colors["text"])
            text_rect_grade = sliderValueText_grade.get_rect(center=(width // 2, gradeSlider["y"] - 30))
            screen.blit(sliderValueText_grade, text_rect_grade)

            # Draw back button.
            pygame.draw.circle(screen, buttonColors["back"], backCircleParams[:2], backCircleParams[2])
            screen.blit(backIcon, backRect)

            pygame.display.flip()
            clock.tick(30)

    pygame.quit() # Uninitialize Pygame when the loop exits.

if __name__ == "__main__":
    runGUI()