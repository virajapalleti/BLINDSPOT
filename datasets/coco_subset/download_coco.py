import fiftyone.zoo as foz
import fiftyone as fo

YOUR_CLASSES = [
    "person",
    "chair",
    "dining table",
    "couch",
    "toilet",
    "bed"    # remove if not needed
]

dataset = foz.load_zoo_dataset(
    "coco-2017",
    split="train",
    classes=YOUR_CLASSES,
    max_samples=2000,
    label_types=["detections"],
)

dataset.export(
    export_dir="datasets/coco_subset/train",    
    dataset_type=fo.types.YOLOv5Dataset,
    classes=YOUR_CLASSES,
)

print(f"Downloaded {len(dataset)} images")