from datetime import datetime

class DataClass:
    def __init__(self, **kwargs):
        for i in kwargs:
            setattr(self, i, kwargs[i])
        
    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{k} = {v.__repr__()}' for k,v in self.__dict__.items()])})"

    def json(c):
        if isinstance(c, DataClass):
            return DataClass.json(c.__dict__)
        elif isinstance(c, list):
            return [DataClass.json(_) for _ in c]
        elif isinstance(c, dict):
            return {k: DataClass.json(v) for k,v in c.items()}
        elif isinstance(c, datetime):
            return c.isoformat()
        else:
            return c
    
class User(DataClass):
    last_name: str
    first_name: str
    id: str
    badge_number: int
    client_number: str
    admin_id: str
    ine: str

class Semester(DataClass):
    semester: int
    units: list

class SemesterUnit(DataClass):
    name: str
    subjects: list

class GradesSubject(DataClass):
    name: str
    id: str
    coeff: float
    grades: list
    promo_average: float
    final_grade: float
    grade_max: float
    evaluation_link: str

class Grade(DataClass):
    grade: float
    max_grade: float
    promo_average: float
    name: str

class Absence(DataClass) :
    subject_id: str
    subject_name: str
    class_type: str
    date: str
    hour: str
    class_duration: str
    state : str


class Presence(DataClass):
    start_time: datetime.date
    end_time: datetime.date
    subject_name: str
    id: int
    hosts: list

    # zoom
    meeting_url: str
    meeting_url_with_password: str
    meeting_passwod: str

    # state
    opened: bool # if the presence is opened by the host
    success: bool # if the presence has been validated by student
    success_time: datetime