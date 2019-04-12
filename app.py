from flask import Flask, json, render_template, request, session
import mysql.connector
from werkzeug import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'why would I tell you my secret key?'

@app.route("/")

def main():
    return render_template('index.html')

@app.route('/showSignUp')
def showSignUp():
    return render_template('signup.html')

@app.route('/signUp',methods=['POST','GET'])
def signUp():
    try:
        usrName = request.form['inputName']
        email = request.form['inputEmail']
        pssWd = request.form['inputPassword']

        # validate the received values
        if usrName and email and pssWd:

            # All Good, let's call MySQL
            #MySQL Connection Parameters
            db = mysql.connector.connect(host='host', user='user', passwd='password',db='db')
            cursor = db.cursor()
            cursor.callproc('create_account',(usrName,email,pssWd))
            data = cursor.fetchall()
            print(data)
            if len(data) is 0:
                cursor.commit()
                return json.dumps({'message':'User created successfully !'})
            else:
                return json.dumps({'error':str(data[0])})
        else:
            return json.dumps({'html':'<span>Enter the required fields</span>'})

    except Exception as e:
        return json.dumps({'error':str(e)})

@app.route('/showSignin')
def showSignin():
    return render_template('signin.html')

@app.route('/validateLogin',methods=['POST'])
def validateLogin():
    try:
        usrName = request.form['inputEmail']
        pssWd = request.form['inputPassword']

        # connect to mysql
        db = mysql.connector.connect(host='host', user='user', passwd='password',db='db')
        cursor = db.cursor()
        cursor.callproc('validate_login',(usrName,))
        data = cursor.fetchall()

        if len(data) > 0:
            if check_password_hash(str(data[0][3]),pssWd):
                session['user'] = data[0][0]
                return redirect('/userHome')
            else:
                return render_template('error.html',error = 'Wrong Email address or Password.')
        else:
            return render_template('error.html',error = 'Wrong Email address or Password.')
    except Exception as e:
        return render_template('error.html',error = str(e))
    finally:
        cursor.close()
        con.close()

@app.route('/userHome')
def userHome():
    if session.get('user'):
        return render_template('userHome.html')
    else:
        return render_template('error.html',error = 'Unauthorized Access')

@app.route('/logout')
def logout():
    session.pop('user',None)
    return redirect('/')

if __name__ == "__main__":
    app.run()
