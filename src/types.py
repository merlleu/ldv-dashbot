
class DataClass:
    def __repr__(self):
        return f"{self.__class__.__name__}({', '.join([f'{k} = {v.__repr__()}' for k,v in self.__dict__.items()])})"

class User(DataClass):
    last_name: str
    first_name: str
    id: str
    badge_number: int
    client_number: str
    admin_id: str
    ine: str

class UserGrades(DataClass):
    semester: int
    units: list

class GradesUnit(DataClass):
    name: str
    subjects: list

class GradesSubject(DataClass):
    name: str
    coeff: float
    grades: list

class Grade(DataClass):
    grade: float
    promo_average: float
    name: str