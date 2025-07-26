import os
from flask import Flask, render_template, request, jsonify, session
from datetime import datetime
import json
import nltk
import textstat
import markdown
import re
from typing import Dict, List, Optional
import uuid

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import Counter

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this')

class StudyAssistant:
    def __init__(self):
        self.memory_file = 'student_memory.json'
        self.load_memory()
    
    def load_memory(self):
        """Load student memory from file"""
        try:
            with open(self.memory_file, 'r', encoding='utf-8') as f:
                self.memory = json.load(f)
        except FileNotFoundError:
            self.memory = {}
    
    def save_memory(self):
        """Save student memory to file"""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, indent=2, ensure_ascii=False)
    
    def get_student_id(self, session_id: str) -> str:
        """Get or create student ID"""
        if 'student_id' not in session:
            session['student_id'] = str(uuid.uuid4())
        return session['student_id']
    
    def add_to_memory(self, student_id: str, interaction_type: str, content: str, topic: str = None):
        """Add interaction to student memory"""
        if student_id not in self.memory:
            self.memory[student_id] = {
                'interactions': [],
                'topics_studied': {},
                'quiz_performance': {},
                'preferences': {}
            }
        
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'type': interaction_type,
            'content': content,
            'topic': topic
        }
        
        self.memory[student_id]['interactions'].append(interaction)
        
        if topic:
            if topic not in self.memory[student_id]['topics_studied']:
                self.memory[student_id]['topics_studied'][topic] = 0
            self.memory[student_id]['topics_studied'][topic] += 1
        
        self.save_memory()
    
    def get_student_history(self, student_id: str) -> Dict:
        """Get student's learning history"""
        return self.memory.get(student_id, {})
    
    def summarize_text(self, text: str) -> Dict:
        """Enhanced text summarization using improved extractive methods"""
        if not text.strip():
            return {"error": "Please provide text to summarize"}
        
        # Clean and preprocess text
        text = self.clean_text(text)
        
        # Tokenize into sentences
        sentences = sent_tokenize(text)
        if len(sentences) <= 2:
            return {
                "summary": text,
                "key_points": sentences,
                "readability": self.get_readability_score(text),
                "confidence": 1.0
            }
        
        # Enhanced preprocessing
        stop_words = set(stopwords.words('english'))
        
        # Calculate sentence importance using multiple factors
        sentence_scores = {}
        word_freq = Counter()
        
        # Build word frequency from all sentences
        for sentence in sentences:
            words = word_tokenize(sentence.lower())
            words = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 2]
            for word in words:
                word_freq[word] += 1
        
        # Score sentences using multiple criteria
        for i, sentence in enumerate(sentences):
            words = word_tokenize(sentence.lower())
            words = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 2]
            
            if len(words) == 0:
                sentence_scores[i] = 0
                continue
            
            # Frequency score
            freq_score = sum(word_freq.get(word, 0) for word in words) / len(words)
            
            # Position score (first and last sentences are often important)
            position_score = 0.5
            if i == 0 or i == len(sentences) - 1:
                position_score = 1.0
            elif i < len(sentences) * 0.3:  # First third
                position_score = 0.8
            
            # Length score (moderate length sentences preferred)
            length_score = 1.0
            if len(words) < 5:
                length_score = 0.5
            elif len(words) > 30:
                length_score = 0.7
            
            # Keyword density score
            keyword_score = self.calculate_keyword_score(sentence, word_freq)
            
            # Combined score with weights
            sentence_scores[i] = (
                freq_score * 0.4 +
                position_score * 0.2 +
                length_score * 0.2 +
                keyword_score * 0.2
            )
        
        # Select top sentences for summary (improved selection)
        num_sentences = max(1, min(4, len(sentences) // 3))
        top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_sentences]
        top_sentences = sorted([item[0] for item in top_sentences])
        
        summary_sentences = [sentences[i] for i in top_sentences]
        summary = ' '.join(summary_sentences)
        
        # Extract enhanced key points
        key_points = self.extract_enhanced_key_points(sentences, sentence_scores)
        
        # Calculate confidence score
        confidence = self.calculate_summary_confidence(sentence_scores, top_sentences)
        
        return {
            "summary": summary,
            "key_points": key_points,
            "readability": self.get_readability_score(text),
            "word_count": len(word_tokenize(text)),
            "sentence_count": len(sentences),
            "confidence": confidence,
            "summary_ratio": round(len(summary) / len(text) * 100, 1)
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize input text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Fix common punctuation issues
        text = re.sub(r'\s+([.!?])', r'\1', text)
        # Ensure proper sentence spacing
        text = re.sub(r'([.!?])\s*', r'\1 ', text)
        return text.strip()
    
    def calculate_keyword_score(self, sentence: str, word_freq: Counter) -> float:
        """Calculate importance based on keyword density"""
        words = word_tokenize(sentence.lower())
        stop_words = set(stopwords.words('english'))
        words = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 2]
        
        if not words:
            return 0
        
        # Find top 10 most frequent words as keywords
        top_keywords = set([word for word, freq in word_freq.most_common(10)])
        keyword_count = sum(1 for word in words if word in top_keywords)
        
        return keyword_count / len(words)
    
    def extract_enhanced_key_points(self, sentences: List[str], sentence_scores: Dict) -> List[str]:
        """Extract key points using advanced scoring"""
        # Get sentences with scores above average
        avg_score = sum(sentence_scores.values()) / len(sentence_scores)
        threshold = avg_score * 1.2
        
        key_points = []
        for i, sentence in enumerate(sentences):
            if sentence_scores.get(i, 0) >= threshold:
                # Clean and shorten if necessary
                cleaned = sentence.strip()
                if len(cleaned) > 150:
                    # Try to find a good break point
                    words = cleaned.split()
                    if len(words) > 20:
                        cleaned = ' '.join(words[:20]) + '...'
                key_points.append(cleaned)
        
        # Ensure we have at least 2 key points
        if len(key_points) < 2:
            top_2 = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:2]
            key_points = [sentences[i] for i, _ in top_2]
        
        return key_points[:5]  # Limit to 5 key points
    
    def calculate_summary_confidence(self, sentence_scores: Dict, selected_indices: List) -> float:
        """Calculate confidence score for the summary"""
        if not sentence_scores or not selected_indices:
            return 0.5
        
        selected_scores = [sentence_scores[i] for i in selected_indices]
        all_scores = list(sentence_scores.values())
        
        avg_selected = sum(selected_scores) / len(selected_scores)
        avg_all = sum(all_scores) / len(all_scores)
        
        # Confidence based on how much better selected sentences are
        confidence = min(1.0, avg_selected / (avg_all + 0.1))
        return round(confidence, 2)
    
    def explain_topic(self, topic: str, difficulty_level: str = "simple") -> Dict:
        """Enhanced topic explanation with more comprehensive content"""
        explanations = {
            "photosynthesis": {
                "simple": "Photosynthesis is how plants make their own food using sunlight, water, and air. Plants use their green leaves to catch sunlight and turn it into energy, just like how solar panels work! The plants breathe in carbon dioxide from the air and drink water from their roots. When sunlight hits the green parts of leaves, it helps mix these ingredients together to make sugar (food for the plant). As a bonus, plants release oxygen into the air - the same oxygen we need to breathe!",
                "intermediate": "Photosynthesis is the process where plants convert carbon dioxide and water into glucose using chlorophyll and sunlight. This process occurs mainly in the leaves and releases oxygen as a byproduct. The green chemical chlorophyll captures light energy, which powers the chemical reactions that combine CO2 and H2O to create glucose (C6H12O6). This glucose serves as food for the plant and forms the base of most food chains on Earth.",
                "advanced": "Photosynthesis consists of two main stages: light-dependent reactions (photo phase) occurring in thylakoids and light-independent reactions (Calvin cycle) in the chloroplast stroma. Chlorophyll absorbs photons, exciting electrons that drive ATP and NADPH production through the electron transport chain. These energy carriers power the Calvin cycle, where CO2 is fixed into organic molecules through the enzyme RuBisCO. The overall equation: 6CO2 + 6H2O + light energy → C6H12O6 + 6O2."
            },
            "gravity": {
                "simple": "Gravity is the invisible force that pulls things toward the Earth. It's why when you drop a ball, it falls down instead of floating away! Everything with weight gets pulled by gravity - that's why we stay on the ground instead of floating around like astronauts in space. The bigger and heavier something is, the stronger its gravity pull. Earth is very big and heavy, so it has strong gravity that keeps everything on its surface.",
                "intermediate": "Gravity is a fundamental force that attracts objects with mass toward each other. The more massive an object, the stronger its gravitational pull. Earth's gravity (9.8 m/s²) keeps us grounded and pulls all objects toward the planet's center. This same force keeps the Moon orbiting Earth and Earth orbiting the Sun. Gravity's strength decreases with distance - that's why astronauts experience weightlessness in space, far from Earth's gravitational influence.",
                "advanced": "Gravity is described by Einstein's General Theory of Relativity as the curvature of spacetime caused by mass and energy. Massive objects warp the fabric of spacetime, creating what we experience as gravitational attraction. Newton's law of universal gravitation (F = G(m1×m2)/r²) provides accurate calculations for most scenarios, while Einstein's field equations describe extreme cases like black holes and gravitational waves."
            },
            "democracy": {
                "simple": "Democracy is when people get to vote and choose their leaders, like choosing a class president at school! In a democracy, everyone's opinion matters and everyone gets a fair say in making important decisions. People vote for the person they think will do the best job leading them. The person who gets the most votes becomes the leader. It's like a big, fair game where everyone gets to participate and the majority decides what happens.",
                "intermediate": "Democracy is a system of government where citizens exercise power through voting and elected representatives. Key principles include majority rule (decisions made by more than half the people), protection of minority rights, individual freedoms, and regular elections. Democratic governments have checks and balances to prevent any one person or group from having too much power. Examples include parliamentary and presidential systems.",
                "advanced": "Democracy encompasses various forms including direct democracy (citizens vote on issues directly), representative democracy (elected officials make decisions), and deliberative democracy (emphasis on discussion and debate). It requires robust institutions: independent judiciary, free press, civil society, and constitutional protections for civil liberties. Modern democracies face challenges like political polarization, disinformation, and balancing majority rule with minority rights."
            },
            "evolution": {
                "simple": "Evolution is how living things slowly change over a very long time. Just like how you grow and change as you get older, all living things - plants, animals, and even tiny germs - change over many, many years. The animals and plants that are best at surviving and having babies pass on their good traits to their children. Over millions of years, these small changes add up to make completely new types of animals and plants!",
                "intermediate": "Evolution is the process by which species change over time through natural selection. Organisms with traits that help them survive and reproduce are more likely to pass these beneficial traits to their offspring. Over many generations, these advantageous traits become more common in the population. This process explains the diversity of life on Earth and how all living things are related through common ancestors.",
                "advanced": "Evolution operates through several mechanisms: natural selection, genetic drift, gene flow, and mutation. Darwin's theory explains how heritable variations that improve survival and reproductive success become more frequent in populations over time. Modern synthesis incorporates genetics, showing how DNA mutations provide the raw material for evolution, while population genetics quantifies evolutionary change using mathematical models."
            },
            "climate change": {
                "simple": "Climate change means the weather on Earth is changing in ways that can be harmful. It's getting warmer because of pollution, especially from cars and factories that put bad gases into the air. These gases trap heat from the sun, making Earth warmer - like being under a thick blanket. This causes problems like melting ice, changing weather patterns, and making it hard for some animals and plants to live in their homes.",
                "intermediate": "Climate change refers to long-term shifts in global weather patterns, primarily caused by human activities that increase greenhouse gas concentrations in the atmosphere. Burning fossil fuels releases CO2, which traps heat and raises global temperatures. This leads to melting ice caps, rising sea levels, extreme weather events, and disruptions to ecosystems and agriculture. Scientists measure these changes and predict future impacts using climate models.",
                "advanced": "Climate change involves complex feedback loops in Earth's climate system. Anthropogenic greenhouse gas emissions (primarily CO2, CH4, N2O) enhance the natural greenhouse effect, causing radiative forcing and global warming. Positive feedbacks (ice-albedo, water vapor) amplify warming, while negative feedbacks provide some stability. Climate sensitivity, tipping points, and regional variations make prediction challenging, requiring sophisticated coupled atmosphere-ocean-land models."
            }
        }
        
        topic_lower = topic.lower()
        explanation_text = ""
        
        if topic_lower in explanations:
            explanation_text = explanations[topic_lower].get(difficulty_level, explanations[topic_lower]["simple"])
        else:
            # Enhanced generic explanations using AI-like reasoning
            explanation_text = self.generate_generic_explanation(topic, difficulty_level)
        
        return {
            "topic": topic,
            "difficulty_level": difficulty_level,
            "explanation": explanation_text,
            "suggested_activities": self.get_suggested_activities(topic),
            "related_topics": self.get_related_topics(topic),
            "estimated_reading_time": self.estimate_reading_time(explanation_text),
            "key_concepts": self.extract_key_concepts(explanation_text)
        }
    
    def generate_generic_explanation(self, topic: str, difficulty_level: str) -> str:
        """Generate explanations for topics not in the database"""
        if difficulty_level == "simple":
            return f"{topic} is an important concept that we can understand by breaking it down into simple parts. It involves basic principles that affect our daily lives. Think of it like building blocks - each part works together to create the bigger picture. Learning about {topic} helps us understand how the world around us works and why certain things happen the way they do."
        elif difficulty_level == "intermediate":
            return f"{topic} is a significant concept that builds upon fundamental principles and involves understanding the relationships between different components. It has practical applications in various fields and demonstrates important cause-and-effect relationships. Understanding {topic} requires analyzing how different factors interact and influence outcomes, making it relevant to real-world situations and decision-making processes."
        else:
            return f"{topic} represents a complex subject that encompasses advanced principles, theoretical frameworks, and intricate relationships with other concepts in the field. It involves sophisticated analysis, critical thinking, and often requires understanding of underlying mathematical, scientific, or logical foundations. Mastery of {topic} typically involves synthesis of multiple concepts and application to novel situations."
    
    def estimate_reading_time(self, text: str) -> str:
        """Estimate reading time for explanation text"""
        words = len(text.split())
        # Average reading speed: 200-250 words per minute
        minutes = max(1, round(words / 225))
        if minutes == 1:
            return "1 minute"
        return f"{minutes} minutes"
    
    def extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts from explanation text"""
        # Simple keyword extraction based on word frequency and importance
        stop_words = set(stopwords.words('english'))
        words = word_tokenize(text.lower())
        words = [word for word in words if word.isalnum() and word not in stop_words and len(word) > 3]
        
        word_freq = Counter(words)
        # Get top concepts (words that appear multiple times or are important)
        key_concepts = [word.title() for word, freq in word_freq.most_common(5) if freq > 1]
        
        return key_concepts[:4]  # Limit to 4 key concepts
    
    def get_suggested_activities(self, topic: str) -> List[str]:
        """Enhanced suggested learning activities for topics"""
        activities = {
            "photosynthesis": [
                "🌱 Grow plants in different light conditions and observe differences",
                "🔬 Create a simple experiment with aquatic plants producing oxygen bubbles",
                "🎨 Draw and label a detailed diagram of photosynthesis process",
                "📱 Use a light meter app to measure light intensity in different locations",
                "🍃 Collect different types of leaves and examine their green chlorophyll"
            ],
            "gravity": [
                "🏀 Drop different objects from the same height and time their fall",
                "⚖️ Build a simple pendulum and observe its motion patterns",
                "🌍 Research how gravity affects different planets and their moons",
                "🚀 Watch videos of astronauts in zero gravity and compare to Earth",
                "📐 Calculate the gravitational force between different objects"
            ],
            "democracy": [
                "🗳️ Organize a class election with proper voting procedures",
                "📊 Research and compare different voting systems worldwide",
                "🏛️ Visit local government buildings or attend town hall meetings",
                "📰 Follow a current political issue and track different viewpoints",
                "🎭 Role-play different government systems and their decision-making"
            ],
            "evolution": [
                "🦴 Examine fossil records and create an evolutionary timeline",
                "🔬 Observe fruit flies or bacteria to see rapid generation changes",
                "🌳 Create a family tree showing how species might be related",
                "🧬 Learn about DNA and how mutations provide variation",
                "🐦 Study Darwin's finches and their beak adaptations"
            ],
            "climate change": [
                "🌡️ Track local temperature and weather patterns over time",
                "📊 Analyze global climate data and create graphs",
                "♻️ Calculate your carbon footprint and find reduction strategies",
                "🌊 Research sea level changes and their impact on coastal areas",
                "🌿 Plant trees or start a school garden to offset carbon"
            ]
        }
        
        topic_lower = topic.lower()
        if topic_lower in activities:
            return activities[topic_lower]
        
        # Generate generic activities based on topic type
        return [
            f"📚 Research {topic} using reliable online sources and libraries",
            f"💭 Create a mind map showing connections within {topic}",
            f"📝 Write a summary in your own words about {topic}",
            f"🎥 Watch educational videos or documentaries about {topic}",
            f"👥 Discuss {topic} with classmates, teachers, or experts",
            f"🧪 Look for hands-on experiments or activities related to {topic}"
        ]
    
    def get_related_topics(self, topic: str) -> List[str]:
        """Enhanced related topics with more comprehensive connections"""
        related = {
            "photosynthesis": [
                "Cellular Respiration", "Chlorophyll", "Plant Biology", "Ecosystems", 
                "Carbon Cycle", "Food Chains", "Solar Energy", "Biochemistry"
            ],
            "gravity": [
                "Physics", "Newton's Laws", "Motion", "Astronomy", "Space Exploration",
                "Planetary Science", "Einstein's Relativity", "Force and Energy"
            ],
            "democracy": [
                "Government Systems", "Voting Rights", "Civil Rights", "Political Science",
                "Constitution", "Elections", "Citizenship", "Rule of Law"
            ],
            "evolution": [
                "Natural Selection", "Genetics", "Adaptation", "Species", "DNA",
                "Fossils", "Biodiversity", "Charles Darwin", "Molecular Biology"
            ],
            "climate change": [
                "Global Warming", "Greenhouse Effect", "Renewable Energy", "Weather Patterns",
                "Ocean Currents", "Biodiversity Loss", "Sustainability", "Carbon Footprint"
            ]
        }
        return related.get(topic.lower(), [
            "Scientific Method", "Research Skills", "Critical Thinking", "Data Analysis"
        ])
    
    def generate_quiz(self, topic: str, num_questions: int = 5) -> Dict:
        """Enhanced quiz generation with improved question quality"""
        quiz_bank = {
            "photosynthesis": [
                {
                    "question": "What are the main ingredients plants need for photosynthesis?",
                    "options": ["Sunlight, water, carbon dioxide", "Only water and soil", "Only sunlight and air", "Soil, fertilizer, and water"],
                    "correct": 0,
                    "explanation": "Plants need three main ingredients: sunlight for energy, water from their roots, and carbon dioxide from the air to make glucose.",
                    "difficulty": "easy"
                },
                {
                    "question": "What gas do plants release during photosynthesis?",
                    "options": ["Carbon dioxide", "Nitrogen", "Oxygen", "Hydrogen"],
                    "correct": 2,
                    "explanation": "Plants release oxygen (O2) as a beneficial byproduct of photosynthesis, which is essential for most life on Earth.",
                    "difficulty": "easy"
                },
                {
                    "question": "Where in the plant cell does photosynthesis mainly occur?",
                    "options": ["Nucleus", "Mitochondria", "Chloroplasts", "Cell wall"],
                    "correct": 2,
                    "explanation": "Photosynthesis occurs in chloroplasts, which contain chlorophyll that captures light energy.",
                    "difficulty": "medium"
                },
                {
                    "question": "What is the chemical equation for photosynthesis?",
                    "options": ["6CO2 + 6H2O + energy → C6H12O6 + 6O2", "CO2 + H2O → glucose", "O2 + H2O → CO2 + glucose", "C6H12O6 → CO2 + H2O"],
                    "correct": 0,
                    "explanation": "The balanced equation shows 6 molecules of CO2 plus 6 molecules of water plus light energy produce glucose and 6 molecules of oxygen.",
                    "difficulty": "hard"
                },
                {
                    "question": "What role does chlorophyll play in photosynthesis?",
                    "options": ["Stores water", "Captures light energy", "Produces oxygen", "Creates carbon dioxide"],
                    "correct": 1,
                    "explanation": "Chlorophyll is the green pigment that absorbs light energy, which powers the photosynthesis process.",
                    "difficulty": "medium"
                }
            ],
            "gravity": [
                {
                    "question": "What happens when you drop an object on Earth?",
                    "options": ["It floats in the air", "It falls toward the ground", "It moves sideways", "It disappears"],
                    "correct": 1,
                    "explanation": "Gravity pulls objects toward Earth's center, making them fall downward when dropped.",
                    "difficulty": "easy"
                },
                {
                    "question": "Which celestial body has stronger gravity?",
                    "options": ["Moon", "Earth", "They're exactly the same", "It depends on the weather"],
                    "correct": 1,
                    "explanation": "Earth has much stronger gravity than the Moon because Earth has much more mass (about 81 times more massive).",
                    "difficulty": "easy"
                },
                {
                    "question": "What is Earth's approximate gravitational acceleration?",
                    "options": ["5.8 m/s²", "9.8 m/s²", "15.2 m/s²", "20.1 m/s²"],
                    "correct": 1,
                    "explanation": "Earth's gravitational acceleration is approximately 9.8 meters per second squared (9.8 m/s²).",
                    "difficulty": "medium"
                },
                {
                    "question": "According to Einstein's theory, what causes gravity?",
                    "options": ["Magnetic fields", "Curved spacetime", "Electric charges", "Air pressure"],
                    "correct": 1,
                    "explanation": "Einstein's General Relativity explains gravity as the curvature of spacetime caused by mass and energy.",
                    "difficulty": "hard"
                },
                {
                    "question": "How does distance affect gravitational force?",
                    "options": ["Force increases with distance", "Force decreases with distance squared", "Distance doesn't matter", "Force only depends on mass"],
                    "correct": 1,
                    "explanation": "Gravitational force decreases with the square of the distance between objects (inverse square law).",
                    "difficulty": "medium"
                }
            ],
            "democracy": [
                {
                    "question": "In a democracy, who has the power to choose leaders?",
                    "options": ["The king or queen", "The citizens through voting", "The military", "Only wealthy people"],
                    "correct": 1,
                    "explanation": "In a democracy, all eligible citizens have the right to vote and choose their representatives and leaders.",
                    "difficulty": "easy"
                },
                {
                    "question": "What is the main purpose of voting in a democracy?",
                    "options": ["To make money", "To choose leaders and make decisions", "To have fun", "To create problems"],
                    "correct": 1,
                    "explanation": "Voting allows citizens to participate in government by choosing leaders and sometimes deciding on important issues directly.",
                    "difficulty": "easy"
                },
                {
                    "question": "What principle protects the rights of people who didn't win an election?",
                    "options": ["Majority rule only", "Minority rights protection", "Winner takes all", "Popular vote"],
                    "correct": 1,
                    "explanation": "Democratic systems protect minority rights to ensure that losing groups still have fundamental freedoms and representation.",
                    "difficulty": "medium"
                },
                {
                    "question": "What is the difference between direct and representative democracy?",
                    "options": ["No difference", "Direct means citizens vote on issues; representative means elected officials decide", "Direct is only for small countries", "Representative is older"],
                    "correct": 1,
                    "explanation": "Direct democracy has citizens vote directly on issues, while representative democracy has elected officials make decisions on behalf of citizens.",
                    "difficulty": "medium"
                },
                {
                    "question": "What are 'checks and balances' in a democratic system?",
                    "options": ["Banking regulations", "Ways to prevent any one branch of government from becoming too powerful", "Voting procedures", "Economic policies"],
                    "correct": 1,
                    "explanation": "Checks and balances ensure that different branches of government (executive, legislative, judicial) can limit each other's power.",
                    "difficulty": "hard"
                }
            ],
            "evolution": [
                {
                    "question": "What is natural selection?",
                    "options": ["Animals choosing their habitat", "Survival and reproduction of organisms with helpful traits", "Humans selecting pets", "Plants growing toward light"],
                    "correct": 1,
                    "explanation": "Natural selection is the process where organisms with traits that help survival and reproduction become more common over time.",
                    "difficulty": "medium"
                },
                {
                    "question": "Who developed the theory of evolution by natural selection?",
                    "options": ["Albert Einstein", "Charles Darwin", "Isaac Newton", "Gregor Mendel"],
                    "correct": 1,
                    "explanation": "Charles Darwin developed the theory of evolution by natural selection, published in 'On the Origin of Species' in 1859.",
                    "difficulty": "easy"
                },
                {
                    "question": "What provides the variation that evolution acts upon?",
                    "options": ["Environmental changes", "Genetic mutations", "Learning", "Diet"],
                    "correct": 1,
                    "explanation": "Genetic mutations create the variation in traits that natural selection can then act upon over generations.",
                    "difficulty": "medium"
                }
            ],
            "climate change": [
                {
                    "question": "What is the main cause of current climate change?",
                    "options": ["Natural weather cycles", "Human activities releasing greenhouse gases", "Solar activity", "Volcanic eruptions"],
                    "correct": 1,
                    "explanation": "Scientific evidence shows that current climate change is primarily caused by human activities that increase greenhouse gas concentrations.",
                    "difficulty": "medium"
                },
                {
                    "question": "Which gas is the most significant contributor to human-caused climate change?",
                    "options": ["Oxygen", "Carbon dioxide", "Nitrogen", "Helium"],
                    "correct": 1,
                    "explanation": "Carbon dioxide (CO2) from burning fossil fuels is the largest single contributor to human-caused climate change.",
                    "difficulty": "easy"
                },
                {
                    "question": "What is the greenhouse effect?",
                    "options": ["Growing plants in greenhouses", "Gases in the atmosphere trapping heat", "Green energy production", "Plant photosynthesis"],
                    "correct": 1,
                    "explanation": "The greenhouse effect occurs when certain gases in the atmosphere trap heat from the sun, warming the planet.",
                    "difficulty": "medium"
                }
            ]
        }
        
        topic_lower = topic.lower()
        if topic_lower not in quiz_bank:
            # Generate adaptive questions for unknown topics
            questions = self.generate_adaptive_questions(topic, num_questions)
        else:
            questions = quiz_bank[topic_lower]
        
        # Intelligent question selection based on difficulty progression
        selected_questions = self.select_optimal_questions(questions, num_questions)
        
        quiz_id = str(uuid.uuid4())
        
        return {
            "quiz_id": quiz_id,
            "topic": topic,
            "questions": selected_questions,
            "total_questions": len(selected_questions),
            "estimated_time": f"{len(selected_questions) * 2} minutes",
            "difficulty_distribution": self.analyze_difficulty_distribution(selected_questions)
        }
    
    def generate_adaptive_questions(self, topic: str, num_questions: int) -> List[Dict]:
        """Generate questions for topics not in database"""
        base_questions = [
            {
                "question": f"What is the main concept behind {topic}?",
                "options": [f"Understanding {topic} fundamentals", "Memorizing facts", "Ignoring details", "Random guessing"],
                "correct": 0,
                "explanation": f"Understanding the fundamental concepts of {topic} is key to mastering the subject.",
                "difficulty": "easy"
            },
            {
                "question": f"Why is {topic} important to study?",
                "options": ["It has no practical use", f"It helps us understand important principles", "It's only for experts", "It's too difficult to learn"],
                "correct": 1,
                "explanation": f"Studying {topic} helps develop understanding of important principles that apply to many situations.",
                "difficulty": "easy"
            },
            {
                "question": f"What field of study does {topic} primarily belong to?",
                "options": ["General knowledge", "Academic discipline", "Entertainment", "Sports"],
                "correct": 1,
                "explanation": f"{topic} is part of academic study that builds knowledge and understanding.",
                "difficulty": "medium"
            }
        ]
        return base_questions[:num_questions]
    
    def select_optimal_questions(self, questions: List[Dict], num_questions: int) -> List[Dict]:
        """Select questions with optimal difficulty progression"""
        if len(questions) <= num_questions:
            return questions
        
        # Sort by difficulty
        difficulty_order = {"easy": 1, "medium": 2, "hard": 3}
        sorted_questions = sorted(questions, key=lambda q: difficulty_order.get(q.get("difficulty", "medium"), 2))
        
        # Select with balanced difficulty
        selected = []
        easy_count = max(1, num_questions // 3)
        medium_count = max(1, num_questions // 3)
        hard_count = num_questions - easy_count - medium_count
        
        easy_questions = [q for q in sorted_questions if q.get("difficulty") == "easy"]
        medium_questions = [q for q in sorted_questions if q.get("difficulty") == "medium"]
        hard_questions = [q for q in sorted_questions if q.get("difficulty") == "hard"]
        
        import random
        selected.extend(random.sample(easy_questions, min(easy_count, len(easy_questions))))
        selected.extend(random.sample(medium_questions, min(medium_count, len(medium_questions))))
        selected.extend(random.sample(hard_questions, min(hard_count, len(hard_questions))))
        
        # Fill remaining spots if needed
        while len(selected) < num_questions and len(selected) < len(questions):
            remaining = [q for q in questions if q not in selected]
            if remaining:
                selected.append(random.choice(remaining))
        
        # Shuffle final order
        random.shuffle(selected)
        return selected[:num_questions]
    
    def analyze_difficulty_distribution(self, questions: List[Dict]) -> Dict:
        """Analyze the difficulty distribution of selected questions"""
        distribution = {"easy": 0, "medium": 0, "hard": 0}
        for question in questions:
            difficulty = question.get("difficulty", "medium")
            distribution[difficulty] += 1
        return distribution
    
    def check_quiz_answer(self, question_index: int, selected_answer: int, correct_answer: int) -> Dict:
        """Check if quiz answer is correct"""
        is_correct = selected_answer == correct_answer
        return {
            "is_correct": is_correct,
            "selected": selected_answer,
            "correct": correct_answer
        }
    
    def get_readability_score(self, text: str) -> Dict:
        """Calculate readability scores for text"""
        try:
            flesch_reading_ease = textstat.flesch_reading_ease(text)
            flesch_kincaid_grade = textstat.flesch_kincaid_grade(text)
            
            # Determine reading level
            if flesch_reading_ease >= 90:
                level = "Very Easy"
            elif flesch_reading_ease >= 80:
                level = "Easy"
            elif flesch_reading_ease >= 70:
                level = "Fairly Easy"
            elif flesch_reading_ease >= 60:
                level = "Standard"
            elif flesch_reading_ease >= 50:
                level = "Fairly Difficult"
            elif flesch_reading_ease >= 30:
                level = "Difficult"
            else:
                level = "Very Difficult"
            
            return {
                "flesch_reading_ease": round(flesch_reading_ease, 1),
                "flesch_kincaid_grade": round(flesch_kincaid_grade, 1),
                "reading_level": level
            }
        except:
            return {
                "flesch_reading_ease": 0,
                "flesch_kincaid_grade": 0,
                "reading_level": "Unknown"
            }

# Initialize the study assistant
study_assistant = StudyAssistant()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    text = data.get('text', '')
    
    if not text:
        return jsonify({"error": "Please provide text to summarize"}), 400
    
    student_id = study_assistant.get_student_id(session.get('session_id', ''))
    result = study_assistant.summarize_text(text)
    
    # Add to memory
    study_assistant.add_to_memory(
        student_id, 
        'summarization', 
        f"Summarized text: {text[:100]}...",
        'text_summarization'
    )
    
    return jsonify(result)

@app.route('/explain', methods=['POST'])
def explain():
    data = request.get_json()
    topic = data.get('topic', '')
    difficulty = data.get('difficulty', 'simple')
    
    if not topic:
        return jsonify({"error": "Please provide a topic to explain"}), 400
    
    student_id = study_assistant.get_student_id(session.get('session_id', ''))
    result = study_assistant.explain_topic(topic, difficulty)
    
    # Add to memory
    study_assistant.add_to_memory(
        student_id,
        'explanation',
        f"Explained {topic} at {difficulty} level",
        topic
    )
    
    return jsonify(result)

@app.route('/quiz', methods=['POST'])
def generate_quiz():
    data = request.get_json()
    topic = data.get('topic', '')
    num_questions = data.get('num_questions', 5)
    
    if not topic:
        return jsonify({"error": "Please provide a topic for the quiz"}), 400
    
    student_id = study_assistant.get_student_id(session.get('session_id', ''))
    result = study_assistant.generate_quiz(topic, num_questions)
    
    # Add to memory
    study_assistant.add_to_memory(
        student_id,
        'quiz_generation',
        f"Generated quiz for {topic} with {num_questions} questions",
        topic
    )
    
    return jsonify(result)

@app.route('/check_answer', methods=['POST'])
def check_answer():
    data = request.get_json()
    question_index = data.get('question_index', 0)
    selected_answer = data.get('selected_answer', 0)
    correct_answer = data.get('correct_answer', 0)
    topic = data.get('topic', '')
    
    student_id = study_assistant.get_student_id(session.get('session_id', ''))
    result = study_assistant.check_quiz_answer(question_index, selected_answer, correct_answer)
    
    # Add to memory
    study_assistant.add_to_memory(
        student_id,
        'quiz_answer',
        f"Answered question {question_index}: {'correct' if result['is_correct'] else 'incorrect'}",
        topic
    )
    
    # Update quiz performance in memory
    if student_id in study_assistant.memory:
        if topic not in study_assistant.memory[student_id]['quiz_performance']:
            study_assistant.memory[student_id]['quiz_performance'][topic] = {'correct': 0, 'total': 0}
        
        study_assistant.memory[student_id]['quiz_performance'][topic]['total'] += 1
        if result['is_correct']:
            study_assistant.memory[student_id]['quiz_performance'][topic]['correct'] += 1
        
        study_assistant.save_memory()
    
    return jsonify(result)

@app.route('/memory')
def get_memory():
    student_id = study_assistant.get_student_id(session.get('session_id', ''))
    history = study_assistant.get_student_history(student_id)
    
    # Format the response for better presentation
    formatted_history = {
        'total_interactions': len(history.get('interactions', [])),
        'topics_studied': history.get('topics_studied', {}),
        'quiz_performance': history.get('quiz_performance', {}),
        'recent_interactions': history.get('interactions', [])[-10:]  # Last 10 interactions
    }
    
    return jsonify(formatted_history)

@app.route('/recommendations')
def get_recommendations():
    student_id = study_assistant.get_student_id(session.get('session_id', ''))
    history = study_assistant.get_student_history(student_id)
    
    recommendations = []
    
    # Analyze quiz performance
    quiz_performance = history.get('quiz_performance', {})
    for topic, performance in quiz_performance.items():
        accuracy = performance['correct'] / performance['total'] if performance['total'] > 0 else 0
        if accuracy < 0.7:  # Less than 70% accuracy
            recommendations.append(f"Consider reviewing {topic} - current accuracy: {accuracy:.1%}")
    
    # Suggest new topics based on studied topics
    topics_studied = history.get('topics_studied', {})
    if 'photosynthesis' in topics_studied and 'cellular respiration' not in topics_studied:
        recommendations.append("Since you studied photosynthesis, you might enjoy learning about cellular respiration!")
    
    if 'gravity' in topics_studied and 'motion' not in topics_studied:
        recommendations.append("You've studied gravity - motion and Newton's laws would be great next topics!")
    
    if not recommendations:
        recommendations.append("Keep up the great work! Try exploring new topics or taking more quizzes.")
    
    return jsonify({'recommendations': recommendations})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
