import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# ---------------- ML MODEL ----------------
class DebugModel:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        self.model = LogisticRegression(max_iter=300)

    def train(self, path):
        df = pd.read_csv(path)

        X = self.vectorizer.fit_transform(df["log_text"])
        y = df["category"]

        self.model.fit(X, y)

    def predict(self, text):
        X = self.vectorizer.transform([text])
        return self.model.predict(X)[0]


# ---------------- SMART RULE ENGINE (UPGRADED) ----------------
def rule_fix(log):
    log_lower = log.lower()

    # ---------------- DEPENDENCY ERRORS ----------------
    if "modulenotfounderror" in log_lower or "no module named" in log_lower:
        pkg = extract_pkg(log)
        return "Dependency", f"Run: pip install {pkg}"

    if "importerror" in log_lower:
        return "Dependency", "Check import path or reinstall missing library"

    # ---------------- SYNTAX ERRORS ----------------
    if "syntaxerror" in log_lower:
        return "Syntax Error", "Check syntax: missing ':' , brackets, or indentation"

    if "indentationerror" in log_lower:
        return "Syntax Error", "Fix indentation (spaces/tabs mismatch)"

    # ---------------- NAME ERROR ----------------
    if "nameerror" in log_lower:
        var = extract_var(log)
        return "Name Error", f"Define variable '{var}' before using it"

    # ---------------- TYPE ERROR ----------------
    if "typeerror" in log_lower:
        return "Type Error", "Check data type mismatch (str/int/list)"

    # ---------------- VALUE ERROR ----------------
    if "valueerror" in log_lower:
        return "Value Error", "Invalid value passed to function"

    # ---------------- INDEX ERROR ----------------
    if "indexerror" in log_lower:
        return "Index Error", "List index out of range"

    # ---------------- KEY ERROR ----------------
    if "keyerror" in log_lower:
        return "Key Error", "Dictionary key not found"

    # ---------------- ZERO DIVISION ----------------
    if "zerodivisionerror" in log_lower:
        return "Runtime Error", "Avoid division by zero"

    # ---------------- FILE ERROR ----------------
    if "filenotfounderror" in log_lower:
        return "File Error", "Check file path or file existence"

    # ---------------- ATTRIBUTE ERROR ----------------
    if "attributeerror" in log_lower:
        return "Attribute Error", "Object has no such attribute"

    # ---------------- PERMISSION ERROR ----------------
    if "permission denied" in log_lower:
        return "Environment", "Run as administrator or change file permissions"

    # ---------------- MEMORY ERROR ----------------
    if "memory" in log_lower:
        return "Runtime Error", "Optimize memory usage or reduce dataset size"

    # ---------------- NODE/NPM ERRORS ----------------
    if "npm err" in log_lower:
        return "Build Error", "Run npm install and check package.json"

    # ---------------- DEFAULT ----------------
    return "Unknown", "Analyze full log for deeper debugging"


# ---------------- HELPERS ----------------
def extract_pkg(log):
    try:
        return log.split("'")[1]
    except:
        return "package"


def extract_var(log):
    match = re.search(r"name '(.+?)' is not defined", log)
    if match:
        return match.group(1)
    return "variable"


# ---------------- TEST ----------------
if __name__ == "__main__":
    model = DebugModel()

    model.train("data/error_logs_dataset.csv")

    test_log = "ModuleNotFoundError: No module named 'numpy'"

    print("ML:", model.predict(test_log))
    print("RULE:", rule_fix(test_log))