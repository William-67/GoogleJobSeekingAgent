job-seeking-ai/
├── job_seeking_agent.py      # Agent handling job seek
├── app.py                    # Flask backend services
├── templates/			# Front end page
	├── chat.html		# Chat page
	├── chat_history.html	# Check chat history page
	├── index.html		# Main page
	├── results.html	# Search result page
	└── start_chat.html 
├── requirements.txt          # Python Dependencies
├── config.py               # configuration
├── utils.py			
├── chats.py			#handling chat functions
└── README.md               

# 1. Clone the code
git clone https://github.com/William-67/GoogleJobSeekingAgent
cd GoogleJobSeekingAgent

# 2. create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate   # Windows

appenv\Scripts\activate   # Windows


# 3. Install dependencies
pip install -r requirements.txt

# 4. Set up .env
copy .env.example .env

# Add your own API Key in the .env


# 5. Run the app
python app.py
