import streamlit as st
import PIL.Image
import google.generativeai as genai
import time
import hashlib
import json
import pandas as pd
from fuzzywuzzy import fuzz  # Import the fuzzy matching function
import re
# Set page title, icon, and dark theme
st.set_page_config(page_title="Fiscal Forecasting", page_icon=">", layout="wide")
background_html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Underwater Bubble Background</title>
    <style>
        body {
            margin: 0;
            overflow: hidden;
            background: linear-gradient(45deg, #161d20 5%, #161d29 47.5%,#161d53 ,#161d52 95%);
         }
        canvas {
            display: block;
        }
    </style>
</head>
<body>
    <canvas id="bubblefield"></canvas>
    <script>
        // Setup canvas
        const canvas = document.getElementById('bubblefield');
        const ctx = canvas.getContext('2d');
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;

        // Arrays to store bubbles
        let bubbles = [];
        const numBubbles = 50;
        const glowDuration = 1000; // Glow duration in milliseconds

        // Function to initialize bubbles
        function initializeBubbles() {
            for (let i = 0; i < numBubbles; i++) {
                bubbles.push({
                    x: Math.random() * canvas.width,
                    y: Math.random() * canvas.height,
                    radius: Math.random() * 5 + 2, // Adjusted smaller bubble size
                    speedX: Math.random() * 0.5 - 0.25, // Adjusted slower speed
                    speedY: Math.random() * 0.5 - 0.25, // Adjusted slower speed
                    glow: false,
                    glowStart: 0
                });
            }
        }

        // Draw function
        function draw() {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            
            // Draw bubbles
            for (let i = 0; i < numBubbles; i++) {
                let bubble = bubbles[i];

                // Calculate glow intensity based on time elapsed since glow started
                let glowIntensity = 0;
                if (bubble.glow) {
                    let elapsedTime = Date.now() - bubble.glowStart;
                    glowIntensity = 0.8 * (1 - elapsedTime / glowDuration); // Decreasing glow intensity over time
                    if (elapsedTime >= glowDuration) {
                        bubble.glow = false; // Reset glow state after glow duration
                    }
                }

                ctx.beginPath();
                ctx.arc(bubble.x, bubble.y, bubble.radius, 0, Math.PI * 2);

                // Set glow effect if bubble should glow
                if (glowIntensity > 0) {
                    let gradient = ctx.createRadialGradient(bubble.x, bubble.y, 0, bubble.x, bubble.y, bubble.radius);
                    gradient.addColorStop(0, `rgba(255, 255, 255, ${glowIntensity})`);
                    gradient.addColorStop(1, 'rgba(255, 255, 255, 0)');
                    ctx.fillStyle = gradient;
                } else {
                    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)'; // Adjusted bubble transparency to 70%
                }
                
                ctx.fill();

                // Move bubbles based on speed
                bubble.x += bubble.speedX;
                bubble.y += bubble.speedY;

                // Wrap bubbles around edges of canvas
                if (bubble.x < -bubble.radius) {
                    bubble.x = canvas.width + bubble.radius;
                }
                if (bubble.x > canvas.width + bubble.radius) {
                    bubble.x = -bubble.radius;
                }
                if (bubble.y < -bubble.radius) {
                    bubble.y = canvas.height + bubble.radius;
                }
                if (bubble.y > canvas.height + bubble.radius) {
                    bubble.y = -bubble.radius;
                }
            }
            
            requestAnimationFrame(draw);
        }

        // Mouse move event listener to move bubbles towards cursor
        canvas.addEventListener('mousemove', function(event) {
            let mouseX = event.clientX;
            let mouseY = event.clientY;
            for (let i = 0; i < numBubbles; i++) {
                let bubble = bubbles[i];
                let dx = mouseX - bubble.x;
                let dy = mouseY - bubble.y;
                let distance = Math.sqrt(dx * dx + dy * dy);
                if (distance < 50) {
                    bubble.speedX = dx * 0.01;
                    bubble.speedY = dy * 0.01;
                    if (!bubble.glow) {
                        bubble.glow = true;
                        bubble.glowStart = Date.now();
                    }
                }
            }
        });

        // Start animation
        initializeBubbles();
        draw();

        // Resize canvas on window resize
        window.addEventListener('resize', function() {
            canvas.width = window.innerWidth;
            canvas.height = window.innerHeight;
            initializeBubbles();  // Reinitialize bubbles on resize
        });
    </script>
