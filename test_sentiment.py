from services.sentiment_service import analyze_sentiment

reviews = [
    "This app is excellent, very fast and reliable",
    "Worst app ever, full of bugs and crashes",
    "Average experience, nothing special",
    "Amazing app, best I have ever used, highly recommend",
    "Terrible performance, waste of time and money",
    "This app is good",
    "Scam app, do not download, very dangerous",
    "Okay app, works sometimes",
    "Great app love it so much perfect",
    "Bad bad bad app horrible experience",
    # Suspicious / fake-style reviews
    "Perfect perfect perfect best best best amazing",
    "Horrible horrible horrible worst worst scam fraud",
    "Excellent excellent excellent wonderful brilliant superb",
    "Awful terrible disgusting horrible worst ever seen",
    "The app crashes sometimes and loading is slow. Needs improvement."
]

print("-" * 85)
print(f"{'Review':<45} {'Label':<12} {'Score':<8} {'FakeProb':<10} Result")
print("-" * 85)

for r in reviews:
    label, score, fake_prob = analyze_sentiment(r)
    flag = "<<< FAKE" if fake_prob >= 0.65 else "Genuine"
    print(f"{r[:45]:<45} {label:<12} {str(score):<8} {str(fake_prob):<10} {flag}")

print("-" * 85)
print("\nThreshold: fake_probability >= 0.65 = FAKE, else Genuine")
print("Score > 0.05 = Positive | Score < -0.05 = Negative | else Neutral")
