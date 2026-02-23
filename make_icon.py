from PIL import Image

# laad je gegenereerde PNG
img = Image.open("icon.png")   # pas naam aan als nodig

# zorg dat hij vierkant is (belangrijk voor ico)
size = max(img.size)
square = Image.new("RGBA", (size, size), (0, 0, 0, 0))
square.paste(img, ((size - img.width) // 2, (size - img.height) // 2))

# sla op als multi-resolution ico
square.save(
    "icon.ico",
    format="ICO",
    sizes=[(16,16), (32,32), (48,48), (64,64), (128,128), (256,256)]
)

print("icon.ico gemaakt.")