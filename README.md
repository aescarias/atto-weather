# Atto Weather

A really simple weather frontend.

![Amsterdam's weather shown in Atto](.github/assets/image.png)

## Features

- Current weather conditions from dozens of locations.
- Weather forecast with 24-hour weather data.
- Air quality and astronomy details.

*Weather data and icons courtesy of [WeatherAPI]*

## Installation

A Windows build for Atto Weather is available for you to use in [Releases](https://github.com/aescarias/atto-weather/releases).

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

Atto Weather relies on [WeatherAPI] for its weather data. To use this service, you must acquire an API key. You can do this by creating an account on [WeatherAPI] and copying the "API key" from the Dashboard into the prompt you see when first opening the application.

After validating your API key, you will be able to select locations and continue to the application.

The amount of forecast days available will depend on your plan. In the free plan, for example, this is currently 3 days (including the present day).

[WeatherAPI]: https://weatherapi.com
