# Atto Weather

A really simple weather frontend.

![Amsterdam's weather shown in Atto](.github/assets/image.png)

## Features

- Current weather information from dozens of locations
- 3-day forecast with 24-hour weather data
- Air quality and astronomy details

*Weather data and icons courtesy of [WeatherAPI]*

## Installation

A Windows build for Atto Weather is available in [Releases](https://github.com/aescarias/atto-weather/releases).

To install Atto Weather from source, you will need a working copy of Python 3.9 or later.

Clone the repository and create a virtual environment.

```sh
# Clone the repository
git clone https://github.com/aescarias/atto-weather
cd atto-weather

# Create and activate a virtual environment 
# (use the appropriate 'python' command for your environment)
python -m venv .venv

source .venv/bin/activate # run this on Unix likes
.venv/Scripts/activate # run this on Windows
```

Once activated, install the required dependencies and run the application.

```sh
python -m pip install -e .
python -m atto_weather
```

## Setup

Atto Weather uses [WeatherAPI] for its weather data. To use this service, you must acquire an API key. You can do this by creating an account and copying the "API key" from the Dashboard into the prompt you see when first opening the application.

[WeatherAPI]: https://weatherapi.com
