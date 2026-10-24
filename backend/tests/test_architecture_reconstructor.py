from app.services.architecture_reconstructor import infer


def test_mvc_fixture_infers_mvc():
    tree = {"dirs": ["models", "views", "controllers", "models", "views"],
            "files": ["models/user.py", "views/home.py", "controllers/main.py"]}
    imports_by_file = {
        "views/home.py": ["models.user"],
        "controllers/main.py": ["models.user"],
    }
    result = infer(tree, imports_by_file)
    assert result["pattern"] == "mvc"


def test_layered_fixture_infers_layered():
    tree = {"dirs": ["api", "services", "db", "models"],
            "files": ["api/routes.py", "services/billing.py", "db/store.py"]}
    imports_by_file = {
        "api/routes.py": ["services.billing"],
        "services/billing.py": ["db.store"],
    }
    result = infer(tree, imports_by_file)
    assert result["pattern"] == "layered"
