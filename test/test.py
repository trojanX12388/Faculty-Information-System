from PIL import Image
# Open the image file
with open("test.jpg", "rb") as f:
    image = Image.open(f)
    
import base64
# Convert the image to base64 format
with open("test.jpg", "rb") as f:
    encoded_image = base64.b64encode(f.read())
  
imgdata = base64.b64decode(encoded_image)
filename = 'some_image.jpg'  # I assume you have a way of picking unique filenames
with open(filename, 'wb') as f:
    f.write(imgdata)