# ROS2 Perception & Tracking System 🤖

A simulation-based autonomous perception pipeline built with ROS2, featuring real-time object detection, Kalman Filter tracking, and autonomous decision-making logic.

![ROS2](https://img.shields.io/badge/ROS2-Jazzy-blue)
![Python](https://img.shields.io/badge/Python-3.12-green)
![OpenCV](https://img.shields.io/badge/OpenCV-4.x-red)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Overview

This project demonstrates a complete **perception-to-control pipeline** for autonomous systems. Instead of relying on expensive hardware, it uses **software-in-the-loop (SIL) simulation** to validate core robotics concepts:

- **Perception**: Detect and track objects using computer vision
- **State Estimation**: Predict object motion using Kalman Filter
- **Decision Making**: Autonomous navigation logic based on object position
- **Control**: Generate velocity commands in real-time

### 🎯 Why This Project?

> **"A working pipeline > a fancy model"**

This project prioritizes **understanding the full robotics stack** over complex algorithms. It proves that you can build a functional autonomous system with:
- Simple color-based detection (no heavy ML models)
- Classical state estimation (Kalman Filter)
- Rule-based control logic

Perfect for learning ROS2 architecture, testing perception algorithms, and demonstrating software-in-the-loop testing capabilities.

---

## 🏗️ System Architecture

┌─────────────────────────────────────────────────────────────────────┐
│                        ROS2 Perception Stack                         │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────┐      ┌────────────────┐      ┌──────────────┐    │
│  │ Camera Node  │      │ Tracker Node   │      │ Mission Node │    │
│  │              │      │                │      │              │    │
│  │ 📹 Video     │─────▶│ 🔍 Detection   │─────▶│ 🤖 Decision  │    │
│  │    Input     │      │ 🎯 Kalman      │      │    Logic     │    │
│  │              │      │    Filter      │      │              │    │
│  └──────────────┘      └────────────────┘      └──────────────┘    │
│         │                       │                       │           │
│         ▼                       ▼                       ▼           │
│  /camera/image_raw      /object/position            /cmd_vel        │
│  (sensor_msgs/Image)    (geometry_msgs/Point)      (geometry_msgs/  │
│                                                      Twist)          │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘


### 🔧 Node Details

#### 1️⃣ **Camera Node** (`camera_node.py`)
- **Publishes**: `/camera/image_raw` (sensor_msgs/Image)
- **Function**: Streams video frames from webcam or prerecorded video
- **Frequency**: ~30 Hz

#### 2️⃣ **Tracker Node** (`tracker_node.py`)
- **Subscribes**: `/camera/image_raw`
- **Publishes**: `/object/position` (geometry_msgs/Point)
- **Functions**:
  - Converts BGR to HSV color space
  - Applies color thresholding (red object detection)
  - Finds contours and calculates centroid
  - **Kalman Filter** for smooth position tracking
  - Normalizes position to [-1.0, 1.0] range

**Kalman Filter State**:
- **State Vector**: `[x, y, vx, vy]` (position + velocity)
- **Measurement**: `[x, y]` (detected centroid)
- **Process Noise**: 0.03
- **Measurement Noise**: 0.5

#### 3️⃣ **Mission Node** (`mission_node.py`)
- **Subscribes**: `/object/position`
- **Publishes**: `/cmd_vel` (geometry_msgs/Twist)
- **Control Logic**:
  - **Object Left** (x < -0.2) → Turn Left (angular.z = 0.5)
  - **Object Right** (x > 0.2) → Turn Right (angular.z = -0.5)
  - **Object Centered** (-0.2 ≤ x ≤ 0.2) → Move Forward (linear.x = 0.5)
  - **Object Lost** (z = 0.0) → Stop (all velocities = 0)

---

## 📦 Installation

### Prerequisites
- **OS**: Ubuntu 22.04 (Jammy) or 24.04 (Noble)
- **ROS2**: Humble or Jazzy
- **Python**: 3.10+
- **WSL2**: (if running on Windows)

### Step 1: Install ROS2 Dependencies
```bash
# For Ubuntu 24.04 + ROS2 Jazzy
sudo apt update
sudo apt install ros-jazzy-desktop python3-pip python3-colcon-common-extensions -y

# Install Python packages
pip3 install opencv-python numpy==1.26.4
```

### Step 2: Clone & Build
```bash
# Create workspace
mkdir -p ~/ros2_perception/src
cd ~/ros2_perception

# Clone repository
git clone https://github.com/RoKenobi/ros2-perception-stack.git src/perception_stack

# Build
colcon build
source install/setup.bash
```

### Step 3: Prepare Test Video (Optional)
If not using a webcam, place a video file in your home directory:
```bash
# Example: red object moving across frame
cp /path/to/your/video.mp4 ~/test_video.mp4
```

---

## 🚀 Usage

### Terminal 1: Launch Camera Node
```bash
cd ~/ros2_perception
source install/setup.bash
ros2 run perception_stack camera_node
```

### Terminal 2: Launch Tracker Node
```bash
cd ~/ros2_perception
source install/setup.bash
ros2 run perception_stack tracker_node
```

### Terminal 3: Launch Mission Node
```bash
cd ~/ros2_perception
source install/setup.bash
ros2 run perception_stack mission_node
```

### Monitor Data Flow
```bash
# View tracked position
ros2 topic echo /object/position

# View velocity commands
ros2 topic echo /cmd_vel

# Visualize graph
rqt_graph
```

---

## 🎥 Demo

### Expected Output

**Terminal logs showing autonomous decisions:**
```
[INFO] [mission_node]: Object Left -> TURN LEFT
[INFO] [mission_node]: Object Center -> FORWARD
[INFO] [mission_node]: Object Lost -> STOP
```

**Position data from Kalman Filter:**
```yaml
x: -0.96    # Object on left side
y: -0.97    # Vertical position
z: 1.0      # 1.0 = detected, 0.0 = lost
```

---

## 🔬 Technical Deep Dive

### Why Kalman Filter?

The Kalman Filter serves two critical purposes:

1. **Noise Reduction**: Raw detection from color thresholding can be jittery due to:
   - Lighting changes
   - Compression artifacts
   - Detection noise

2. **Prediction**: When the object is temporarily occluded or lost, the Kalman Filter:
   - Predicts position based on velocity
   - Maintains tracking continuity
   - Smooths the trajectory

### Color Detection Pipeline

```python
# 1. Convert to HSV (better color segmentation than RGB)
hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

# 2. Define red color range
lower_red = np.array([0, 70, 50])
upper_red = np.array([10, 255, 255])

# 3. Create binary mask
mask = cv2.inRange(hsv, lower_red, upper_red)

# 4. Find largest contour
contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
c = max(contours, key=cv2.contourArea)

# 5. Calculate centroid
x, y, w, h = cv2.boundingRect(c)
center_x, center_y = x + w//2, y + h//2
```

### Normalization Logic

Position is normalized to `[-1.0, 1.0]` for platform-independent control:

```python
norm_x = (pixel_x - image_width/2) / (image_width/2)
# Result: -1.0 (far left) to 1.0 (far right)
```

This allows the same logic to work on:
- 640x480 resolution
- 1920x1080 resolution
- Any aspect ratio

---

## 📂 Project Structure

```
ros2_perception/
├── src/
│   └── perception_stack/
│       ├── perception_stack/
│       │   ├── __init__.py
│       │   ├── camera_node.py       # Video streaming
│       │   ├── tracker_node.py      # Detection + Kalman
│       │   └── mission_node.py      # Control logic
│       ├── setup.py
│       └── package.xml
├── .gitignore
└── README.md
```

---

## 🛠️ Customization

### Track a Different Color

Edit `tracker_node.py`:
```python
# For blue objects
lower_blue = np.array([100, 70, 50])
upper_blue = np.array([130, 255, 255])
```

### Adjust Control Sensitivity

Edit `mission_node.py`:
```python
# Tighter centering threshold
if self.target_x < -0.1:      # was -0.2
    twist.angular.z = 0.8     # faster turn
```

### Use Webcam Instead of Video

Edit `camera_node.py`:
```python
self.cap = cv2.VideoCapture(0)  # 0 = default webcam
```

---

## 🧪 Testing & Validation

### Test 1: Data Flow
```bash
ros2 topic list
# Should show:
# /camera/image_raw
# /object/position
# /cmd_vel
```

### Test 2: Message Rate
```bash
ros2 topic hz /object/position
# Expected: ~30 Hz
```

### Test 3: Visualization
```bash
rqt_image_view /camera/image_raw
```

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- [ ] Add YOLOv5/v8 detection for multi-object tracking
- [ ] Implement data association (Hungarian algorithm)
- [ ] Add RViz visualization
- [ ] Support multiple color tracking
- [ ] Gazebo simulation integration

---

## 📚 Learning Resources

- [ROS2 Documentation](https://docs.ros.org/)
- [OpenCV Color Detection](https://docs.opencv.org/4.x/df/d9d/tutorial_py_colorspaces.html)
- [Kalman Filter Explained](https://www.bzarg.com/p/how-a-kalman-filter-works-in-pictures/)
- [ROS2 Humble Tutorials](https://docs.ros.org/en/humble/Tutorials.html)

---

##  License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👨 Author

**RoKenobi**  
[GitHub](https://github.com/RoKenobi) | [LinkedIn](YOUR_LINKEDIN_URL)

*Built with ❤️ for learning robotics and autonomous systems*

---

## 🙏 Acknowledgments

- ROS2 Community
- OpenCV Team
- Inspired by BeeX robotics challenges

---

<div align="center">

**If this helped you learn ROS2, please ⭐ star the repo!**

*Happy Coding & Happy Robotics! 🤖*

</div>
