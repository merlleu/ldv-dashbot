
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
