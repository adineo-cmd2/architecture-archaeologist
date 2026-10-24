from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.analysis_report import AnalysisReport
from app.models.codebase import Codebase
from app.models.drift_record import DriftRecord
from app.models.source_file import SourceFile
from app.models.user import User


def test_user_codebase_files_report_drift_link():
    for table in (DriftRecord.__table__, AnalysisReport.__table__,
                  SourceFile.__table__, Codebase.__table__, User.__table__):
        table.drop(bind=engine, checkfirst=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    u = User(email="t7@example.com", password_hash=hash_password("secret123"))
    db.add(u)
    db.commit()
    db.refresh(u)
    c = Codebase(user_id=u.id, name="demo")
    db.add(c)
    db.commit()
    db.refresh(c)
    assert c.source == "upload"
    f1 = SourceFile(codebase_id=c.id, path="app/main.py",
                    language="python", content="print('hi')")
    f2 = SourceFile(codebase_id=c.id, path="README.md",
                    language="markdown", content="# demo")
    db.add_all([f1, f2])
    db.commit()
    r = AnalysisReport(codebase_id=c.id, pattern="layered",
                       intent="original intent", decisions=["keep it simple"],
                       mermaid="graph TD; A-->B")
    db.add(r)
    db.commit()
    db.refresh(r)
    d = DriftRecord(codebase_id=c.id, path="app/main.py",
                    score=0.2, reasons=["clean"])
    db.add(d)
    db.commit()
    assert db.query(SourceFile).filter_by(codebase_id=c.id).count() == 2
    assert db.query(AnalysisReport).filter_by(codebase_id=c.id).count() == 1
    assert db.query(DriftRecord).filter_by(codebase_id=c.id).count() == 1
    assert r.codebase_id == c.id
    assert d.codebase_id == c.id
    db.close()
