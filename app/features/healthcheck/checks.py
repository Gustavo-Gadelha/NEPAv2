from app.extensions import db


def database_available():
    db.session.execute(db.text('SELECT 1'))
    return True, 'database ok'
