# Image downloder
- Download images from input website and store them in images folder
- Able to download SVG, JPG, PNG, GIF and base64 encoded images
- To speed up downloading parallel processing is done 

# Solution
- Go to the URL and use BeautifulSoup4 to parse the website content 
- Search for all img and svg tag
- If src contains data:image then save the base64 content in file and use content-type to determine file extension
- If src contains URL then download the file and save and use determine the file name from URL
- For svg tags, store the content of svg tag in file

# Language & Tools
- Python
- Requests 
- BeautifulSoup4 
