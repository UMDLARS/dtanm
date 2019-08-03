from db.conn import connect_mongo
from mongoengine import Document, StringField, BooleanField, FloatField, MapField, ReferenceField


class Result(Document):
    # id = StringField(primary_key=True)

    # ID Fields
    attack = StringField(required=True, unique_with=['team', 'commit'])
    team = StringField(required=True)
    commit = StringField(required=True)

    # Results
    passed = BooleanField(required=True)


class AuditLog(Document):
    # id = StringField(primary_key=True)
    result = ReferenceField(Result)

    # ID Fields
    attack = StringField(required=True)
    team = StringField(required=True)
    commit = StringField(required=True)

    # Results
    passed = BooleanField(required=True)

    # Result details
    failed_stdout = BooleanField()
    failed_stderr = BooleanField()
    failed_exit_code = BooleanField()
    failed_file_out = BooleanField()

    # Metrics
    start_time = FloatField()
    end_time = FloatField()
    team_time_sec = FloatField()
    gold_time_sec = FloatField()
