from flask import Flask, render_template, request, redirect, url_for, session
import cv2
import numpy as np
import math
import random
import os
from flask import redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Check if the uploads folder exists, if not, create it
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

p, q, n, m, E, D = None, None, None, None, None, None
import sqlite3

conn = sqlite3.connect('user_data.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        password TEXT NOT NULL
    )
''')

conn.commit()
conn.close()
DATABASE = 'user_data.db'
def is_user_registered(username):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute('SELECT * FROM users WHERE username = ?', (username,))
    user = c.fetchone()

    conn.close()

    return user is not None
def is_prime(number):
    if number <= 1:
        return False
    else:
        for i in range(2, number):
            if number % i == 0:
                return False
        return True

def generate_primes():
    while True:
        prime1 = random.randint(100, 1000)
        prime2 = random.randint(100, 1000)
        if is_prime(prime1) and is_prime(prime2) and prime1 != prime2:
            return prime1, prime2

def generate_E(m):
    coprime_number = 2
    while math.gcd(m, coprime_number) != 1:
        coprime_number = random.randint(2, m - 1)
    return coprime_number

def generate_D(M, E):
    k = 1
    while True:
        d = (((M * k) + 1) / E ) # Use integer division here
        if d == int(d):  # Ensure that d is the modular multiplicative inverse of E
            return int(d)
        k += 1

def generate_key_pair():
    global p, q, n, m, E, D
    p, q = generate_primes()
    n = p * q
    m = (p - 1) * (q - 1)
    e = generate_E(m)
    d = generate_D(m, e)
    return p, q, n, m, e, d

def encrypt_image(flatten_image, E, modulus):
    encrypted_text = [pow(int(flatten_image[i]), E, modulus) for i in range(len(flatten_image))]
    encrypted_text = np.array(encrypted_text)
    return encrypted_text

def decrypt_image(encrypted_image, D, modulus):
    decrypted_text = [pow(int(encrypted_image[i]), D, modulus) for i in range(len(encrypted_image))]
    decrypted_text = np.array(decrypted_text)
    return decrypted_text

def flatten_image(image_array):
    flattened_image = image_array.flatten()
    return flattened_image

def reshape_image(flattened_image, height, width):
    reshaped_image = flattened_image.reshape(height, width, 3)
    return reshaped_image

def convert_flat_2_3D(flat_image, h, w):
    for pixel in flat_image:
        flat_image[pixel] = flat_image[pixel] % 256
    flat_image = flat_image.astype(np.uint8)
    flat_image = reshape_image(flat_image, h, w) 
    return flat_image


def RSA_encryption(img):
    img = cv2.imread(img)
    height, width = img.shape[:2]

    p, q, n, m, E, D = generate_key_pair()
    flat_array_of_original_image = flatten_image(img)

    encrypted_image_text = encrypt_image(flat_array_of_original_image, E, n)
    encrypted_image_img= convert_flat_2_3D(encrypted_image_text, height, width)
    encrypted_image_img= cv2.cvtColor(encrypted_image_img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite("static/encrypted_image.jpg", encrypted_image_img*2)

    decrypted_image_text = decrypt_image(encrypted_image_text, D, n)
    decrypted_image_img = reshape_image(decrypted_image_text, height, width)
    cv2.imwrite("static/decrypted_image.jpg", decrypted_image_img)

@app.route('/')
def home():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('home.html')



# Route for encryption
# Route for encryption
@app.route('/encrypt', methods=['POST'])
def encrypt():
    file = request.files['file']
    filename = file.filename
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    RSA_encryption('uploads/' + file.filename)
    encrypted_image = url_for('static', filename='encrypted_image.jpg')
    return render_template('home.html', encrypted_image=encrypted_image)


# Route for decryption
@app.route('/decrypt', methods=['POST'])
def decrypt():
    decrypted_image = url_for('static', filename='decrypted_image.jpg')

    encrypted_image_path = url_for('static', filename='encrypted_image.jpg')

    return render_template('home.html', decrypted_image=decrypted_image, encrypted_image=encrypted_image_path)

from flask import redirect, url_for, session

@app.route('/logout',methods=['GET', 'POST'])
def logout():
    # Clear all session variables
    session.clear()
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the user already exists
        if is_user_registered(username):
            return render_template('register.html', user_exists=True)

        # If not, insert the user into the database
        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()

        c.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))

        conn.commit()
        conn.close()

        return redirect(url_for('login'))

    return render_template('register.html', user_exists=False)


@app.route('/login', methods=['GET','POST'])
def login():
    error = None

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = sqlite3.connect('user_data.db')
        c = conn.cursor()

        c.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
        user = c.fetchone()

        conn.close()

        if user:
            session['logged_in'] = True
            return redirect(url_for('home'))  # Redirect to home page after successful login
        else:
            error = 'Invalid credentials. Please try again.'

    return render_template('login.html', error=error)





if __name__ == '__main__':
    app.run(debug=True)
