# NaanStop Tiffin: Logistic Regression for Delivery & Allergies

## T_TOPIC
**Core concept**: Using Logistic Regression to predict binary outcomes for a tiffin delivery service: (1) Will this delivery be late? (2) Does this menu conflict with a member's allergies?
**Historical context**: Based on concepts from David R. Cox (1958) who formalized logistic regression for binary sequences.
**Current applications**: Predicting probabilities of binary events (e.g., Late vs On-Time, Conflict vs Safe).
**Implementation strategies**: 
- *Smart implementation*: Using an OLS fallback if there are fewer than 10 labeled training rows, gradually building up to a fully trained `sklearn.linear_model.LogisticRegression` as data grows.
**Credits**: IBM ML Lab 1 (OLS foundation) and scikit-learn documentation.

## E_EXPERIENCE
**Personal learning**: Real-world ML isn't just about training models; it's about handling cold starts. The "fallback" mechanism is just as important as the model itself.
**Research findings**: Logistic Regression outputs probabilities (between 0 and 1) rather than hard classifications, which allows us to set custom thresholds based on business logic.
**Original discoveries**: 
1. The "Allergy Alert" threshold must be tuned extremely low (e.g., 0.30 or if ANY keyword overlap is found) because a False Negative is a critical safety failure.
2. The "Delivery Risk" threshold can be dynamic based on the user tier (e.g., 0.35 for Premium/Professionals who need precision vs 0.60 for Standard).
**Comparison matrix**: 
- *Keyword Matching*: Good for day-1 allergy checks but fails on synonyms/regional dialects over time.
- *Logistic Regression*: Learns over time and handles probability thresholds elegantly.
**Credits**: The NaanStop Tiffin E_EXPERIENCE discovery phase.

## W_WORK
**Implementation process**:
1. Built `DeliveryRiskClassifier` to predict if a delivery will be >60 min late using features: `route_order`, `day_of_week`, `stop_count`.
2. Built `AllergyAlertClassifier` to check if tomorrow's dishes conflict with a member's allergies, using a synonym expansion dictionary.
**Tech stack**: 
- Python, SQLAlchemy, scikit-learn (LogisticRegression, StandardScaler), joblib for model persistence.
**What helped**: Persisting the trained model + scaler to disk (`joblib.dump`) so the FastAPI layer remains stateless.
**Iterations**:
- *V1*: Pure OLS linear regression (predicting continuous minutes).
- *V2*: Migrated to Logistic Regression (predicting probability of being late) to better suit the binary "Late / On-Time" action triggers.
**Code and assets**: Implemented in `backend/ai/logistic_regression.py`.
**Credits**: Scikit-learn for the seamless API.

## A_ART
**Personal issue solved**: Making sure hard-working professionals get their tiffin on time without having to ask "where is my food?", and ensuring dietary safety for all members.
**Design philosophy**: Graceful degradation. If the ML model doesn't have enough data (MIN_TRAINING_ROWS = 10), it safely falls back to a simpler heuristic (OLS).
**Beauty and craft**: The code is highly modular, separating the training phase from the prediction phase, and persisting the state beautifully on disk.
**Impact and meaning**: Proactive customer service instead of reactive apologies.
**LinkedIn Post Hook**: "How do you know if a delivery driver is going to be late before they even leave the kitchen? You predict it."

---
### LinkedIn Post Draft
How do you know if a delivery driver is going to be late before they even leave the kitchen? You predict it.

I built a Logistic Regression model for NaanStop Tiffin to classify delivery risk.

Here's what I learned:

**T — The Concept:**
We use Logistic Regression to predict binary outcomes: Will this delivery be late? (Yes/No). We use features like `route_order` and `day_of_week`.

**E — What I Discovered:**
The real secret isn't the model itself; it's the thresholds. We set dynamic thresholds based on the customer: Premium members have a lower alert threshold (0.35) because working professionals need precision. 

**W — How I Built It:**
Built with `scikit-learn` and `joblib` for persistence. The biggest hurdle was the "cold start" problem. If we have less than 10 labeled deliveries, the code gracefully falls back to a simpler OLS model. Iteration beats perfection.

**A — Why It Matters:**
We want to offer proactive customer service instead of reactive apologies. By predicting delays, we send notifications *before* the customer even has to ask "where is my food?"

Thanks to the IBM ML labs for the foundational concepts!
