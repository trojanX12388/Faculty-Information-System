from website import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug="true", host="0.0.0.0", port=8000)
    