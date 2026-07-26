import os
from PIL import Image

media_dir = r"C:\Users\himan\.gemini\antigravity-ide\brain\d38b61af-840f-42cf-b3fb-799a4e4f308e"
output_dir = r"C:\Users\himan\project1\frontend\assets"
os.makedirs(output_dir, exist_ok=True)

files = [
    ("media__1785259281486.png", "real_tighra_lake_boats.jpg"),
    ("media__1785259287258.png", "real_tighra_dam_wall.jpg"),
    ("media__1785259303562.png", "real_tighra_dam_spillway.jpg")
]

for filename, out_name in files:
    filepath = os.path.join(media_dir, filename)
    if os.path.exists(filepath):
        img = Image.open(filepath)
        w, h = img.size
        # The browser viewport photo is centered between top bar (y ~ 140px) and taskbar (y ~ h - 50px)
        # and x bounds (x ~ w*0.19 to w*0.80)
        crop_box = (int(w * 0.192), int(h * 0.138), int(w * 0.796), int(h * 0.942))
        cropped = img.crop(crop_box)
        out_path = os.path.join(output_dir, out_name)
        cropped.convert("RGB").save(out_path, quality=95)
        print(f"Successfully saved real photo: {out_name} (Dimensions: {cropped.size})")