</body>
</html>
"""

# Embed the HTML code into the Streamlit app
st.components.v1.html(background_html, height=1000)
st.markdown("""
<style>
    iframe {
        position: fixed;
        left: 0;
        right: 0;
        top: 0;
        bottom: 0;
        border: none;
        height: 100%;
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
    <style>
        @keyframes gradientAnimation {
            0% {
                background-position: 0% 50%;
            }
            50% {
                background-position: 100% 50%;
            }
            100% {
                background-position: 0% 50%;
            }
        }

        .animated-gradient-text {
            font-family: "Graphik Semibold";
            font-size: 42px;
            background: linear-gradient(45deg, #22ebe8 30%, #dc14b7 55%, #fe647b 20%);
            background-size: 300% 200%;
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            animation: gradientAnimation 20s ease-in-out infinite;
        }
    </style>
    <p class="animated-gradient-text">
        Economic Forecast Bot!
    </p>
""", unsafe_allow_html=True)



# Initialize session state
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# Configure Google Generative AI with the API key
#GOOGLE_API_KEY = st.secrets['GEMINI_API_KEY']
GOOGLE_API_KEY = "AIzaSyCNX1H0w4y7dJPlwqvrxiW1OjAMf4dkFp0"
genai.configure(api_key=GOOGLE_API_KEY)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Define users and hashed passwords for simplicity
users = {
    "pranav.baviskar": hash_password("pranav123")
}

def login():
    col1, col2= st.columns([0.3, 0.7])  # Create three columns with equal width
    with col1:  # Center the input fields in the middle column
        st.title("Login")
        st.write("Username")
        username = st.text_input("",  label_visibility="collapsed")
        st.write("Password")
        password = st.text_input("", type="password",  label_visibility="collapsed")
        
        if st.button("Sign in"):
            hashed_password = hash_password(password)
            if username in users and users[username] == hashed_password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.success("Logged in successfully!")
                st.rerun()  # Refresh to show logged-in state
            else:
                st.error("Invalid username or password")

def logout():
    # Clear session state on logout
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.success("Logged out successfully!")
    st.rerun()  # Refresh to show logged-out state

# Path to the logo image
logo_url = "https://www.vgen.it/wp-content/uploads/2021/04/logo-accenture-ludo.png"

def generate_content(user_question,image):
    max_retries = 10
    delay = 10
    retry_count = 0
    while retry_count < max_retries:
        try:
            # Initialize the GenerativeModel
            print("Model definition")
            model = genai.GenerativeModel('gemini-1.5-pro')
            system_prompt = """You are provided with economic data. If the user requests a forecast, create a detailed forecast table for the next 5 years (2025–2029), unless a different period is specified. 
            Include brief calculations, brief key assumptions, and a concise summary at the end. Sectors are: Public Administration, Military, Security and Regional Administration, Municipal Services, Education, Health and Social Development, 
            Economic Resources, Infrastructure and Transportation, and General Items. Ensure the response is clear, precise, and includes only the forecast table, assumptions, and summary. 
            Response format should be:
            
            Assumptions:
            
            Table:
            | Year | Column 1 | Column 2 | Column 3 | Column 4 |
            |------|------------------------|----------|-----------|--------|
            | 2025 | 500                   | 400      | 300       | 200    |
            | 2026 | 520                   | 410      | 320       | 210    |
            | 2027 | 540                   | 420      | 340       | 220    |
            | 2028 | 560                   | 430      | 360       | 230    |
            | 2029 | 580                   | 440      | 380       | 240    |
            
            Summary:
            """
			
# Combine the system prompt with the user question
            prompt = f"{system_prompt}\n\n{user_question}"
# Generate content using the image
            print("Model generate")
            # st.write(prompt)
            response = model.generate_content([prompt, image], stream=True)
            response.resolve()
            print("Response text", response.text)
            return response.text  # Return generated text
        except Exception as e:
            retry_count += 1
            if retry_count == max_retries:
                st.error(f"Error generating content: Server not available. Please try again after sometime")
            time.sleep(delay)
    
    # Return None if all retries fail
    return None

def main():
    st.markdown("")
    col1, col2, col3 = st.columns([4, 1, 4])  # Create three columns

    generated_text = ""

    with col1:
        # Place tabs within col1
        tabs = st.tabs(["📄 Ask Question here", "⚙️ See Fiscal Data here"])

        # Document tab
        with tabs[0]:
            uploaded_images = ["KSAEco.png"]
            user_question = st.text_input("Ask a Question", key="user_question")
            #st.file_uploader("Upload images", type=["jpg", "jpeg", "png"], accept_multiple_files=True, label_visibility="collapsed")

                        # Inject custom CSS to hide the element
            hide_css = """
            <style>
                .st-emotion-cache-fis6aj, .e1b2p2ww10 {
                    color: white !important;
                    background-color: white !important;
                }
            </style>
            """
            st.markdown(hide_css, unsafe_allow_html=True)
            
            # Display uploaded images and data extraction button
            if uploaded_images:
                for uploaded_image in uploaded_images:
                    image = PIL.Image.open(uploaded_image)
                    button_label = f"Submit {uploaded_images.index(uploaded_image) + 1}" if len(uploaded_images) > 1 else "Submit"

                    if st.button(button_label):
                        with st.spinner("Evaluating..."):
                            generated_text = generate_content(user_question,image)  # Generate content from image

                   
        # System tab
        with tabs[1]:
            excel_file = "KSAEcoData.xlsx"  # Ensure this file is in your working directory
            try:
                df = pd.read_excel(excel_file)  # Read the Excel file
                st.dataframe(df)  # Display the data as a table
            except Exception as e:
                st.error(f"Error reading the Excel file: {e}")

    # Display extraction result in col3, separate from col1
    with col3:
        if generated_text:
            st.markdown("### Evaluation Results:")
            st.write(generated_text)

                
if __name__ == "__main__":
    if st.session_state.logged_in:
        col1, col2, col3 = st.columns([10, 10, 1.5])
        with col3:
            if st.button("Logout"):
                logout()
        main()
    else:
        login()
