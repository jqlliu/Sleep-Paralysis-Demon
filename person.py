class Person:
    name:str = ""
    column:int = 2
    today:int = -10
    late:bool = False
    place: int = 0
    time: int = 0
    def __init__(self, name: str, column: int) -> None:
        self.name = name
        self.column = column