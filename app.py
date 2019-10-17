from app import app

app.debug = True
app.run("0.0.0.0", debug=True, port=5000)