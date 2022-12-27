# BBC News Scraper
This repository is based on [@keleog](https://github.com/keleog/)'s [BBC Pidgin Scraper](https://github.com/keleog/bbc_pidgin_scraper) but generalizes to a lot more languages:

| Language | Language Code | Website |
|---------|--------------|--------|
| Afaan Oromoo | afa | https://www.bbc.com/afaanoromoo |
| Afrique | afr | https://www.bbc.com/afrique |
| Amharic | amh | https://www.bbc.com/amharic |
| Gahuza | gah | https://www.bbc.com/gahuza |
| Hausa | hau | https://www.bbc.com/hausa |
| Igbo | igb | https://www.bbc.com/igbo |
| Somali | som | https://www.bbc.com/somali |
| Swahili | swa | https://www.bbc.com/swahili |
| Tigrinya | tig | https://www.bbc.com/tigrinya |
| Yoruba | yor | https://www.bbc.com/yoruba |
| Nigerian Pidgin | pid | https://www.bbc.com/pidgin |

This scraper works fine as of `23rd of December, 2022`.

## Setup & Installation
- Create a virtual environment 
-  Install required packages
```
pip install -r requirements.txt
```

## Using the scraper
- To scrape all articles from all categories
```
python scraper.py --no_of_articles=-1 --language <language-code> --output_file_name=data/<filename.tsv> --categories=all --time_delay=True --cleanup
```
- To scrape a finite amount of articles from all categories
```
python scraper.py --no_of_articles=<no-of-articles> --language <language-code> --output_file_name=data/<filename.tsv> --categories=all --time_delay=True --cleanup --spread
```
- To check the full list of arguments for the scraper
```
python scraper.py --help
```

You can check language codes in the table above.
The scraper output should be a `tsv` file with four columns: `heading`, `text`, `category`, `url`. See sample output in [data](data/)

## Contribution
BBC regularly changes the HTML class attributes and structure of its website. To ensure that this scraper is maintainable over time, class attributes and other such configurations are separated into [config.yaml](config.yml).
Feel free to raise an issue & open a pull request if you discover a bug or want to propose an improvement.
