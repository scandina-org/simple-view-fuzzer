class WordFuzzer:
    def __init__(self):
        return
    def fuzz(self,field,button,word):
        field.send_keys(word)
        button.click()
        field.clear_text()