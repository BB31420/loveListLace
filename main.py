import csv
import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from bs4 import BeautifulSoup
from openai import OpenAI
import requests
from pathlib import Path
from moviepy.editor import ImageClip, AudioFileClip
from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mpy
import numpy as np



OPENAI_API_KEY = 'REMOVE AND ADD YOUR API KEY HERE BETWEEN THE SINGLE QUOTES'  # Replace with your actual OpenAI API key


def read_csv(file_path):
    data = []
    with open(file_path, 'r') as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            data.append(row)
    return data

areas_data = read_csv('areas.csv')
categories_data = read_csv('categories.csv')

def fetch_and_save_data():
    selected_area = area_combobox.get()
    selected_category = category_combobox.get().split(" - ")[0]
    query = query_entry.get()
    
    hostname = next((item['Hostname'] for item in areas_data if item['Description'] == selected_area), None)
    
    if hostname and selected_category:
        encoded_query = query.replace(" ", "+")
        # Build link to fetch
        url = f"https://{hostname}.craigslist.org/jsonsearch/{selected_category}?query={encoded_query}&srchType=A&hasPic=0&bundleDuplicates=1&format=json"
        
        print(f"Fetching data from URL: {url}")
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            
            # Filter out the 'null' URLs
            valid_urls = [item.get('PostingURL') for item in data[0] if item.get('PostingURL')]
            
            # Save only the valid URLs to a file
            with open(f"{selected_area}_{selected_category}_urls.json", 'w') as file:
                json.dump(valid_urls, file, indent=4)
            
            print(f"URLs saved to {selected_area}_{selected_category}_urls.json")
            messagebox.showinfo("Success", "URLs fetched and saved successfully!")
        else:
            print("Failed to fetch data.")
            messagebox.showerror("Error", "Failed to fetch data.")


def fetch_posts_contents():
    selected_area = area_combobox.get()
    selected_category = category_combobox.get().split(" - ")[0]
    num_posts = int(num_posts_combobox.get())
    
    try:
        # Load URLs from the saved JSON file
        with open(f"{selected_area}_{selected_category}_urls.json", 'r') as file:
            urls = json.load(file)
        
        if not urls:
            print("No URLs found in the file.")
            return

        posts_list = []  # List to hold post details
        
        for url in urls[:num_posts]:
            if not url:
                print("Encountered an empty URL. Skipping...")
                continue
            
            response = requests.get(url)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extracting the title
                title_span = soup.find('span', {'id': 'titletextonly'})
                title = title_span.text.strip() if title_span else "Title not found"
                
                # Extracting the post body and removing unwanted text
                post_body_div = soup.find('section', {'id': 'postingbody'})
                post_body = post_body_div.text.strip().replace("QR Code Link to This Post", "") if post_body_div else "Post body not found"
                
                post_details = {
                    'Title': title,
                    'Post Body': post_body
                }
                
                posts_list.append(post_details)
                
        # Save fetched posts to a JSON file
        with open(f"{selected_area}_{selected_category}_posts.json", 'w') as file:
            json.dump(posts_list, file, indent=4)
        
        print(f"Posts saved to {selected_area}_{selected_category}_posts.json")
        messagebox.showinfo("Success", "Posts fetched and saved successfully!")
                
    except FileNotFoundError:
        print("No URLs file found for selected area and category.")
    except Exception as e:
        print(f"An error occurred: {e}")


