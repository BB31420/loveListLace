# LoveListLace
An AI-powered storytelling video generator that takes real-time Craigslist data, generates a story using OpenAI's GPT-4, creates images using OpenAI's DALL-E 3, adds voiceover using Neets.ai, and combines the elements into a video.

![gui](https://i.imgur.com/Hq7osfR.png)

## Video Examples
[![Example 0](https://img.youtube.com/vi/L049Xi_POaU/0.jpg)](https://www.youtube.com/watch?v=L049Xi_POaU)
[![Example 1](https://img.youtube.com/vi/ZyY20n5VyQA/0.jpg)](https://www.youtube.com/watch?v=ZyY20n5VyQA)


### To DO & Contributions: 
1. The code in main.py is WET(Write everything twice), we need to DRY(Don't repeat yourself) it out by changing how it handles file paths and variables.
2. Converting the code to object oriented classes will make it modular and easier to maintain.
3. OpenAi has increased the API limit for high quality images to 5 per minute. We should add the ability to specify the amount of images to create and merge.
4. Zoom, pan, fade, and other editing effects can be added with ffmpeg.
5. Offline Ai models are becoming easier to use. Running this code offline can save costs but introduces a new level of difficutly in sourcing and running the models. Can we implement this effectively?


## Getting Started

These instructions will help you set up the project on your local machine.

### Prerequisites

- Python 3.6 or higher
- Pip (Python package manager)
- FFmpeg (a command-line program for video processing)

### Create Virtual Environment
This helps keep packages seperate to avoid conflicts. Use the venv when running the code and before installing the required packages. The code requires openai 0.28, which is specified in the requirements.txt. 

1. Make a project folder where the virtual environment and code will be stored. 
 * Windows: ```mkdir loveListLace_project```
 * Linux: ```mkdir loveListLace_project```   
2. Navigate to the project directory with: ```cd``` ```ls -la``` use tab key to auto complete instead of typing out the full file/folder names.
 * Windows: ```python -m venv .venv``` then ```Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser```
 * Linux: ```python3 -m venv .venv```
3. Activate the venv
 * Windows: ```venv\Scripts\Activate.ps1```
 * Linux: ```source .venv/bin/activate```
4. Close venv when finished running main.py, it needs to be active to use the packages ```deactivate```



### Installation

1. Clone the repository: ```git clone git@github.com:BB31420/loveListLace.git```
2. Navigate to the cloned code directory: ```cd loveListLace```
3. Install the required Python packages: ```pip install -r requirements.txt```
4. Install FFmpeg:
- On macOS, you can use Homebrew: brew install ffmpeg
- On Linux, you can use your package manager (e.g., apt-get install ffmpeg on Ubuntu)
- On Windows, you can download an installer from the official FFmpeg website





### Usage

1. Edit the file named main.py in the project directory and add your API key: 


 * Replace your_openai_api_key with your actual [OpenAi](https://www.openai.com) keys:
 `OPENAI_API_KEY='your_openai_api_key'`
 * Replace with your [Neets API Key](https://www.neets.ai):
 `"X-API-Key": "Your Neet.Ai API Key"`


2. Edit the file named main.py with your desired font path, specify the directory and font name.
 * Modify font path
```
font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regu
```
   * Linux fonts can be found at: `"/usr/share/fonts"`
   * Windows fonts can be found at: `C:\Windows\Fonts` 
3. Run the main.py script by navigating to the project directory. Output will be generated in the same folder: 

* Windows: `python main.py`
* Linux: `python3 main.py`
4. Follow the prompts to enter a story prompt and generate a video.

### Troubleshooting
* If you encounter errors related to missing dependencies, make sure you have installed the required Python packages by running `pip install -r requirements.txt`
* If you encounter errors related to FFmpeg, make sure it is installed on your system and available in your system's PATH.
* https://platform.openai.com/account/api-keys
* Keep your keys safe

 
 
 


# Instructable: Using the App for different style stories:

This instructable will guide you through modifying the provided code to focus on generating a video about a car salesman and a love story. We'll cover changing the prompts and app.

 **Example usage**
 * For a love story, use the default prompts, no query, and select the ```mis - missed connections``` category with the desired area and amount of posts
 * For an auto salesman, select an area and category as ```cto - cars and trucks - by owner```
 * Pick 4 posts since cars posts are longer in general
 * Enter the query ```5 speed```
 * Fetch and Save Posts
 * Fetch Posts Contents
 * Generate OpenAI Response and replace the system content message with:
   ```
   You are a used cars salesman. Do not speak as if the subjects in the stories are listening. Do not repeat yourself, be interesting but not long-winded. Do not use [Your Name] instead create a real name you prefer. Do not repeat a website url.

   ```
 * Replace the custom prompt at the top and scroll to review the posts below that will be sent to generate a response: 
   ```
   Read these posts and create a virtual story attempting to sell the vehicles.
   ```      
 * Use the same technique to generate an image
 * Pick a voice an review the script.
 * Create the video before adding captions
 * Click the heart thing on the repo to donate



