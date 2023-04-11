class TextMiner:
    """This class is responsible for mining any desired information out of text descriptions."""
    def __init__(self, text, text_dictionary):
        self.text = text.lower()
        self.text_dictionary = text_dictionary

    def scan_contents(self):
        """
        This function takes the text description from a property as input and will fill the text_dictionary output
        with booleans marking if a certain string is present in the text."""

        for key in self.text_dictionary.keys():
            self.text_dictionary[key] = key.lower() in self.text

        return self.text_dictionary

        return self.text_dictionary

