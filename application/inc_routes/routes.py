from flask import Blueprint, render_template, redirect, url_for, flash
from application import db, login_required
from application.forms import IncomeTypeForm
from application.models import IncomeExpTracker, User, Profile
from werkzeug.security import generate_password_hash, check_password_hash

inc_bp = Blueprint('income', __name__, url_prefix='/income')

@inc_bp.route('/')
def index():
    form = IncomeTypeForm()
    return render_template('income/create.html', form=form)