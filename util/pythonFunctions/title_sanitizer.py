import unicodedata
import pandas as pd
import re


class TitleSanitizer:
    def __init__(self, file_path):
        self.df = pd.read_excel(file_path)
        self.titles = self.df[(self.df['video_territory_code'] == 'AU') & (self.df['swc_mkt_rank'] < 1000)]['title'].tolist()

    @staticmethod
    def contains_hindi(s):
        # Remove any non-Hindi characters from the string
        s = re.sub(r'[^\u0900-\u097F]', '', s)
        # Check if the string contains any Hindi characters
        return len(s) > 0

    @staticmethod
    def contains_japanese(s):
        # Remove any non-Japanese characters from the string
        s = re.sub(r'[^\u3040-\u309F\u30A0-\u30FF\uFF66-\uFF9F]', '', s)
        # Check if the string contains any Japanese characters
        return len(s) > 0

    @staticmethod
    def contains_korean(s):
        # Remove any non-Korean characters from the string
        s = re.sub(r'[^\u3131-\u3163\uAC00-\uD7A3]', '', s)
        # Check if the string contains any Korean characters
        return len(s) > 0

    @staticmethod
    def contains_telugu(s):
        # Check if the string contains any Telugu characters
        return re.search(r'[\u0C00-\u0C7F]', s) is not None

    @staticmethod
    def contains_tamil(s):
        # Check if the string contains any Tamil characters
        return re.search(r'[\u0B80-\u0BFF]', s) is not None

    @staticmethod
    def contains_kannada(s):
        # Iterate over each character in the string
        for c in s:
            # Check if the character falls in the Kannada unicode block
            if ord(c) >= 0x0C80 and ord(c) <= 0x0CFF:
                return True
        return False
    
    @staticmethod
    def has_malayalam_characters(text):
        for char in text:
            if 'MALAYALAM' in unicodedata.name(char, ''):
                return True
        return False
    # to add more 

    @staticmethod
    def only_english(s):
        t = TitleSanitizer
        return not t.contains_korean(s) and not t.contains_hindi(s) and not t.contains_japanese(s) and not t.contains_telugu(s) and not t.contains_tamil(s) and not t.contains_kannada(s) and not t.has_malayalam_characters(s)

    @staticmethod
    def sanitize(s):
        if s.endswith(" II"):
            s= s.replace(" II", " 2")
        elif s.endswith(" III"):
            s= s.replace(" III", " 3")
        elif s.endswith(" IV"):
            s= s.replace(" IV", " 4")
        elif s.endswith(" V"):
            s= s.replace(" V", " 5")
        elif s.endswith(" VI"):
            s= s.replace(" VI", " 6")
        elif s.endswith(" VII"):
            s= s.replace(" VII", " 7")
        s= s.replace(" &", " and")
        return s

    def get_sanitized_titles(self):
        sanitized_titles = []
        for title in list(set(self.titles)):
            title_name = TitleSanitizer.sanitize(str(title))
            # sanitize and remove emptry string
            if TitleSanitizer.only_english(title_name) and len(str(title))>0:
                sanitized_titles.append(title_name)
        return sanitized_titles
