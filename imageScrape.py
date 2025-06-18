from google_images_search import GoogleImagesSearch
import os, time
import flickTools

# Initialize the Google Images Search client with API key and Project CX.
gis = GoogleImagesSearch('AIzaSyCTEh_LfhD9iwS9q_P4iPnJE1MYbB9lkCo', '158fe729f328c4f0c')

def clearImages(folderPath='resources/images'):
    """
    Clears all image files from the specified folder.
    If the folder does not exist, it creates it.

    Args:
        folderPath (str): The path to the folder to clear.
    """
    # Check if the specified folder exists. If not, create it.
    if not os.path.exists(folderPath):
        os.makedirs(folderPath)
        return # Exit the function as there's nothing to clear

    # Iterate over all files in the folder
    for filename in os.listdir(folderPath):
        filePath = os.path.join(folderPath, filename) # Get the full path to the file
        # Check if it's a file (and not a directory) before attempting to remove
        if os.path.isfile(filePath):
            os.remove(filePath) # Delete the file

def getImage(query, num, folderPath='resources/images'):
    """
    Searches for images on Google Images and downloads a specified number of them
    to a local folder. Includes a delay to account for download time and
    checks if images were successfully downloaded.

    Args:
        query (str): The search query for images.
        num (int): The number of images to download.
        folderPath (str): The directory where images will be saved.
    """
    # Define search parameters for the Google Images Search API
    searchParams = {
        'q': query,         # The search query string
        'num': num,         # The number of images to retrieve
        'safe': 'active'    # Activates safe search to filter explicit content
    }

    # Execute the image search and download images to the specified directory
    gis.search(search_params=searchParams, path_to_dir=folderPath)

    print("SCRAPE| Started image download")

    # Introduce a delay to allow time for images to download.
    # The delay is proportional to the number of images requested.
    time.sleep(num * 0.5)

    # Check if any images were actually downloaded using a function from flickTools.
    # This might indicate if the Google Search JSON API limit has been reached.
    if not flickTools.checkImagesExist():
        print("SCRAPE| GS JSON API drained")

    print("SCRAPE| Lifted blocker") # Indicates that the blocking operation (download + delay) is complete