from bs4 import BeautifulSoup
from os import listdir
from os.path import isfile, join
import os


class Scraper:
    def __init__(self, path):
        self.path = path
        self.file_list = [f for f in listdir(path) if isfile(join(path, f))]

    def scrape_files(self):
        dir_path = "docs"
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        for file in self.file_list:
            if not file.startswith('.'):
                print(file)
                filename = self.path + "/" + file
                html = open(filename, "r")
                # Get text in #content-main
                soup = BeautifulSoup(html, "lxml")
                content = soup.find("section", {"id": "content-main"}).getText()
                # Write to file
                output = open(dir_path + "/" + os.path.splitext(file)[0] + ".txt", "w")
                output.write(content)
                output.close()


def main():
    s = Scraper("concordia/test_html")
    s.scrape_files()


if __name__ == "__main__":
    main()
