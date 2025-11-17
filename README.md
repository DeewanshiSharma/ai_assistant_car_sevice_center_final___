# Futuristic AI Voice Assistant 🤖

A desktop voice assistant with a dynamic, futuristic user interface powered by the Google Gemini API. This application uses your browser's built-in speech capabilities and a Python backend to create an interactive AI experience.



## ✨ Features

* **Voice Recognition & Synthesis**: Uses the browser's Web Speech API to listen to commands and speak responses.
* **AI-Powered Conversations**: Integrates with the Google Gemini API (`gemini-1.5-flash`) for intelligent, general-purpose conversations.
* **Custom Hardcoded Commands**:
    * Responds with creator information ("I was created by Veera karthick").
    * Provides specific details when asked about Veera Karthick.
* **Application Launcher**: Can open applications on your local machine (customizable for Windows and macOS).
* **Futuristic UI**: Features a dark theme with a glowing, animated orb and a dynamic particle-constellation background.
* **Secure API Key Management**: Uses a `.env` file to keep your Google Gemini API key safe and out of the source code.

## 💻 Technology Stack

* **Backend**: Python 3, Flask
* **Frontend**: HTML5, CSS3, JavaScript
* **API**: Google Gemini API
* **Python Libraries**: `requests`, `python-dotenv`

## 🚀 Setup and Installation

Follow these steps to get the project running on your local machine.

### 1. Prerequisites

* Python 3.7+
* A modern web browser that supports the Web Speech API (e.g., Google Chrome, Edge).
* A Google Gemini API key.

### 2. Clone the Repository

```bash
git clone <your-repository-url>
cd voice-assistant
```

### 3. Set Up a Virtual Environment

It's highly recommended to use a virtual environment to keep project dependencies isolated.

* **On Windows:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    ```

* **On macOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

### 4. Install Dependencies

Install all the required Python packages from the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5. Set Up Your API Key

1.  In the root directory of the project (`voice-assistant/`), create a file named `.env`.
2.  Open the `.env` file and add your Gemini API key in the following format:

    ```
    GEMINI_API_KEY="YOUR_API_KEY_HERE"
    ```

    Replace `YOUR_API_KEY_HERE` with your actual secret key.

### 6. Customize Applications (Optional)

Open the `app.py` file and find the `apps_windows` or `apps_macos` dictionaries. You can add or modify the application names and their executable paths to match your system.

### 7. Run the Application

Start the Flask backend server.

```bash
python app.py
```

The server will start, and you will see an output like:
`* Running on http://127.0.0.1:5000`

### 8. Access the Assistant

Open your web browser and navigate to **`http://127.0.0.1:5000`**. The browser will likely ask for permission to use your microphone. Click **"Allow"**.

You can now click the orb and start speaking!#
