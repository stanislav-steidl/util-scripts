



import logging


def main():
    print("Hello, World!") 




if __name__ == "__main__":


    logging.basicConfig(level=logging.INFO)


    import os
    
    if os.getenv("DEBUG", "False").lower() in ("true", "1", "t"):
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode is enabled.")
    else:
        logging.info("Debug mode is disabled.")

    main()