def generate_openai_response():
    selected_area = area_combobox.get()
    selected_category = category_combobox.get().split(" - ")[0]
    
    try:
        # Fetch posts from the respective JSON file
        with open(f"{selected_area}_{selected_category}_posts.json", 'r') as file:
            posts = json.load(file)
        
        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Combine post bodies into a single string to send as a prompt
        combined_prompt = "Read these posts and write a newscast type story about the specific city's social life:\n\n"
        combined_prompt += "\n\n".join([post['Post Body'] for post in posts])
        
        # Create a Toplevel window for user input
        custom_prompt_window = tk.Toplevel(root)
        custom_prompt_window.title("Custom Prompt and System Content")
        
        # System Content Input
        ttk.Label(custom_prompt_window, text="System Content:").pack(pady=5)
        system_content_text = tk.Text(custom_prompt_window, height=8, width=50, wrap="word")
        system_content_text.insert(tk.END, "You are a news anchor. Do not speak as if the subjects in the stories are listening. Do not repeat yourself, be interesting but not long-winded. Do not use [Your Name] instead create a real name you prefer. Do not repeat a website url.")
        system_content_text.pack(pady=5)
        
        # Custom Prompt Input
        ttk.Label(custom_prompt_window, text="Enter your custom prompt (modify if needed):").pack(pady=5)
        custom_prompt_text = tk.Text(custom_prompt_window, height=8, width=50, wrap="word")
        custom_prompt_text.insert(tk.END, combined_prompt)  # Set the combined prompt
        custom_prompt_text.pack(pady=5)
        
        def fetch_openai_response():
            system_content = system_content_text.get("1.0", tk.END).strip()
            custom_prompt = custom_prompt_text.get("1.0", tk.END).strip()
            
            # Send the system content and custom prompt to OpenAI API
            response = client.chat.completions.create(
                model="gpt-4-1106-preview",
                messages=[
                    {"role": "system", "content": system_content},
                    {"role": "user", "content": custom_prompt}
                ]
            )
            
            content = response.choices[0].message.content
            
            # Save the OpenAI response to a file
            with open(f"{selected_area}_{selected_category}_openai_response.txt", 'w') as file:
                file.write(content)
            
            print(f"OpenAI response saved to {selected_area}_{selected_category}_openai_response.txt")
            
            # Close the Toplevel window after fetching the response
            custom_prompt_window.destroy()
            
            # Bring the main application window to the foreground
            root.lift()
            
            # Show confirmation message box on top
            messagebox.showinfo("Success", "OpenAI response fetched and saved successfully!")
        
        ttk.Button(custom_prompt_window, text="Generate Response", command=fetch_openai_response).pack(pady=10)
        
    except FileNotFoundError:
        print("No posts file found for selected area and category.")
        # Bring the main application window to the foreground
        root.lift()
        messagebox.showerror("Error", "No posts file found for selected area and category.")
    except Exception as e:
        print(f"An error occurred: {e}")
        # Bring the main application window to the foreground
        root.lift()
        messagebox.showerror("Error", f"An error occurred: {e}")


