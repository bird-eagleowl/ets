# util/util.py
import json

# def add(x, y):
#     return x + y

# def subtract(x, y):
#     return x - y

class Calculator:
    def __init__(self):
        pass

    def multiply(self, x, y):
        return x * y

    def divide(self, x, y):
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y

class PrettyJson:
    def __init__(self):
        pass
    def pretty_print_json(jsonOrDict):
        try:

            # JSON 형식의 문자열인지 확인
            if isinstance(jsonOrDict, str):
                parsed = json.loads(jsonOrDict)
            # 딕셔너리인지 확인
            elif isinstance(jsonOrDict, dict):
                parsed = jsonOrDict
            else:
                raise TypeError("Input must be a JSON string or a dictionary.")
            
            pretty = json.dumps(parsed, indent=4, ensure_ascii=False)
            print(pretty)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON: {e}")
        except TypeError as e:
            print(f"TypeError: {e}")
        except Exception as e:
            print(f"An error occurred: {e}")