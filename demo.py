"""
Study Assistant Demo Script
Demonstrates the enhanced features and capabilities
"""

def demo_text_for_summarization():
    """Returns sample text perfect for testing summarization"""
    return """
    Artificial Intelligence (AI) is a rapidly evolving field that focuses on creating computer systems capable of performing tasks that typically require human intelligence. These tasks include learning, reasoning, problem-solving, perception, and language understanding. AI can be divided into two main categories: narrow AI and general AI. Narrow AI, also known as weak AI, is designed to perform specific tasks, such as playing chess, recognizing speech, or recommending products. This type of AI is what we see in most current applications, from virtual assistants like Siri and Alexa to recommendation algorithms on social media platforms.

    General AI, also called strong AI or artificial general intelligence (AGI), refers to machines that would have the ability to understand, learn, and apply knowledge across a wide range of tasks at a level equal to or beyond human capability. While general AI remains largely theoretical and is still a subject of ongoing research, it represents the ultimate goal for many AI researchers. The development of AI has been influenced by various fields, including computer science, mathematics, psychology, neuroscience, and philosophy.

    Machine learning, a subset of AI, has been particularly instrumental in recent advances. It involves training algorithms on large datasets to recognize patterns and make predictions or decisions without being explicitly programmed for each specific task. Deep learning, which uses neural networks with multiple layers, has enabled breakthroughs in image recognition, natural language processing, and game playing. However, AI also presents challenges and ethical considerations, including concerns about job displacement, privacy, bias in algorithms, and the need for responsible development and deployment of AI systems.
    """

def demo_topics_for_explanation():
    """Returns topics that work well with the explanation feature"""
    return [
        "photosynthesis",
        "gravity", 
        "democracy",
        "evolution",
        "climate change",
        "artificial intelligence",
        "quantum physics",
        "ecosystem",
        "renewable energy"
    ]

def demo_quiz_topics():
    """Returns topics with built-in quiz questions"""
    return [
        "photosynthesis",
        "gravity",
        "democracy", 
        "evolution",
        "climate change"
    ]

def usage_tips():
    """Provides tips for using the enhanced Study Assistant"""
    return """
    🎯 USAGE TIPS FOR ENHANCED STUDY ASSISTANT:

    📝 SUMMARIZATION:
    • Paste articles, research papers, or long notes (up to 10,000 characters)
    • Check the confidence score - higher scores indicate better summaries
    • Note the compression ratio to see how much the text was condensed
    • Use the readability score to understand text difficulty

    💡 EXPLANATIONS:
    • Try topics like: photosynthesis, gravity, democracy, evolution, climate change
    • Experiment with different difficulty levels for the same topic
    • Click on related topic badges to explore connected concepts
    • Check estimated reading time to plan your study session

    🧠 QUIZZES:
    • Start with built-in topics for the best question quality
    • Notice difficulty indicators on each question (easy/medium/hard)
    • Review the difficulty breakdown after completing a quiz
    • Use "Get Study Tips" for personalized recommendations

    📊 MEMORY & PROGRESS:
    • Check your learning statistics in the Memory tab
    • View recent activity and topics studied
    • Get personalized recommendations based on your performance
    • Track quiz performance across different subjects

    🎨 UI FEATURES:
    • Enjoy the animated gradient background
    • Notice smooth hover effects and animations
    • Use progress bars during loading for better feedback
    • Look for confidence and performance indicators
    """

if __name__ == "__main__":
    print("Study Assistant Demo Resources")
    print("=" * 50)
    print("\n📖 Sample Text for Summarization:")
    print(demo_text_for_summarization())
    
    print("\n🎯 Recommended Topics for Explanation:")
    for topic in demo_topics_for_explanation():
        print(f"  • {topic}")
    
    print("\n🧠 Quiz Topics (with built-in questions):")
    for topic in demo_quiz_topics():
        print(f"  • {topic}")
    
    print(usage_tips())
