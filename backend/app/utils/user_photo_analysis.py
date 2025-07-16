import cv2
import numpy as np
import mediapipe as mp
from typing import Dict, List, Tuple, Optional
import json
from sklearn.cluster import KMeans
import math

class PhotoProcessingService:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.5
        )
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=True,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5
        )
    
    def extract_skin_tone(self, image_path: str) -> Dict[str, any]:
        """Extract dominant skin tone from image"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "Could not load image"}
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Use face detection to focus on face area for better skin tone extraction
            results = self.face_mesh.process(img_rgb)
            
            if results.multi_face_landmarks:
                # Extract face region
                h, w, _ = img_rgb.shape
                face_landmarks = results.multi_face_landmarks[0]
                
                # Get face bounding box
                x_coords = [int(landmark.x * w) for landmark in face_landmarks.landmark]
                y_coords = [int(landmark.y * h) for landmark in face_landmarks.landmark]
                
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                
                # Extract face region
                face_region = img_rgb[y_min:y_max, x_min:x_max]
                
                # Convert to LAB color space for better skin tone analysis
                lab_image = cv2.cvtColor(face_region, cv2.COLOR_RGB2LAB)
                
                # Create mask for skin-like colors
                lower_skin = np.array([20, 133, 77], dtype=np.uint8)
                upper_skin = np.array([255, 173, 127], dtype=np.uint8)
                mask = cv2.inRange(lab_image, lower_skin, upper_skin)
                
                # Apply mask to get skin pixels
                skin_pixels = face_region[mask > 0]
                
                if len(skin_pixels) > 0:
                    # Get dominant color using K-means
                    skin_pixels = skin_pixels.reshape(-1, 3)
                    kmeans = KMeans(n_clusters=1, random_state=42, n_init=10)
                    kmeans.fit(skin_pixels)
                    dominant_color = kmeans.cluster_centers_[0].astype(int)
                else:
                    # Fallback to face region mean
                    dominant_color = face_region.reshape(-1, 3).mean(axis=0).astype(int)
            else:
                # Fallback to overall image analysis
                img_resized = cv2.resize(img_rgb, (224, 224))
                dominant_color = img_resized.reshape(-1, 3).mean(axis=0).astype(int)
            
            # Convert to skin tone category
            skin_tone_category = self._classify_skin_tone(dominant_color)
            
            return {
                "rgb_values": dominant_color.tolist(),
                "hex_color": "#{:02x}{:02x}{:02x}".format(dominant_color[0], dominant_color[1], dominant_color[2]),
                "skin_tone_category": skin_tone_category,
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _classify_skin_tone(self, rgb_color: np.ndarray) -> str:
        """Classify RGB color into skin tone categories"""
        # Convert RGB to ITA (Individual Typology Angle) for skin tone classification
        r, g, b = rgb_color
        
        # Calculate brightness
        brightness = (0.299 * r + 0.587 * g + 0.114 * b)
        
        # Skin tone classification based on brightness and color values
        if brightness > 200:
            return "very_light"
        elif brightness > 170:
            return "light"
        elif brightness > 140:
            return "medium_light"
        elif brightness > 110:
            return "medium"
        elif brightness > 80:
            return "medium_dark"
        elif brightness > 50:
            return "dark"
        else:
            return "very_dark"
    
    def extract_body_measurements(self, image_path: str) -> Dict[str, any]:
        """Extract body measurements and shape from full-body image"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return {"error": "Could not load image"}
            
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            results = self.pose.process(img_rgb)
            
            if not results.pose_landmarks:
                return {"error": "No pose detected in image"}
            
            landmarks = results.pose_landmarks.landmark
            h, w, _ = img_rgb.shape
            
            # Extract key body points
            key_points = self._extract_key_points(landmarks, w, h)
            
            # Calculate body measurements
            measurements = self._calculate_body_measurements(key_points)
            
            # Determine body type
            body_type = self._determine_body_type(measurements)
            
            return {
                "measurements": measurements,
                "body_type": body_type,
                "key_points": key_points,
                "success": True
            }
            
        except Exception as e:
            return {"error": str(e), "success": False}
    
    def _extract_key_points(self, landmarks, width: int, height: int) -> Dict[str, Tuple[int, int]]:
        """Extract key body points from pose landmarks"""
        key_points = {}
        
        # Map MediaPipe landmark indices to body parts
        landmark_map = {
            'nose': 0,
            'left_shoulder': 11,
            'right_shoulder': 12,
            'left_elbow': 13,
            'right_elbow': 14,
            'left_wrist': 15,
            'right_wrist': 16,
            'left_hip': 23,
            'right_hip': 24,
            'left_knee': 25,
            'right_knee': 26,
            'left_ankle': 27,
            'right_ankle': 28
        }
        
        for part, idx in landmark_map.items():
            if idx < len(landmarks):
                landmark = landmarks[idx]
                if landmark.visibility > 0.5:  # Only use visible landmarks
                    x = int(landmark.x * width)
                    y = int(landmark.y * height)
                    key_points[part] = (x, y)
        
        return key_points
    
    def _calculate_body_measurements(self, key_points: Dict[str, Tuple[int, int]]) -> Dict[str, float]:
        """Calculate body measurements from key points"""
        measurements = {}
        
        try:
            # Shoulder width
            if 'left_shoulder' in key_points and 'right_shoulder' in key_points:
                left_shoulder = key_points['left_shoulder']
                right_shoulder = key_points['right_shoulder']
                shoulder_width = math.sqrt((left_shoulder[0] - right_shoulder[0])**2 + 
                                         (left_shoulder[1] - right_shoulder[1])**2)
                measurements['shoulder_width'] = shoulder_width
            
            # Hip width
            if 'left_hip' in key_points and 'right_hip' in key_points:
                left_hip = key_points['left_hip']
                right_hip = key_points['right_hip']
                hip_width = math.sqrt((left_hip[0] - right_hip[0])**2 + 
                                    (left_hip[1] - right_hip[1])**2)
                measurements['hip_width'] = hip_width
            
            # Waist approximation (midpoint between shoulders and hips)
            if ('left_shoulder' in key_points and 'right_shoulder' in key_points and
                'left_hip' in key_points and 'right_hip' in key_points):
                
                # Calculate waist position
                shoulder_mid_y = (key_points['left_shoulder'][1] + key_points['right_shoulder'][1]) / 2
                hip_mid_y = (key_points['left_hip'][1] + key_points['right_hip'][1]) / 2
                waist_y = shoulder_mid_y + (hip_mid_y - shoulder_mid_y) * 0.7
                
                # Estimate waist width (this is approximate)
                waist_width = measurements.get('shoulder_width', 0) * 0.8
                measurements['waist_width'] = waist_width
            
            # Body height
            if 'nose' in key_points and ('left_ankle' in key_points or 'right_ankle' in key_points):
                nose_y = key_points['nose'][1]
                ankle_y = min(key_points.get('left_ankle', (0, float('inf')))[1],
                            key_points.get('right_ankle', (0, float('inf')))[1])
                if ankle_y != float('inf'):
                    body_height = ankle_y - nose_y
                    measurements['body_height'] = body_height
            
        except Exception as e:
            measurements['error'] = str(e)
        
        return measurements
    
    def _determine_body_type(self, measurements: Dict[str, float]) -> str:
        """Determine body type based on measurements"""
        if not measurements or len(measurements) < 3:
            return "unknown"
        
        shoulder_width = measurements.get('shoulder_width', 0)
        waist_width = measurements.get('waist_width', 0)
        hip_width = measurements.get('hip_width', 0)
        
        if shoulder_width == 0 or hip_width == 0:
            return "unknown"
        
        # Calculate ratios
        shoulder_hip_ratio = shoulder_width / hip_width
        waist_hip_ratio = waist_width / hip_width if hip_width > 0 else 0
        waist_shoulder_ratio = waist_width / shoulder_width if shoulder_width > 0 else 0
        
        # Body type classification
        if shoulder_hip_ratio > 1.05:
            return "inverted_triangle"
        elif shoulder_hip_ratio < 0.95:
            return "pear"
        elif waist_hip_ratio < 0.75 and waist_shoulder_ratio < 0.75:
            return "hourglass"
        elif waist_hip_ratio > 0.85:
            return "apple"
        else:
            return "rectangle"
    
    def process_user_photos(self, profile_photo_path: str, body_photos_paths: List[str]) -> Dict[str, any]:
        """Process all user photos and extract features"""
        results = {
            "skin_tone": None,
            "body_measurements": None,
            "body_type": None,
            "success": False,
            "errors": []
        }
        
        try:
            # Process profile photo for skin tone
            if profile_photo_path:
                skin_tone_result = self.extract_skin_tone(profile_photo_path)
                if skin_tone_result.get("success"):
                    results["skin_tone"] = skin_tone_result["skin_tone_category"]
                    results["skin_tone_hex"] = skin_tone_result["hex_color"]
                else:
                    results["errors"].append(f"Skin tone extraction failed: {skin_tone_result.get('error')}")
            
            # Process body photos for measurements
            if body_photos_paths:
                for body_photo_path in body_photos_paths:
                    body_result = self.extract_body_measurements(body_photo_path)
                    if body_result.get("success"):
                        results["body_measurements"] = body_result["measurements"]
                        results["body_type"] = body_result["body_type"]
                        break  # Use first successful measurement
                    else:
                        results["errors"].append(f"Body measurement extraction failed: {body_result.get('error')}")
            
            # If we have either skin tone or body measurements, consider it a success
            if results["skin_tone"] or results["body_measurements"]:
                results["success"] = True
            
        except Exception as e:
            results["errors"].append(f"General processing error: {str(e)}")
        
        return results

