import numpy as np
import pydicom
import cv2
from skimage import morphology
from skimage.measure import label, regionprops
from scipy.ndimage import binary_fill_holes
from skimage.feature import graycomatrix, graycoprops
import base64
import io
from PIL import Image

def load_dicom_image(dicom_path):
    dicom_data = pydicom.dcmread(dicom_path)
    image = dicom_data.pixel_array.astype(np.float32)
    image = image * dicom_data.RescaleSlope + dicom_data.RescaleIntercept
    image_resized = cv2.resize(image, (256, 256), interpolation=cv2.INTER_LINEAR)
    return image_resized

def normalize_img(img):
    img = (img - np.min(img)) / (np.max(img) - np.min(img) + 1e-5)
    return img

def create_lung_masks(hu_image):
    lung_mask = (hu_image > -950) & (hu_image < -400)
    lung_mask_filled = binary_fill_holes(lung_mask)
    lung_mask_cleaned = morphology.remove_small_objects(lung_mask_filled, min_size=1500)

    labeled_mask = label(lung_mask_cleaned)
    regions = regionprops(labeled_mask)
    if len(regions) < 2:
        return None, None
    regions = sorted(regions, key=lambda r: r.area, reverse=True)[:2]
    regions_sorted_by_x = sorted(regions, key=lambda r: np.mean(r.coords[:, 1]))

    right_mask = np.zeros_like(hu_image, dtype=np.uint8)
    left_mask = np.zeros_like(hu_image, dtype=np.uint8)

    for coord in regions_sorted_by_x[0].coords:
        right_mask[coord[0], coord[1]] = 1
    for coord in regions_sorted_by_x[1].coords:
        left_mask[coord[0], coord[1]] = 1

    return left_mask, right_mask

def extract_features(lung_image, mask):
    region = lung_image * mask
    hu_values = region[mask == 1]
    mean_hu = np.mean(hu_values)
    std_hu = np.std(hu_values)
    lung_8bit = (normalize_img(region) * 255).astype(np.uint8)
    glcm = graycomatrix(lung_8bit, distances=[1], angles=[0], levels=256, symmetric=True, normed=True)
    contrast = graycoprops(glcm, 'contrast')[0, 0]
    homogeneity = graycoprops(glcm, 'homogeneity')[0, 0]
    return mean_hu, std_hu, contrast, homogeneity

def classify(mean_hu, std_hu, contrast, homogeneity):
    if mean_hu < -700 and std_hu < 100 and homogeneity > 0.5:
        return "Normal", 0.95
    elif -700 <= mean_hu <= -300 and std_hu < 150 and homogeneity > 0.4:
        return "GGO", 0.89
    elif mean_hu > -100 and std_hu > 100 and homogeneity < 0.3:
        if mean_hu > 150:
            return "Consolidation (Severe)", 0.96
        elif mean_hu > 50:
            return "Consolidation (Mild)", 0.92
        else:
            return "Consolidation (Normal)", 0.88
    elif -700 <= mean_hu <= -300 and contrast > 50 and homogeneity < 0.4:
        return "Crazy Paving", 0.90
    elif mean_hu > -300 and contrast > 70 and homogeneity < 0.3:
        return "Fibrosis", 0.91
    return "GGO", 0.6

def predict_dicom(dicom_path):
    hu_img = load_dicom_image(dicom_path)
    left_mask, _ = create_lung_masks(hu_img)
    if left_mask is None:
        return "Lung Not Detected", 0.0
    mean_hu, std_hu, contrast, homogeneity = extract_features(hu_img, left_mask)
    label, confidence = classify(mean_hu, std_hu, contrast, homogeneity)
    return label, confidence
