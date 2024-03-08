from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import os
import textwrap
from openai import OpenAI
import os
from IPython.display import Image, display, Markdown
from pyairtable import Api
import time
load_dotenv()

def print_wrapped(text, width=80):
    wrapped_text = textwrap.fill(text, width=width)
    print(wrapped_text)


def image_from_prompt(style, object):

  ## create the image
  prompt = f'please create an image of a {object} and please adhere strictly to the following style prompt: {style["prompt"]}'

  client = OpenAI(
      api_key = os.getenv("OPENAI_API_KEY")
  )
  imageresponse = client.images.generate(
    model="dall-e-3",
    quality="hd",
    prompt=prompt,
    n=1,
    size="1024x1024"
  )

  image_url=imageresponse.data[0].url
  revised_prompt=imageresponse.data[0].revised_prompt

  ## display it in colab

  display(Image(url=image_url, width=500))
  display(Markdown("## prompt"))
  print_wrapped(prompt)
  display(Markdown("## revised_prompt"))
  print_wrapped(revised_prompt)

  ## send it to Airtable database
  gallery_url = "https://airtable.com/appxAzTlapU1rYEpi/tblZtKvMDUj3fjPJW/viwfRmpGHHw1wZpNp?blocks=biplIkQhqX3esgZBQ"
  base_id = "appszoCOuMekB7MzP"
  table_name = "Images"

  AIRTABLE_API_KEY = os.getenv("AIRTABLE_API_KEY")
  api = Api(AIRTABLE_API_KEY)
  table = api.table(base_id, table_name)

  record_data = {
      "InitialURL": image_url,
      "ImageAttachment": [{"url": image_url}],
      "Name": style["slug"] + "-" + object + "-" + str(int(time.time())),
      "Prompt": prompt,
      "RevisedPrompt": revised_prompt,
      "Style": style["name"],
      "Object": object,
      "Title": style["name"] + " " + object
  }

  try:
      created_record=table.create(record_data)
      record_id = created_record['id']
      record_data['record_id'] = record_id
      print(f"Record created successfully in Airtable. It should be at this {gallery_url}")
      return record_data
  except Exception as e:
      print(f"An error occurred: {e}")


# Load environment variables
load_dotenv()

app = FastAPI()

@app.get("/generate-image/{style_key}/{object_name}")
async def generate_image(style_key: str, object_name: str):
    if style_key not in styles or object_name not in objects:
        raise HTTPException(status_code=404, detail="Style or Object not found")

    try:
        image_data = image_from_prompt(styles[style_key], object_name)
        return image_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

styles = {
    "product_photography": {
        "name": "Product Photography",
        "prompt": "with high-resolution product photography lighting, photorealism, showcasing the object's details sharply against a neutral background, direct lighting, front-facing product, magazine shoot, website photography",
        "slug": "product_photography"
    },
    "3d_blender": {
        "name": "3D Blender",
        "prompt": "rendered in a 3D Blender style, with realistic textures, advanced lighting, and shadow effects to give depth, 3D shapes, 3D depth, video game design",
        "slug": "3d_blender"
    },
    "technical_drawing": {
        "name": "Technical Drawing",
        "prompt": "as a technical drawing, with precise lines and measurements, showcasing an isometric or orthographic projection, precise detailing, monochromatic, technical pencils, drafting tools",
        "slug": "technical_drawing"
    },
    "product_concept_art": {
        "name": "Product Concept Art",
        "prompt": "as concept art, using digital painting techniques to present a visual representation of an idea with dynamic composition and lighting, ultra detailed, close-up, high resolution, futuristic yet elegant color palette with metallic tones",
        "slug": "product_concept_art"
    },
    "my_style": {
        "name": "MK Style",
        "prompt": "product photo with high key, bright lighting and saturated colors. shot on a seamless white background. very even bright lighting and saturated colors.",
        "slug": "my-style"
    },
    "mj_style": {
        "name": "MJ Style",
        "prompt": "nuetral photo with bright, even lighting and saturated colors. realistic style on a nuetral background and a general, basic aesthetic.",
        "slug": "mj-style"
    },
    "real_style": {
        "name": "Real Style",
        "prompt": "realistic close up photo with matted colors. Simple dim lighting on a nuetral white background. As close to a real photograph of an object as possible.",
        "slug": "real-style"
    },
    "stock_style": {
        "name": "Stock Style",
        "prompt": "in the style of a standard stock photo. neutral white background. even lighting. matte colors. photorealistic style. simple and professional. realistic imperfect textures.",
        "slug": "stock-style"
    },
    "makeshift_style": {
      "name":  "Makeshift style",
      "prompt": "made from locally sourced materials, even lighting, close to reality, matte colors, many materials, makeshift with the makerspace vibe, on a matte well lit wooden surface surrounded by the tools used to make it",
      "slug": "makeshift-style"
    }
}


# add more objects that contain PFAS
objects = ["umbrella", "raincoat", "pizza box"]