import cv2
import numpy as np
from ultralytics import YOLO
import math

class ObjectDetector:
    def __init__(self):
        # Load YOLOv8 nano model (smaller, faster)
        print("Loading YOLO model...")
        self.model = YOLO('yolov8n.pt')  # Downloads automatically on first run
        
        # Initialize webcam
        self.cap = cv2.VideoCapture(1)
        if not self.cap.isOpened():
            raise ValueError("Could not open webcam")
        
        # Set webcam resolution
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        # Known reference for distance estimation (optional)
        # Assuming average person height is 170cm and appears as ~400 pixels
        self.pixels_per_cm = 400 / 170  # Rough calibration
        
    def calculate_distance(self, center1, center2):
        """Calculate Euclidean distance between two points"""
        x1, y1 = center1
        x2, y2 = center2
        distance_pixels = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return distance_pixels
    
    def pixels_to_cm(self, distance_pixels):
        """Convert pixel distance to approximate real-world distance"""
        return distance_pixels / self.pixels_per_cm
    
    def draw_bounding_box(self, frame, box, label, confidence, color=(0, 255, 0)):
        """Draw bounding box with label and confidence"""
        x1, y1, x2, y2 = map(int, box)
        
        # Draw rectangle
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Draw label background
        label_text = f"{label}: {confidence:.2f}"
        (text_width, text_height), _ = cv2.getTextSize(label_text, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        cv2.rectangle(frame, (x1, y1 - text_height - 10), (x1 + text_width, y1), color, -1)
        
        # Draw label text
        cv2.putText(frame, label_text, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return frame
    
    def get_box_center(self, box):
        """Get center point of bounding box"""
        x1, y1, x2, y2 = box
        center_x = int((x1 + x2) / 2)
        center_y = int((y1 + y2) / 2)
        return (center_x, center_y)
    
    def run(self):
        """Main detection loop"""
        print("Starting object detection. Press 'q' to quit.")
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                print("Failed to grab frame")
                break
            
            # Run YOLO detection
            results = self.model(frame, verbose=False)
            
            # Process detections
            detected_objects = []
            colors = [(0, 255, 0), (255, 0, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255)]
            
            for r in results:
                boxes = r.boxes
                if boxes is not None:
                    for i, box in enumerate(boxes):
                        # Get box coordinates, confidence, and class
                        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                        confidence = box.conf[0].cpu().numpy()
                        class_id = int(box.cls[0].cpu().numpy())
                        class_name = self.model.names[class_id]
                        
                        # Filter by confidence threshold
                        if confidence > 0.5:
                            color = colors[i % len(colors)]
                            
                            # Draw bounding box
                            self.draw_bounding_box(frame, [x1, y1, x2, y2], class_name, confidence, color)
                            
                            # Store object info
                            center = self.get_box_center([x1, y1, x2, y2])
                            detected_objects.append({
                                'center': center,
                                'box': [x1, y1, x2, y2],
                                'class': class_name,
                                'confidence': confidence
                            })
                            
                            # Draw center point
                            cv2.circle(frame, center, 5, color, -1)
            
            # Calculate distance if exactly 2 objects detected
            if len(detected_objects) == 2:
                center1 = detected_objects[0]['center']
                center2 = detected_objects[1]['center']
                
                # Calculate distance in pixels
                distance_pixels = self.calculate_distance(center1, center2)
                distance_cm = self.pixels_to_cm(distance_pixels)
                
                # Draw line between centers
                cv2.line(frame, center1, center2, (255, 255, 255), 2)
                
                # Display distance information
                distance_text = f"Distance: {distance_pixels:.1f}px ({distance_cm:.1f}cm)"
                cv2.putText(frame, distance_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                # Display object names
                obj1_name = detected_objects[0]['class']
                obj2_name = detected_objects[1]['class']
                objects_text = f"Objects: {obj1_name} <-> {obj2_name}"
                cv2.putText(frame, objects_text, (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            
            # Display object count
            count_text = f"Objects detected: {len(detected_objects)}"
            cv2.putText(frame, count_text, (10, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
            
            # Show instructions
            instruction_text = "Press 'q' to quit"
            cv2.putText(frame, instruction_text, (frame.shape[1] - 150, frame.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Display frame
            cv2.imshow('Object Detection with Distance Measurement', frame)
            
            # Check for quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        print("Program ended.")

def main():
    """Main function to run the object detector"""
    try:
        detector = ObjectDetector()
        detector.run()
    except ValueError as e:
        print(f"Error: {e}")
    except KeyboardInterrupt:
        print("\nProgram interrupted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
