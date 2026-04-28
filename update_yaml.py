import yaml

# These are the 29 classes from the Roboflow Plants Diseases dataset
CLASS_NAMES = [
    "Apple Scab",                    # class_0
    "Apple Healthy",                 # class_1
    "Apple Cedar Rust",              # class_2
    "Bell Pepper Healthy",           # class_3
    "Bell Pepper Bacterial Spot",    # class_4
    "Blueberry Healthy",             # class_5
    "Cherry Healthy",                # class_6
    "Cherry Powdery Mildew",         # class_7
    "Corn Gray Leaf Spot",           # class_8
    "Corn Common Rust",              # class_9
    "Peach Healthy",                 # class_10
    "Peach Bacterial Spot",          # class_11
    "Potato Early Blight",           # class_12
    "Potato Late Blight",            # class_13
    "Raspberry Healthy",             # class_14
    "Soybean Healthy",               # class_15
    "Squash Powdery Mildew",         # class_16
    "Strawberry Healthy",            # class_17
    "Strawberry Leaf Scorch",        # class_18
    "Tomato Septoria Leaf Spot",     # class_19
    "Tomato Yellow Leaf Curl Virus", # class_20
    "Tomato Bacterial Spot",         # class_21
    "Tomato Late Blight",            # class_22
    "Tomato Mosaic Virus",           # class_23
    "Tomato Target Spot",            # class_24
    "Tomato Leaf Mold",              # class_25
    "Tomato Spider Mites",           # class_26
    "Grape Healthy",                 # class_27
    "Grape Black Rot",               # class_28
]

with open("data.yaml", "r") as f:
    data = yaml.safe_load(f)

data["names"] = CLASS_NAMES
data["nc"] = len(CLASS_NAMES)

with open("data.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False)

print("data.yaml updated with real class names!")
print(f"Total classes: {len(CLASS_NAMES)}")
