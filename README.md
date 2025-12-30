CivicLens 🚀
An AI-Powered Civic Grievance Redressal System with Intelligent Verification & Gamified Rewards.

CivicLens AI is a smart governance platform designed to streamline the reporting and resolution of urban civic issues such as potholes, garbage piles, and broken infrastructure. By combining Deep Learning for automated verification and a rewards-based incentive model, it creates a transparent and accountable ecosystem for both citizens and authorities.

✨ Key Features
AI-Driven Issue Verification: Utilizes a MobileNetV2 Convolutional Neural Network (CNN) to automatically classify reported issues from images, significantly reducing the manual verification workload for authorities.

Mandatory Geolocation Integrity: Features a forced GPS-locking mechanism using native browser APIs to ensure that every report is submitted with authentic, real-time location data.

Civic Rewards (Gamification): Encourages active citizenship by awarding 50 Credit Points to users once their reported issue is officially resolved.

Authority Management Dashboard: A centralized interface for government officials to track, analyze (via GPS coordinates), and update the status of public grievances.

Smart Manual Fallback: If the AI model is unable to confidently identify an issue, the system provides a manual entry path to ensure no genuine citizen concern is ignored.

🛠️ Tech Stack
Backend: Python / Flask

AI/ML: TensorFlow & Keras (MobileNetV2)

Database: SQLite3

Frontend: HTML5, CSS3 (Jakarta Sans Typography), JavaScript

🚦 How It Works
Report: A citizen captures and uploads a photo of a civic issue. The system enforces a GPS prompt to lock the location.

Verify: The AI engine analyzes the image to confirm the type of issue.

Resolve: Local authorities access the report on their dashboard and take action.

Reward: Once the status is changed to 'Resolved', the citizen receives reward credits in their dashboard wallet.

🚀 Installation & Local Setup
Clone the Repository:

Bash

git clone https://github.com/himanshurajverma843325-boop/CivicLens.git
Install Dependencies:

Bash

pip install -r requirements.txt
Run the Application:

Bash

python app.py
Access the Portal: Open http://127.0.0.1:5000 in your web browser
