from flask import Flask



messages = Flask(__name__)


@messages.route('/', methods=['GET'])
def get_static_string():
    return "Not implemented yet"


if __name__ == '__main__':
    messages.run(port=5200)
