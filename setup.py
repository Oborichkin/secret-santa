import setuptools

setuptools.setup(
    name="santa",
    packages=setuptools.find_packages(),
    version="0.1.0",
    description="Telegram Bot for Secret Santa",
    author="Pavel Oborin",
    author_email="oborin.p@gmail.com",
    url="https://github.com/Oborichkin/secret-santa",
    python_requires=">=3.7",
    install_requires=[
        "python-telegram-bot @ git+https://github.com/python-telegram-bot/python-telegram-bot#egg=python-telegram-bot",
        "python-dotenv",
        "redis",
    ],
)
