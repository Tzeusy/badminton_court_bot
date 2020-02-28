# Introduction
Built because I'm lazy to check for badminton court availability one by one from the OnePA website. Built in a day, and subject to consistency of OnePA's website structure (works via webscraping).

## Dependencies
Install python dependencies as follows:
```
python-telegram-bot
requests
beautifulsoup
```

### Setup
Create a `credentials.json` file in the base directory, containing your telegram key under the `telegram_key` key. For example,
```
{
    "telegram_key": "123456:abcdef"
}
```

### Usage
Run ```python3 tele_interface.py```
