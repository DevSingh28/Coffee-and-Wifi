from flask import Flask, render_template, flash, redirect, url_for
from flask_bootstrap import Bootstrap5
from forms import RegisterForm, LoginForm, CoffeeForm, ResetPasswordForm, ForgotPasswordForm
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, Boolean
from flask_login import LoginManager, login_user, logout_user, current_user, UserMixin
from werkzeug.security import check_password_hash, generate_password_hash
import smtplib
from itsdangerous import URLSafeTimedSerializer
import os
# import pandas as pd


app = Flask(__name__)
Bootstrap5(app)
app.secret_key = os.environ.get('coffee_key')
serializer = URLSafeTimedSerializer(app.secret_key)

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)


mail = 'devsingh2017dp@gmail.com'
passcode = os.environ.get('gm_pass')


class Base(DeclarativeBase):
    pass


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///info.db'
db = SQLAlchemy(model_class=Base)
db.init_app(app)


class User(db.Model, UserMixin):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String, nullable=False)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)


with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return render_template("index.html", current_user=current_user)


@app.route("/buy", methods=['POST', 'GET'])
def buy():
    return render_template('coffee.html', current_user=current_user)


@app.route('/register', methods=['POST', "GET"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if user:
            flash("The entered email is already registered. Please try again with a different email address.")
            return redirect(url_for('register'))
        new_password = generate_password_hash(
            password=form.password.data,
            method="pbkdf2:sha256",
            salt_length=8
        )
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=new_password,
            verified=False
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        send_verification_email(new_user)
        flash("Registration successful. Please check your email to verify your account.")
        return redirect(url_for('home'))
    return render_template('register.html', form=form, current_user=current_user)


def send_verification_email(user):
    token = serializer.dumps(user.email, salt='email-verification')
    verification_url = url_for('verify_email', token=token, _external=True)
    subject = "Verify Your Email Address"
    body = f"Hello {user.name},\n\nThank you for registering with DS Coffee. Please click the following link to verify your email address: {verification_url}"
    send_email(user.email, subject, body)


@app.route('/verify_email/<token>')
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-verification', max_age=3600)
        user = User.query.filter_by(email=email).first()
        if user:
            user.verified = True
            db.session.commit()
            flash("Email verified successfully!")
        else:
            flash("Invalid verification link.")
    except:
        flash("The verification link is invalid or has expired.")
    return redirect(url_for('login'))


@app.route('/login', methods=['POST', 'GET'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        result = db.session.execute(db.select(User).where(User.email == email))
        user = result.scalar()
        if not user:
            flash("User not found. Please register.", "error")
            return redirect(url_for('login'))
        elif not check_password_hash(user.password, password):
            flash("Incorrect password. Please try again.", "error")
            return redirect(url_for('login'))
        else:
            login_user(user)
            return redirect(url_for('home'))
    return render_template('login.html', form=form, current_user=current_user)


@app.route("/forgot_password", methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()
        if user:
            send_password_reset_email(user)
            flash("An email with instructions to reset your password has been sent.")
            return redirect(url_for('login'))
        else:
            flash("User not found. Please register.", "error")
    return render_template("forgot_password.html", form=form, current_user=current_user)


def send_password_reset_email(user):
    token = serializer.dumps(user.email, salt='password-reset')
    reset_url = url_for('reset_password', token=token, _external=True)
    subject = "Reset Your Password"
    body = f"Hello {user.name},\n\nYou have requested to reset your password. Please click the following link to reset your password: {reset_url}"
    send_email(user.email, subject, body)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
        user = User.query.filter_by(email=email).first()
        if not user:
            flash("Invalid password reset link.", "error")
            return redirect(url_for('login'))
        form = ResetPasswordForm()
        if form.validate_on_submit():
            new_password = generate_password_hash(form.password.data, method="pbkdf2:sha256", salt_length=8)
            user.password = new_password
            db.session.commit()
            flash("Your password has been reset successfully.")
            return redirect(url_for('login'))
    except:
        flash("The password reset link is invalid or has expired.", "error")
        return redirect(url_for('login'))
    return render_template("reset_password.html", form=form, current_user=current_user)


def send_email(recipient, subject, body):
    with smtplib.SMTP("smtp.gmail.com") as connect:
        connect.starttls()
        connect.login(user=mail, password=passcode)
        connect.sendmail(from_addr=mail, to_addrs=recipient, msg=f"Subject: {subject}\n\n{body}")


@app.route("/mychoice", methods=["POST", "GET"])
def create():
    form = CoffeeForm()
    if form.validate_on_submit():
        name = form.name.data
        water = form.water.data
        flavor = form.flavor.data
        icecream = form.icecream.data
        milk = form.milk.data
        sugar = form.sugar.data
        whipped_cream = form.whipped_cream.data
        glass = form.glass.data
        howmany = form.howmany.data
        chocolate = form.chocolate.data
        data = {
            'Name': [name],
            'Water': [water],
            'Flavor': [flavor],
            'IceCream': [icecream],
            'Milk': [milk],
            'Sugar': [sugar],
            'WhippedCream': [whipped_cream],
            'Glass': [glass],
            'HowMany': [howmany],
            'Chocolate': [chocolate]
        }

        # df = pd.DataFrame(data)
        # df.to_csv('coffee_details.csv', index=False)

        subject = "Welcome to Our Coffee Shop!"
        body = f"Hello {current_user.name},\n\nThank you for choosing our coffee shop. We are delighted to have you with us. Your wifi password is: Nhi_btaunga"
        with smtplib.SMTP("smtp.gmail.com") as connect:
            connect.starttls()
            connect.login(user=mail, password=passcode)
            connect.sendmail(
                from_addr=mail,
                to_addrs=current_user.email,
                msg=f"Subject: {subject} \n\n {body}"
            )

        return render_template('success.html')
    return render_template("create.html", form=form, current_user=current_user)


@app.route('/remove', methods=['POST', 'GET'])
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/buyer', methods=['POST', 'GET'])
def buyer():
    subject = "Welcome to Our Coffee Shop!"
    body = f"Hello {current_user.name},\n\nThank you for choosing our coffee shop. We are delighted to have you with us. Your wifi password is: Nhi_btaunga"
    with smtplib.SMTP("smtp.gmail.com") as connect:
        connect.starttls()
        connect.login(user=mail, password=passcode)
        connect.sendmail(
            from_addr=mail,
            to_addrs=current_user.email,
            msg=f"Subject: {subject} \n\n {body}"
        )
    return render_template("success.html", current_user=current_user)


if __name__ == "__main__":
    app.run(debug=True, port=5002)
