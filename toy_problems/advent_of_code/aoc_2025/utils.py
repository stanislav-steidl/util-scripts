

from pathlib import Path


class DataHandler:

    def __init__(self,task_workspace:str,task_id:int = 1) -> None:
        self.task_workspace = task_workspace
        self.task_id = task_id

    
    def load_data(self) -> list[str]:
        file_path = Path(self.task_workspace) / "data" / f"{self.task_id}" /"input.txt"
        
        with open(file_path, 'r') as file:
            data = file.read().strip().splitlines()
        return data
    

    @staticmethod
    def parse_letter_and_number(s: str) -> tuple[str, int]:
        letter = s[0]
        number = int(s[1:])
        return letter, number
    


    