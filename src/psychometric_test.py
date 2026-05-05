def get_psychometric_questions():
    """Define the psychometric test questions"""
    questions = [
        # Anxiety (4 questions)
        ("I feel nervous or anxious frequently", "anxiety"),
        ("I worry too much about different things", "anxiety"),
        ("I find it hard to relax", "anxiety"),
        ("I feel restless or on edge", "anxiety"),
        # Depression (4 questions)
        ("I feel sad or down most of the time", "depression"),
        ("I have lost interest in activities I used to enjoy", "depression"),
        ("I feel hopeless about the future", "depression"),
        ("I feel worthless or guilty", "depression"),
        # Stress (4 questions)
        ("I feel overwhelmed by responsibilities", "stress"),
        ("I find it hard to concentrate", "stress"),
        ("I get irritated easily", "stress"),
        ("I feel mentally exhausted", "stress"),
        # Sleep & General (4 questions)
        ("I have trouble sleeping", "general"),
        ("I wake up feeling tired", "general"),
        ("I feel low on energy throughout the day", "general"),
        ("I avoid social interactions", "general")
    ]
    return questions

def interpret_score(score, max_per_category=20):
    """Interpret category score"""
    if score <= 8:
        return "Low"
    elif score <= 12:
        return "Mild"
    elif score <= 16:
        return "Moderate"
    else:
        return "High"

def calculate_psychometric_results(scores):
    """Calculate and display psychometric results"""
    results = {}
    print("\n" + "="*60)
    print("PSYCHOMETRIC ANALYSIS RESULT")
    print("="*60)
    
    for category, score in scores.items():
        level = interpret_score(score)
        results[category] = level
        print(f"{category.capitalize():<12} -> Score: {score:<2} | Level: {level}")
    
    total_score = sum(scores.values())
    
    if total_score < 40:
        overall = "Normal"
    elif total_score < 55:
        overall = "Mild"
    elif total_score < 70:
        overall = "Moderate"
    else:
        overall = "Severe"
    
    print(f"\nTotal Score: {total_score}/80")
    print(f"Overall Mental Health Status: {overall}")
    
    return overall, results, total_score

def conduct_psychometric_test(questions=None, interactive=True, preset_answers=None):
    """
    Conduct the psychometric test
    If interactive=False and preset_answers provided, use those answers
    """
    if questions is None:
        questions = get_psychometric_questions()
    
    scores = {
        "anxiety": 0,
        "depression": 0,
        "stress": 0,
        "general": 0
    }
    
    if interactive:
        print("\n" + "="*60)
        print("MENTAL HEALTH SELF-ASSESSMENT")
        print("="*60)
        print("Please rate each statement:")
        print("1 = Never | 2 = Rarely | 3 = Sometimes | 4 = Often | 5 = Always\n")
        
        for i, (q, category) in enumerate(questions, 1):
            while True:
                try:
                    ans = int(input(f"{i}. {q}: "))
                    if 1 <= ans <= 5:
                        scores[category] += ans
                        break
                    else:
                        print("Enter a number between 1-5")
                except ValueError:
                    print("Invalid input, try again")
    else:
        # Use preset answers
        for i, (q, category) in enumerate(questions):
            if preset_answers and i < len(preset_answers):
                scores[category] += preset_answers[i]
    
    overall, results, total_score = calculate_psychometric_results(scores)
    
    return scores, overall, results, total_score