from ultralytics import YOLO

MODEL  = r"C:\Users\aisva\Downloads\AgriHelp-main\runs\detect\runs\train\plant_disease2\weights\best.pt"
SOURCE = r"C:\Users\aisva\Downloads\AgriHelp-main\test\images"

CLASS_NAMES = [
    "Apple Scab", "Apple Healthy", "Apple Cedar Rust",
    "Bell Pepper Healthy", "Bell Pepper Bacterial Spot",
    "Blueberry Healthy", "Cherry Healthy", "Cherry Powdery Mildew",
    "Corn Gray Leaf Spot", "Corn Common Rust", "Peach Healthy",
    "Peach Bacterial Spot", "Potato Early Blight", "Potato Late Blight",
    "Raspberry Healthy", "Soybean Healthy", "Squash Powdery Mildew",
    "Strawberry Healthy", "Strawberry Leaf Scorch",
    "Tomato Septoria Leaf Spot", "Tomato Yellow Leaf Curl Virus",
    "Tomato Bacterial Spot", "Tomato Late Blight", "Tomato Mosaic Virus",
    "Tomato Target Spot", "Tomato Leaf Mold", "Tomato Spider Mites",
    "Grape Healthy", "Grape Black Rot"
]

def predict():
    model = YOLO(MODEL)
    results = model.predict(
        source=SOURCE,
        conf=0.4,
        save=True,
        project="runs/predict",
        name="plant_disease_results2"
    )

    print("\n?? Detection Results:")
    for r in results:
        img_name = r.path.split("\\")[-1]
        detections = []
        for box in r.boxes:
            cls_id = int(box.cls)
            label  = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else f"class_{cls_id}"
            conf   = float(box.conf)
            detections.append(f"{label} ({conf:.1%})")
        if detections:
            print(f"  {img_name}: {', '.join(detections)}")
        else:
            print(f"  {img_name}: No detections")

if __name__ == "__main__":
    predict()
