# NaanStop Tiffin: Decision Tree Surplus Food Matcher

## T_TOPIC
**Core concept**: Using a Decision Tree algorithm to instantly match surplus prepared food with nearby customers who want it, offering them a flash sale discount to eliminate food waste.
**Historical context**: Decision Trees are classical Machine Learning algorithms heavily used in medical diagnostics (like the IBM Machine Learning drug classification lab) because of their interpretable nature.
**Current applications**: 
1. Medical diagnosis (classifying patient features to prescribe specific drugs).
2. Tiffin services (NaanStop Tiffin) matching food supply to demand dynamically.
**Implementation strategies**:
- *Smart implementation*: Using scikit-learn's `DecisionTreeClassifier` with `max_depth` and `min_samples_leaf` to prevent overfitting the local customer base.
**Credits**: IBM Machine Learning with Python Course (drug200.csv dataset).

## E_EXPERIENCE
**Personal learning**: Learned how to visualize the shift from Entropy (randomness/chaos) to pure leaves (certainty) using Information Gain at every split. Also learned that 100% training accuracy is usually a sign of overfitting, not success.
**Research findings**: Trees that grow without bounds will memorize the training data. Pruning is mathematically necessary for real-world application.
**Original discoveries**: While standard loyalty metrics (like "order 5 times") work for general food apps, tiffin services are subscription-based, meaning standard metrics fail. We need highly targeted, context-aware interventions (like the Surplus Food Matcher).
**Comparison matrix**: 
- *Neural Networks*: High accuracy, black box (cannot explain why it chose a customer).
- *Decision Trees*: Good accuracy, 100% interpretable (we can see the exact IF/THEN path).
**Credits**: Inspired by the IBM ML lab for predicting Drug A vs B.

## W_WORK
**Implementation process**:
1. Defined the problem: Commercial kitchens prepping extra food leads to waste.
2. Built a Decision Tree that asks: `IF customer is within 2 miles AND IF they order Paneer frequently THEN send discount.`
3. Addressed subscription fatigue by planning a "churn predictor".
**Tech stack**: 
- Scikit-learn (DecisionTreeClassifier) for the algorithm.
- Python/FastAPI for the backend integration.
**Iterations**:
- *V1*: Let the tree grow infinitely. Resulted in overfitting (too specific rules).
- *V2*: Applied Pruning (`max_depth=3`, `min_samples_leaf=10`). The model generalized perfectly to new customers.
**Credits**: Scikit-learn documentation for pruning strategies.

## A_ART
**Personal issue solved**: It's painful to see good, home-cooked food thrown away simply because of logistics mismatches.
**Design philosophy**: Tech should reduce waste, not just increase convenience.
**Beauty and craft**: Choosing a Decision Tree over a flashy Neural Network because it is interpretable and simple. We value readability and reliability over AI hype.
**Impact and meaning**: Zero-waste food logistics powered by classical machine learning.
**LinkedIn Post Hook**: "What happens when a commercial kitchen accidentally preps too much food? Most restaurants just throw it away. At NaanStop Tiffin, we built a Surplus Food Matcher using the exact same algorithm doctors use to prescribe medication."
**Credits**: The NaanStop Tiffin vision of sustainable, local food delivery.

---
### LinkedIn Post Draft
What happens when a commercial kitchen accidentally preps too much food? Most restaurants just throw it away.

At NaanStop Tiffin, we built a "Surplus Food Matcher" to solve this. 

Here's what I learned:

**T — The Concept:**
We use a Decision Tree—an automated flowchart of IF/THEN questions—to instantly find a nearby customer who loves that exact dish and push them a 30% Flash Sale discount before the food gets cold.

**E — What I Discovered:**
In my IBM Machine Learning lab, I used this exact algorithm to prescribe drugs with 98% accuracy based on patient features. At NaanStop, we use it to reduce Entropy (randomness) until we reach Certainty on which customer gets the offer. 

**W — How I Built It:**
We didn't need a massive, unreadable neural network. We used scikit-learn. The trick? Pruning. By setting a `max_depth`, we stop the tree from "overfitting" and memorizing the data, creating a robust, generalized model.

**A — Why It Matters:**
It hurts to see good food wasted. By leaning into interpretable, simple ML, we are eliminating food waste while offering a highly personalized experience to our subscribers. 

Don't sleep on the classics. Before you reach for a massive Neural Network, ask yourself: Could a simple flowchart solve this?

Thanks to the IBM ML course for the original inspiration.
