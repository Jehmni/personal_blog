# Code Citations

## License: unknown
https://github.com/anifilm/webapp/tree/7ef1a9a8c0dccc125a8c21b22db7db4b9d5c0cda/flask/doit_JumpToFlask/chap03/03-11/%EB%8C%93%EA%B8%80%EA%B8%B0%EB%8A%A5_%EC%B6%94%EA%B0%80/models.py

```
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200)
```


## License: unknown
https://github.com/ajinurcahyo/sewa-buku-using-Flask/tree/5f958dfa971ada6fa2c949d4f45b3b5c73c114d7/app.py

```
Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['
```


## License: unknown
https://github.com/baran61/Task-Manager-App-with-Python/tree/79ff2f0ec8639e71196fcf35185b52675404551f/app.py

```
route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user
```


## License: unknown
https://github.com/youssef035/incident-management-app/tree/8c03d889a031d0c975f47a255d43094c517c63e9/app.py

```
['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash
```


## License: unknown
https://github.com/lekhacse/DevRev-/tree/3c3962f35379778716a5dd7cd253927f3d75b21e/Flight%20ticket%20booking/app.py

```
)
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = get_user_by_username(username)
        if user and check_password_hash(user.password, password):
            session
```

