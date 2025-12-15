import cv2
import numpy as np
from typing import List, Dict, Optional
import os

class FaceRecognitionService:
    def __init__(self):
        # In-memory storage: {user_id: [encoding1, encoding2, ...]}
        self.known_faces: Dict[str, List[np.ndarray]] = {}
        
        # Paths to models - Adjusted paths for new structure
        # Assuming models are still in the root 'models' directory or we need to adjust relative paths
        # Ideally, we should use absolute paths or configuration
        base_dir = os.getcwd() # Or use a config to get the base path
        self.detection_model_path = os.path.join(base_dir, "models/face_detection_yunet_2023mar.onnx")
        self.recognition_model_path = os.path.join(base_dir, "models/face_recognition_sface_2021dec.onnx")
        
        # Initialize models
        self.detector = cv2.FaceDetectorYN.create(
            self.detection_model_path,
            "",
            (320, 320),
            0.9,
            0.3,
            5000
        )
        self.recognizer = cv2.FaceRecognizerSF.create(
            self.recognition_model_path,
            ""
        )
        
        # Thresholds
        self.cosine_threshold = 0.363
        self.l2_threshold = 1.128

    def load_image(self, file_stream):
        """Load image from file stream."""
        # Read file stream into numpy array
        file_bytes = np.asarray(bytearray(file_stream.read()), dtype=np.uint8)
        image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
        return image

    def get_encoding(self, image) -> Optional[np.ndarray]:
        """Get face encoding from image. Returns None if no face found."""
        height, width, _ = image.shape
        self.detector.setInputSize((width, height))
        
        # Detect faces
        _, faces = self.detector.detect(image)
        
        if faces is None:
            return None
            
        # Use the first face found
        face = faces[0]
        
        # Align face
        aligned_face = self.recognizer.alignCrop(image, face)
        
        # Get feature
        feature = self.recognizer.feature(aligned_face)
        return feature

    def register_face(self, user_id: str, image_file) -> bool:
        """Register a new face for a user."""
        image = self.load_image(image_file)
        if image is None:
            return False
            
        encoding = self.get_encoding(image)
        
        if encoding is None:
            return False
            
        if user_id not in self.known_faces:
            self.known_faces[user_id] = []
            
        self.known_faces[user_id].append(encoding)
        return True

    def verify_face(self, user_id: str, image_file) -> Optional[bool]:
        """Verify if the image matches the registered user. Returns None if no face detected."""
        if user_id not in self.known_faces:
            return False
            
        image = self.load_image(image_file)
        if image is None:
            return None
            
        unknown_encoding = self.get_encoding(image)
        
        if unknown_encoding is None:
            return None
            
        # Compare with all registered encodings for this user
        for known_encoding in self.known_faces[user_id]:
            score = self.recognizer.match(known_encoding, unknown_encoding, cv2.FaceRecognizerSF_FR_COSINE)
            if score >= self.cosine_threshold:
                return True
                
        return False

    def recognize_face(self, image_file) -> Optional[str]:
        """Identify the user in the image."""
        image = self.load_image(image_file)
        if image is None:
            return None
            
        unknown_encoding = self.get_encoding(image)
        
        if unknown_encoding is None:
            return None
            
        best_score = 0.0
        best_user_id = None
        
        for user_id, encodings in self.known_faces.items():
            for known_encoding in encodings:
                score = self.recognizer.match(known_encoding, unknown_encoding, cv2.FaceRecognizerSF_FR_COSINE)
                if score > best_score:
                    best_score = score
                    best_user_id = user_id
                    
        if best_score >= self.cosine_threshold:
            return best_user_id
            
        return None