def generate_openai_image_response():
    selected_area = area_combobox.get()
    selected_category = category_combobox.get().split(" - ")[0]
    
    try:
        with open(f"{selected_area}_{selected_category}_openai_response.txt", 'r') as file:
            openai_response_text = file.read().strip()
        
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Create a Toplevel window for user input
        custom_prompt_window = tk.Toplevel(root)
        custom_prompt_window.title("Custom Image Prompt")
        
        # Prompt Input
        ttk.Label(custom_prompt_window, text="Modify the prompt for the image generation:").pack(pady=10)
        
        prompt_entry = ttk.Entry(custom_prompt_window, width=60)
        prompt_entry.insert(tk.END, "Create a real image using some details from the following text: \n")
        prompt_entry.pack(pady=10)
        
        def fetch_image_with_custom_prompt():
            modified_prompt = prompt_entry.get() + custom_prompt_text.get("1.0", tk.END).strip()
            
            response = client.images.generate(
                model="dall-e-3",
                prompt=modified_prompt,
                size="1024x1024",
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url
            
            # Download the image using the requests library
            image_response = requests.get(image_url)
            
            # Check if the request was successful
            if image_response.status_code == 200:
                with open(f"{selected_area}_{selected_category}_generated_image.png", 'wb') as image_file:
                    image_file.write(image_response.content)
                
                print(f"Image downloaded successfully as {selected_area}_{selected_category}_generated_image.png")
                
                # Close the Toplevel window after fetching the image
                custom_prompt_window.destroy()
                
                # Show confirmation message box on top
                root.lift()
                messagebox.showinfo("Success", "Image created and saved successfully!")
                
            else:
                print("Failed to download the image.")
        
        custom_prompt_text = tk.Text(custom_prompt_window, height=5, width=60, wrap="word")
        custom_prompt_text.insert(tk.END, openai_response_text)  # Set the default openai response text
        custom_prompt_text.pack(pady=10)
        
        ttk.Button(custom_prompt_window, text="Generate Image", command=fetch_image_with_custom_prompt).pack(pady=10)
        
    except FileNotFoundError:
        print("No OpenAI response file found.")
        messagebox.showerror("Error", "No OpenAI response file found.")
    except Exception as e:
        print(f"An error occurred while generating or downloading the image: {e}")
        messagebox.showerror("Error", f"An error occurred: {e}")


def generate_openai_audio_response():
    selected_area = area_combobox.get()
    selected_category = category_combobox.get().split(" - ")[0]
    
    try:
        with open(f"{selected_area}_{selected_category}_openai_response.txt", 'r') as file:
            openai_response_text = file.read().strip()
        
        client = OpenAI(api_key=OPENAI_API_KEY)  # Initialize the client with your API key
        
        # Create a Toplevel window for user input
        audio_settings_window = tk.Toplevel(root)
        audio_settings_window.title("Select Voice for Audio Response")
        
        # Display OpenAI response for user review
        ttk.Label(audio_settings_window, text="Review the OpenAI Response:").pack(pady=10)
        response_text_widget = tk.Text(audio_settings_window, height=10, width=50, wrap="word")
        response_text_widget.insert(tk.END, openai_response_text)
        response_text_widget.pack(pady=10)
        
        # Label for voice selection
        ttk.Label(audio_settings_window, text="Select Voice for Audio Response:").pack(pady=10)
        
        # Combobox for voice selection
        voice_options = ["alloy", "echo", "fable", "nova", "onyx", "shimmer"]
        selected_voice = tk.StringVar()
        voice_combobox = ttk.Combobox(audio_settings_window, textvariable=selected_voice, values=voice_options)
        voice_combobox.pack(pady=10)
        voice_combobox.set("nova")  # Default voice selection
        
        def generate_audio_with_selected_voice():
            try:
                response = client.audio.speech.create(
                    model="tts-1",
                    voice=selected_voice.get(),
                    input=openai_response_text
                )
                
                speech_file_path = Path(__file__).parent / f"{selected_area}_{selected_category}_speech.mp3"
                
                # Save the audio to the specified file path
                with open(speech_file_path, 'wb') as audio_file:
                    audio_file.write(response.content)
                    
                print(f"Audio file saved successfully as {speech_file_path}")
                # Close the Toplevel window after saving the audio
                audio_settings_window.destroy()
                
                # Bring the main application window to the foreground
                root.lift()
                
                messagebox.showinfo("Success", "Audio created and saved successfully!")
                
            except Exception as e:
                print(f"An error occurred while generating or saving the audio: {e}")
                # Bring the main application window to the foreground
                root.lift()
                messagebox.showerror("Error", f"An error occurred: {e}")
        
        ttk.Button(audio_settings_window, text="Generate Audio", command=generate_audio_with_selected_voice).pack(pady=10)
        
    except FileNotFoundError:
        print("No OpenAI response file found.")
        # Bring the main application window to the foreground
        root.lift()
        messagebox.showerror("Error", "No OpenAI response file found.")
        
    except Exception as e:
        print(f"An error occurred while reading the OpenAI response: {e}")
        # Bring the main application window to the foreground
        root.lift()
        messagebox.showerror("Error", f"An error occurred: {e}")



def generate_video_from_image_and_audio(image_path, audio_path, output_path):
    # Load the image and audio using moviepy
    audio_clip = AudioFileClip(audio_path)
    
    # Determine the duration of the audio clip
    audio_duration = audio_clip.duration

    # Create an image clip with the same duration as the audio clip
    image_clip = ImageClip(image_path).set_duration(audio_duration)

    # Combine the image and audio clips
    final_clip = image_clip.set_audio(audio_clip)

    # Set fps for the final clip (e.g., 24 fps)
    final_clip = final_clip.set_fps(24)

    # Write the video to a file
    final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac', fps=24)


def generate_video():
    selected_area = area_combobox.get()
    selected_category = category_combobox.get().split(" - ")[0]

    image_path = f"{selected_area}_{selected_category}_generated_image.png"
    audio_path = f"{selected_area}_{selected_category}_speech.mp3"
    output_path = f"{selected_area}_{selected_category}_combined_video.mp4"

    try:
        generate_video_from_image_and_audio(image_path, audio_path, output_path)
        print(f"Video generated successfully as {output_path}")
        messagebox.showinfo("Success", "Video created successfully!")
    except Exception as e:
        print(f"An error occurred while generating the video: {e}")
        messagebox.showerror("Error", "Failed to generate the video.")


def create_caption_images(story, chars_per_caption=30):
    """
    Convert the story into caption segments based on characters.
    Ensure that words are not split across captions.
    """
    words = story.split()
    caption_segments = []
    
    current_segment = ""
    for word in words:
        if len(current_segment + word) <= chars_per_caption:
            current_segment += " " + word if current_segment else word
        else:
            caption_segments.append(current_segment.strip())
            current_segment = word
    
    # Add any remaining segment
    if current_segment:
        caption_segments.append(current_segment.strip())
    
    caption_images = []
    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
    font_size = 40
    font = ImageFont.truetype(font_path, font_size)

    for segment in caption_segments:
        img = Image.new('RGBA', (1920, 100), (0, 0, 0, 100))
        d = ImageDraw.Draw(img)
        d.text((290, 10), segment, fill=(255, 255, 255, 255), font=font)
        caption_images.append(img)

    return caption_images


def add_captions_to_video(video_path, caption_images, output_path):
    video_clip = mpy.VideoFileClip(video_path)
    total_duration = video_clip.duration
    num_captions = len(caption_images)
    avg_duration_per_caption = total_duration / num_captions
    
    caption_clips = []
    for idx, caption_img in enumerate(caption_images):
        start_time = idx * avg_duration_per_caption
        end_time = start_time + avg_duration_per_caption
        if end_time > total_duration:
            end_time = total_duration
        
        caption_img_array = np.array(caption_img)
        caption_clip = mpy.ImageClip(caption_img_array).set_duration(end_time - start_time).set_start(start_time).set_position(('left', 'bottom'))
        caption_clips.append(caption_clip)
    
    final_caption_clip = mpy.CompositeVideoClip(caption_clips, size=video_clip.size)
    final_video_clip = mpy.CompositeVideoClip([video_clip.set_duration(total_duration), final_caption_clip.set_duration(total_duration)])
    
    final_video_clip.write_videofile(output_path, codec="libx264", audio_codec='aac', fps=24)


def generate_and_add_captions():
    selected_area = area_combobox.get()
    selected_category = category_combobox.get().split(" - ")[0]
    openai_response_file_path = f"{selected_area}_{selected_category}_openai_response.txt"
    
    try:
        with open(openai_response_file_path, 'r') as file:
            openai_response_text = file.read().strip()
        
        caption_images = create_caption_images(openai_response_text)
        
        video_path = f"{selected_area}_{selected_category}_combined_video.mp4"
        output_path = f"{selected_area}_{selected_category}_video_with_captions.mp4"
        
        add_captions_to_video(video_path, caption_images, output_path)
        
        print(f"Video with captions generated successfully as {output_path}")
        messagebox.showinfo("Success", "Captions added to the video successfully!")
    except Exception as e:
        print(f"An error occurred while adding captions to the video: {e}")
        messagebox.showerror("Error", "Failed to add captions to the video.")


# Build GUI 
root = tk.Tk()
root.title("LoveListLace")

# Areas Dropdown
ttk.Label(root, text="Select Area:").grid(row=0, column=0)
area_combobox = ttk.Combobox(root, values=[item['Description'] for item in areas_data])
area_combobox.grid(row=0, column=1)
area_combobox.current(0)

# Categories Dropdown
ttk.Label(root, text="Select Category:").grid(row=1, column=0)
category_combobox = ttk.Combobox(root, values=[f"{item['Abbreviation']} - {item['Description']}" for item in categories_data])
category_combobox.grid(row=1, column=1)
category_combobox.current(0)

# Query Entry
ttk.Label(root, text="Enter Query:").grid(row=2, column=0)
query_entry = ttk.Entry(root, width=40)
query_entry.grid(row=2, column=1)

# Number of Posts Dropdown
ttk.Label(root, text="Number of Posts:").grid(row=3, column=0)
num_posts_combobox = ttk.Combobox(root, values=[i for i in range(1, 11)])  # Letting user select 1 to 10 posts
num_posts_combobox.grid(row=3, column=1)
num_posts_combobox.current(0)

# Fetch and Save Data Button
fetch_button = ttk.Button(root, text="Fetch and Save Posts", command=fetch_and_save_data)
fetch_button.grid(row=4, columnspan=2)

# Fetch Posts Contents Button
fetch_posts_button = ttk.Button(root, text="Fetch Posts Contents", command=fetch_posts_contents)
fetch_posts_button.grid(row=5, columnspan=2)

# Add a button to trigger OpenAI API request
generate_openai_button = ttk.Button(root, text="Generate OpenAI Response", command=generate_openai_response)
generate_openai_button.grid(row=6, columnspan=2)

# Add a button to trigger OpenAI image generation
generate_image_button = ttk.Button(root, text="Generate Image from OpenAI Response", command=generate_openai_image_response)
generate_image_button.grid(row=7, columnspan=2)

# Add a button to generate OpenAI audio response
generate_audio_button = ttk.Button(root, text="Generate OpenAI Audio Response", command=generate_openai_audio_response)
generate_audio_button.grid(row=8, columnspan=2)

# Add a button to create a video
generate_video_button = ttk.Button(root, text="Generate Video", command=generate_video)
generate_video_button.grid(row=9, columnspan=2)

# Add a button for generating captions
generate_captions_button = ttk.Button(root, text="Add Captions to Video", command=generate_and_add_captions)
generate_captions_button.grid(row=10, columnspan=2)

root.mainloop()
