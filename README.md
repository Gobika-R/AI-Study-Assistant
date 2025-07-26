# Study Assistant

A comprehensive AI-powered study companion that helps students with note summarization, topic explanations, quiz generation, and learning progress tracking.

## Features

### 🔍 **Text Summarization**
- Extract key points from lengthy notes and articles
- Provide concise summaries with readability analysis
- Calculate reading difficulty levels
- Word and sentence count statistics

### 💡 **Topic Explanation**
- Explain complex topics in simple terms
- Adjustable difficulty levels (Simple, Intermediate, Advanced)
- Suggested learning activities
- Related topic recommendations

### 📝 **Interactive Quizzes**
- Generate personalized quizzes on any topic
- Multiple-choice questions with explanations
- Real-time scoring and feedback
- Performance tracking across topics

### 🧠 **Learning Memory**
- Track all student interactions and progress
- Monitor quiz performance by topic
- Personalized study recommendations
- Learning history and statistics

## Repository

🔗 **GitHub Repository:** [https://github.com/yourusername/ai-study-assistant](https://github.com/yourusername/ai-study-assistant)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/ai-study-assistant.git
   cd ai-study-assistant
   ```

2. **Or download the project files**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Download required NLTK data (automatic on first run):**
   - The app will automatically download required NLTK packages
   - This includes punkt tokenizer and stopwords

4. **Run the application:**
   ```bash
   python app.py
   ```

5. **Open your browser and navigate to:**
   ```
   http://localhost:5000
   ```

## Project Structure

```
study-assistant/
│
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Web interface
├── student_memory.json   # Student data storage (created automatically)
└── README.md            # This file
```

## Usage Guide

### Getting Started
1. Launch the application and open it in your browser
2. The system will automatically create a unique student ID for tracking your progress
3. Navigate between different features using the tabs

### Summarizing Text
1. Go to the "Summarize" tab
2. Paste your text in the input area
3. Click "Summarize Text"
4. Review the summary, key points, and readability analysis

### Getting Topic Explanations
1. Go to the "Explain" tab
2. Enter the topic you want explained
3. Choose your preferred difficulty level
4. Click "Explain Topic"
5. Read the explanation and explore suggested activities

### Taking Quizzes
1. Go to the "Quiz" tab
2. Enter the topic for your quiz
3. Select the number of questions
4. Click "Start Quiz"
5. Answer each question and review explanations
6. See your final score and performance

### Viewing Learning Progress
1. Go to the "Memory" tab
2. Click "Refresh Memory" to see your current progress
3. Click "Get Recommendations" for personalized study suggestions
4. Review your topic performance and learning history

## Features in Detail

### Memory System
The Study Assistant remembers:
- All your interactions (summarizations, explanations, quizzes)
- Topics you've studied and how often
- Quiz performance by topic
- Timestamps of all activities

### Intelligent Recommendations
Based on your activity, the system provides:
- Suggestions to review topics with low quiz scores
- Related topics to explore
- Encouragement and study tips

### Readability Analysis
For summarized text, you'll see:
- Flesch Reading Ease score
- Flesch-Kincaid Grade Level
- Reading difficulty classification

## Technical Details

### Backend (Python/Flask)
- Flask web framework for the server
- NLTK for natural language processing
- JSON-based data persistence
- Extractive text summarization algorithm
- Built-in quiz question database

### Frontend (HTML/CSS/JavaScript)
- Bootstrap 5 for responsive design
- Modern gradient-based UI
- Interactive quiz interface
- Real-time progress tracking
- AJAX for seamless user experience

## Supported Topics

The system has built-in knowledge for:
- **Science**: Photosynthesis, Gravity, Biology concepts
- **Social Studies**: Democracy, Government, History
- **General**: Any topic (with generic explanations)

You can ask about any topic - the system will provide the best explanation possible!

## Browser Compatibility

Works on all modern browsers:
- Chrome, Firefox, Safari, Edge
- Mobile-friendly responsive design
- No additional plugins required

## Troubleshooting

### Common Issues:

1. **NLTK Download Errors:**
   - The app will automatically download required data
   - Ensure you have an internet connection on first run

2. **Port Already in Use:**
   - Change the port in app.py: `app.run(port=5001)`
   - Or stop other applications using port 5000

3. **Memory Not Saving:**
   - Ensure the app has write permissions in its directory
   - Check that student_memory.json is created

## Future Enhancements

Potential additions:
- Integration with AI APIs (OpenAI, etc.) for more advanced explanations
- Support for uploading files (PDF, DOCX)
- Advanced quiz types (fill-in-the-blank, matching)
- Study schedule and reminder system
- Export progress reports
- Multi-user support with authentication

## Contributing

This project is designed to be educational and extensible. Feel free to:
- Add new quiz questions to the database
- Improve the summarization algorithm
- Enhance the UI/UX
- Add new explanation topics
- Integrate with external APIs

## License

This project is open source and available for educational use.

---

**Happy Learning!** 🎓📚✨
