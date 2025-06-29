# NEMESIS Legal Aversary using GenAI

An AI-powered legal adversary for Indian Law, helping legal professionals train and improve their argumentation skills.

## Project Structure

```
nemesis/
├── nemesis_run.ipynb       # model run with gradio interface on colab
├── app.py                  # Flask backend server
├── requirements.txt        # Python dependencies
├── index.html              # Landing page
├── login.html              # Login/Registration page
└── chat.html               # Main chat interface
```

## Setup Instructions

### 1. Run model on colab

Run nemesis_run.ipynb on google colab using T4 GPU, connect to mounted google drive at dhruv.pai167@gmail.com, then get the gradio API link.

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Flask Backend Server

Copy the link from Gradio API and paste it in required space.

```bash
python app.py
```
This will start the server on http://127.0.0.1:5000

### 4. Serve the HTML Files

You can use any simple HTTP server to serve the HTML files. For example, using Python's built-in HTTP server:

```bash
# In a new terminal window, navigate to the directory containing your HTML files
python -m http.server 8000
```

This will serve your website at http://localhost:8000

### 5. Access the Application

Open your browser and go to http://localhost:8000 to access the NEMESIS application.

## Usage Flow

1. The user begins at the landing page (index.html)
2. They click "GET STARTED" to go to the login page (login.html)
3. After login, they're redirected to the chat interface (chat.html)
4. In the chat interface, they can:
   - Select case type from the dropdown
   - Select their client's position
   - Enter relevant acts and codes
   - Send messages to the AI and receive responses

## Note

The Gradio API link in app.py may expire. If this happens, you'll need to update it with a new link to your hosted model.
