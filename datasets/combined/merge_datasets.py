import os
import shutil
import random

# Paths
COCO_IMAGES = "datasets/coco_subset/train/images/val"
COCO_LABELS = "datasets/coco_subset/train/labels/val"

STAIRS_IMAGES = "datasets/stairs/stairs/final stairs"
STAIRS_LABELS = "datasets/stairs/stairs/labels"

OUT_TRAIN_IMAGES = "datasets/combined/images/train"
OUT_TRAIN_LABELS = "datasets/combined/labels/train"
OUT_VAL_IMAGES   = "datasets/combined/images/val"
OUT_VAL_LABELS   = "datasets/combined/labels/val"

# Create output folders
for folder in [OUT_TRAIN_IMAGES, OUT_TRAIN_LABELS, OUT_VAL_IMAGES, OUT_VAL_LABELS]:
    os.makedirs(folder, exist_ok=True)

# --- Copy COCO (already split, all goes to train) ---
for fname in os.listdir(COCO_IMAGES):
    shutil.copy(os.path.join(COCO_IMAGES, fname), OUT_TRAIN_IMAGES)

for fname in os.listdir(COCO_LABELS):
    shutil.copy(os.path.join(COCO_LABELS, fname), OUT_TRAIN_LABELS)

print(f"COCO copied.")

# --- Copy Stairs (flat, split 80/20) ---
image_exts = (".jpg", ".jpeg", ".png")
stair_images = [f for f in os.listdir(STAIRS_IMAGES) if f.lower().endswith(image_exts)]

random.seed(42)
random.shuffle(stair_images)

split = int(0.8 * len(stair_images))
train_imgs = stair_images[:split]
val_imgs   = stair_images[split:]

def copy_stairs(img_list, out_img_dir, out_lbl_dir):
    for img_fname in img_list:
        # copy image
        shutil.copy(os.path.join(STAIRS_IMAGES, img_fname), out_img_dir)
        # copy matching label
        label_fname = os.path.splitext(img_fname)[0] + ".txt"
        label_src = os.path.join(STAIRS_LABELS, label_fname)
        if os.path.exists(label_src):
            shutil.copy(label_src, out_lbl_dir)

copy_stairs(train_imgs, OUT_TRAIN_IMAGES, OUT_TRAIN_LABELS)
copy_stairs(val_imgs,   OUT_VAL_IMAGES,   OUT_VAL_LABELS)

print(f"Stairs — train: {len(train_imgs)}, val: {len(val_imgs)}")
print("Merge complete. datasets/combined is ready.")