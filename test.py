import main

def main_function():
    import sys
    sys.modules["__main__"] = main

if __name__ == "__main__":
    main_function()
