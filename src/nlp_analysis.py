from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import nltk

# Download required NLTK data
nltk.download('vader_lexicon', quiet=True)

class NLPAnalyzer:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()
    
    def analyze_text(self, text):
        """Core analysis logic for text processing"""
        vader_scores = self.vader_analyzer.polarity_scores(text)
        blob = TextBlob(text)
        
        return {
            "compound": vader_scores['compound'],
            "subjectivity": blob.sentiment.subjectivity,
            "polarity": blob.sentiment.polarity
        }
    
    def get_sentiment_tone(self, compound_score):
        """Convert compound score to tone description"""
        if compound_score >= 0.5:
            return "Highly Positive / Resilient"
        elif compound_score >= 0.05:
            return "Stable / Positive"
        elif compound_score <= -0.5:
            return "High Emotional Distress"
        elif compound_score <= -0.05:
            return "Struggling / Negative"
        else:
            return "Neutral / Flat"
    
    def conduct_nlp_assessment(self, responses=None, interactive=True):
        """
        Conduct NLP assessment
        If interactive=False, use provided responses
        """
        questions = [
            {"q": "Can you describe how you've been feeling over the past 2 weeks?", "cat": "Mood"},
            {"q": "What thoughts or worries keep running through your mind lately?", "cat": "Cognition"},
            {"q": "How has your sleep and energy level been throughout the day?", "cat": "Physical"},
            {"q": "How are you managing your daily responsibilities and stress?", "cat": "Coping"},
            {"q": "When you look at your future, what do you see or feel?", "cat": "Outlook"}
        ]
        
        if interactive:
            print("\n" + "="*70)
            print("INTERACTIVE NLP EMOTIONAL ASSESSMENT")
            print("="*70)
            print("Please share your thoughts openly. More detail helps the AI understand better.\n")
            
            responses = []
            for i, item in enumerate(questions, 1):
                print(f"[{item['cat']}] Question {i}: {item['q']}")
                response = input("Your answer: ").strip()
                
                # Validate response length
                while len(response) < 15:
                    print("The AI needs a bit more detail to analyze effectively (at least 15 characters)")
                    response = input("Your answer: ").strip()
                
                responses.append(response)
                print("✓ Recorded. Thank you.\n")
        else:
            if responses is None:
                raise ValueError("Must provide responses when interactive=False")
        
        # Combine all responses
        combined_text = " ".join(responses)
        final_analysis = self.analyze_text(combined_text)
        
        score = final_analysis['compound']
        tone = self.get_sentiment_tone(score)
        
        print("\n" + "="*70)
        print("NLP SENTIMENT RESULTS")
        print("="*70)
        print(f"Aggregated Sentiment Score: {score:.2f} (-1 to +1)")
        print(f"Subjectivity (Personal): {final_analysis['subjectivity']*100:.1f}%")
        print(f"Overall Emotional Tone: {tone}")
        print("="*70)
        
        return score, tone, responses