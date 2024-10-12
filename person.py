class Person:
    name:str = ""
    column:int = 2
    today:int = -10
    late:bool = False
    points:int = 0
    lates:int = 0
    last_late:bool = False
    stalked: bool = False
    hide: bool = False
    streak: int = 0
    def __init__(self, name: str, column: int) -> None:
        self.name = name
        self.column = column