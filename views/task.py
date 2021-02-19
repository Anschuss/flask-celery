from flask import url_for
from flask_mail import Message

from app import db, client, mail
from models import Users, Drugs, ClassDrugs


@client.task(bind=True)
def update(self, form_username, form_email, username):
    """
    :param form:
    :param user:
    :return:
    """
    user = Users.query.filter(Users.username == username).first()
    user.username = form_username
    user.email = form_email
    db.session.commit()


@client.task(bind=True)
def update_drugs(self, form_colloquial_name, form_sicenc_name, form_formula, form_opening_year, form_discoverer, sicenc_name):
    """
    :param self:
    :param drug:
    :param form:
    :return:
    """
    drug = Drugs.query.filter(Drugs.sicenc_name == sicenc_name).first()

    drug.colloquial_name = form_colloquial_name
    drug.sicenc_name = form_sicenc_name
    drug.formula = form_formula
    drug.opening_year = form_opening_year
    drug.discoverer = form_discoverer
    db.session.commit()


@client.task(bind=True)
def create_task(self, form_colloquial_name, form_sicenc_name,
           form_formula, form_opening_year,
           form_discoverer, username, form_class_drugs):

    drug = Drugs(colloquial_name=form_colloquial_name, sicenc_name=form_sicenc_name,
                 formula=form_formula, opening_year=form_opening_year,
                 discoverer=form_discoverer, user=username)
    # cls = ClassDrugs.query.filter(ClassDrugs.drugs_class == form_class_drugs).first()
    # drug_cls = drug_class(cls.id, drug.id)
    db.session.add(drug)
    db.session.commit()


# @client.task(bind=True)
# def send_reset_email(form_email):
#     """
#     :param form_email:
#     :return:
#     """
#     user = Users.query.filter(Users.email == form_email).first()
#     token = user.get_reset_token()
#     msg = Message("Password Reset Request",
#                   sender="noreplay@demo.com",
#                   recipients=[user.email])
#     msg.body = f"""To reset your password, visit the following link:
#     {url_for("reset_token", token=token, _external=True)}
#
#     If you did not make this request then simply ignore this email and change your account
#     """
#
#     mail.send(msg)