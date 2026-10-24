from app.services.drift_scorer import detect_violations, score_file


def test_emergency_file_scores_higher_than_clean():
    dirty = score_file("app/hack.py", complexity=2, emergency_count=3,
                       total_commits=4, violations=0)
    clean = score_file("app/clean.py", complexity=2, emergency_count=0,
                       total_commits=4, violations=0)
    assert dirty["score"] > clean["score"]
    assert dirty["reasons"]


def test_violations_add_to_score():
    base = score_file("models/user.py", complexity=1, emergency_count=0,
                      total_commits=10, violations=0)
    violated = score_file("models/user.py", complexity=1, emergency_count=0,
                          total_commits=10, violations=1)
    assert violated["score"] > base["score"]


def test_detect_violations_models_importing_views():
    imports_by_file = {"models/user.py": ["views.helpers", "os"]}
    layers = {"models": ["models/user.py"], "views": ["views/helpers.py"]}
    assert detect_violations(imports_by_file, layers) == 1
    clean = {"models/user.py": ["db.store"]}
    assert detect_violations(clean, layers) == 0
