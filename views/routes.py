from flask import render_template, redirect, flash, url_for, request, abort
from flask_login import current_user, logout_user, login_required, login_user
from flask_mail import Message

from app import app, db, bcrypt, mail
from .forms import RegForm, LoginForm, UpdateAccountForm, \
    DrugsForm, RequestEmailForm, RequestPasswordForm
from models import Users, Drugs, Years, ClassDrugs
from .task import update, update_drugs, create_task


@app.route("/")
def index():
    drugs = Drugs.query.all()
    return render_template("index.html", drugs=drugs)


@app.route("/reg", methods=["GET", "POST"])
def reg_page():
    form = RegForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8")
        user = Users(username=form.username.data,
                     email=form.email.data,
                     hash_password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash("Your account has been created! You are now able to login", "success")
        return redirect(url_for("index"))

    return render_template("reg.html", form=form)


@app.route("/login/", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.hash_password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for("index"))
        else:
            flash("Login Unsuccessful. Pleas check username and password", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect("index")


@app.route("/<string:username>", methods=["GET", "POST"])
@login_required
def account(username):
    form = UpdateAccountForm()
    if form.validate_on_submit():
        update.delay(form.username.data, form.email.data, current_user.username)
        flash("Your account has been update!", "success")
        return redirect(url_for("account", username=username))
    form.username.data = current_user.username
    form.email.data = current_user.email
    user = Users.query.filter(Users.username == username).first()
    return render_template("account.html", username=user, form=form)


@app.route("/drugs/create", methods=["GET", "POST"])
@login_required
def create():
    form = DrugsForm()

    if request.method == "POST":

        create_task.apply_async((form.colloquial_name.data, form.sicenc_name.data, form.formula.data,
                                 form.opening_year.data, form.discoverer.data, current_user.username,
                                 form.class_drugs.data))
        flash("Your drug has been created!", "success")
        return redirect(url_for("index"))
    elif request.method == "GET":
        form.opening_year.choices = [year.year for year in Years.query.all()]
        form.class_drugs.choices = [class_drug for class_drug in ClassDrugs.query.all()]
    return render_template("create.html", form=form)


@app.route("/drugs/<string:sicenc_name>", methods=["GET"])
def drug_detail(sicenc_name):
    drug = Drugs.query.filter(Drugs.sicenc_name == sicenc_name).first()
    return render_template("detail.html", drug=drug)


@app.route("/drugs/<string:sicenc_name>/update", methods=["GET", "POST"])
@login_required
def drug_update(sicenc_name):
    drug = Drugs.query.filter(Drugs.sicenc_name == sicenc_name).first()
    if drug.user != current_user.username:
        abort(403)
    form = DrugsForm()
    if request.method == "POST":

        update_drugs.delay(form.colloquial_name.data,
                           form.sicenc_name.data, form.formula.data, form.opening_year.data,
                           form.discoverer.data, sicenc_name)

        flash("This drug is update", "success")
        return redirect(url_for("drug_detail", sicenc_name=drug.sicenc_name))
    elif request.method == "GET":
        form.opening_year.choices = [year.year for year in Years.query.all()]
        form.class_drugs.choices = [drug.drugs_class for drug in ClassDrugs.query.all()]
        form.colloquial_name.data = drug.colloquial_name
        form.sicenc_name.data = drug.sicenc_name
        form.formula.data = drug.formula
        form.opening_year.data = drug.opening_year
        form.discoverer.data = drug.discoverer
        return render_template("update.html", form=form, title="Update", legend="Update")


@app.route("/drugs/<string:sicenc_name>/delete", methods=["POST"])
@login_required
def delete(sicenc_name):
    drug = Drugs.query.filter(Drugs.sicenc_name == sicenc_name).first()
    if drug.user != current_user.username:
        abort(403)
    db.session.delete(drug)
    db.session.commit()
    flash("Your drug has been delete!", "success")
    return redirect(url_for("index"))


def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message("Password Reset Request",
                  sender="noreplay@demo.com",
                  recipients=[user.email])
    msg.body = f"""To reset your password, visit the following link:
    {url_for("reset_token", token=token, _external=True)}
    
    If you did not make this request then simply ignore this email and change your account
    """

    mail.send(msg)


@app.route("/reset_password", methods=["GET", "POST"])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RequestEmailForm()
    if request.method == "POST":
        user = Users.query.filter(Users.email == form.email.data).first()
        send_reset_email(user)
        flash("An email has been sent with instructions to reset your password", "info")
        return redirect(url_for("login"))
    return render_template("reset_request.html", form=form)


@app.route("/reset_password/<token>")
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = Users.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "warning")
        return redirect(url_for("reset_request"))
    form = RequestPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data)
        user.password = hashed_password
        db.session.commit()
        flash("Your password has been update! You are now able to log in", "success")
    return render_template("reset_token.html", form=form)
