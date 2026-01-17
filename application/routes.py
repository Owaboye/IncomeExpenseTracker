from flask import Blueprint, render_template, redirect, url_for, flash, session, abort
from application import db, login_required
from application.forms import IncomeExpForm, SignUpForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from application.models import IncomeExpTracker, User, Profile
from werkzeug.security import generate_password_hash, check_password_hash

routes_bp = Blueprint("routes", __name__, url_prefix='/')






# ---------------- DASHBOARD ----------------
@routes_bp.route('/')
def index():

    return render_template("home.html")

@routes_bp.route('/dashboard')
@login_required
def dashboard():
    
    inc_total = db.session.query(
        db.func.sum(IncomeExpTracker.amount)
    ).filter(IncomeExpTracker.type == 'Income',
             IncomeExpTracker.user_id == session["user_id"]).scalar()
    
    cash_cat = db.session.query(
    IncomeExpTracker.type,
    db.func.sum(IncomeExpTracker.amount).label("Amount")
    ).filter(IncomeExpTracker.user_id == session["user_id"]).group_by(IncomeExpTracker.type).all()

    data = {row[0]: float(row[1]) for row in cash_cat}

    # Income by Category
    income_by_Category = db.session.query(
        IncomeExpTracker.category,
        db.func.sum(IncomeExpTracker.amount).label("Amount")
    ).filter(IncomeExpTracker.type == 'Income', 
             IncomeExpTracker.user_id == session["user_id"]).group_by(IncomeExpTracker.category).all()

    # Expenses by Category
    exp_by_Category = db.session.query(
        IncomeExpTracker.category,
        db.func.sum(IncomeExpTracker.amount).label("Amount")
    ).filter(IncomeExpTracker.type == 'Expenses', IncomeExpTracker.user_id == session["user_id"]).group_by(IncomeExpTracker.category).all()

    monthly_expenses = db.session.query(
        db.func.strftime('%Y-%m', IncomeExpTracker.created_at).label("month"),
        db.func.sum(IncomeExpTracker.amount).label("total")
    ).filter(IncomeExpTracker.type == 'Expenses', IncomeExpTracker.user_id == session["user_id"]).group_by("month").all()

    
    monthly_income = db.session.query(
        db.func.strftime('%Y-%m', IncomeExpTracker.created_at).label("month"),
        db.func.sum(IncomeExpTracker.amount).label("total")
    ).filter(IncomeExpTracker.type == 'Income', IncomeExpTracker.user_id == session["user_id"]).group_by("month").all()

    return render_template('dashboard.html', title='Dashboard', 
                           inc_total=inc_total, 
                           data=data,
                           income_by_Category=income_by_Category,
                           exp_by_Category=exp_by_Category,
                           monthly_expenses=monthly_expenses,
                           monthly_income= monthly_income
                           )

# ---------------- LIST ----------------
@routes_bp.route('/get_cashflow')
@login_required
def get_cashflow():
    query = IncomeExpTracker.query

    if session["role"] != "admin":
        query = query.filter_by(user_id=session["user_id"])

    entries = query.order_by(IncomeExpTracker.created_at.desc()).all()
    cash_cat = db.session.query(
    IncomeExpTracker.type,
    db.func.sum(IncomeExpTracker.amount).label("Amount")
    ).filter(IncomeExpTracker.user_id == session["user_id"]).group_by(IncomeExpTracker.type).all()

    data = {row[0]: float(row[1]) for row in cash_cat}
    return render_template("cashflow/index.html", entries=entries, data=data, title='All entries')


# ---------------- CREATE ----------------
@routes_bp.route('/create_cashflow', methods=['GET','POST'])
@login_required
def create_cashflow():
    form = IncomeExpForm()

    if form.validate_on_submit():
        category = form.income_source.data if form.type.data == "Income" else form.expense_category.data

        record = IncomeExpTracker(
            user_id=session["user_id"],
            amount=form.amount.data,
            type=form.type.data,
            category=category,
            description=form.description.data
        )

        db.session.add(record)
        db.session.commit()

        flash("Record added successfully", "success")
        return redirect(url_for("routes.dashboard"))

    return render_template("cashflow/create.html", form=form)


# ---------------- EDIT ----------------
@routes_bp.route('/edit_cashflow/<int:id>', methods=['GET','POST'])
@login_required
def edit_cashflow(id):

    record = IncomeExpTracker.query.get_or_404(id)

    if record.user_id != session["user_id"] and session["role"] != "admin":
        abort(403)

    form = IncomeExpForm(obj=record)

    if form.validate_on_submit():
        record.amount = form.amount.data
        record.type = form.type.data
        record.description = form.description.data
        record.category = form.income_source.data if form.type.data == "Income" else form.expense_category.data

        db.session.commit()
        flash("Record updated successfully", "success")
        return redirect(url_for("routes.get_cashflow"))

    return render_template("cashflow/edit.html", form=form)


# ---------------- DELETE ----------------
@routes_bp.route('/delete_cashflow/<int:id>')
@login_required
def delete_cashflow(id):

    record = IncomeExpTracker.query.get_or_404(id)

    if record.user_id != session["user_id"] and session["role"] != "admin":
        abort(403)

    db.session.delete(record)
    db.session.commit()

    flash("Record deleted successfully", "success")
    return redirect(url_for("routes.get_cashflow"))


# ---------------- MONTHLY FILTER ----------------
@routes_bp.route('/income/<month>')
@login_required
def monthly_income_items(month):
    query = IncomeExpTracker.query.filter_by(type="Income")

    if session["role"] != "admin":
        query = query.filter_by(user_id=session["user_id"])

    items = query.filter(db.func.strftime('%Y-%m', IncomeExpTracker.created_at)==month).all()
    total = sum(i.amount for i in items)

    return render_template("cashflow/monthly_income_items.html", items=items, month=month, total=total)


@routes_bp.route('/expenses/<month>')
@login_required
def monthly_expenses_items(month):
    query = IncomeExpTracker.query.filter_by(type="Expenses")

    if session["role"] != "admin":
        query = query.filter_by(user_id=session["user_id"])

    items = query.filter(db.func.strftime('%Y-%m', IncomeExpTracker.created_at)==month).all()
    total = sum(i.amount for i in items)

    return render_template("cashflow/monthly_expenses_items.html", items=items, month=month, total=total)

# --- Export route ---
@routes_bp.route('/cashflow/export/<filetype>')
@login_required
def export_cashflow(filetype):
    entries = IncomeExpTracker.query.order_by(IncomeExpTracker.created_at.desc()).all()


# ---------------- AUTH ----------------
@routes_bp.route('/sign-in', methods=['GET','POST'])
def sign_in():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if not user or not check_password_hash(user.password, form.password.data):
            flash("Invalid login credentials", "danger")
            return redirect(url_for("routes.sign_in"))

        session["authenticated"] = True
        session["user_id"] = user.id
        session["email"] = user.email
        session["role"] = user.role
        session["full_name"] = f"{user.first_name} {user.last_name}"

        return redirect(url_for("routes.dashboard"))

    return render_template("auth/sign-in.html", form=form)


@routes_bp.route('/sign-up', methods=['GET','POST'])
def sign_up():
    form = SignUpForm()

    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash("Email already exists", "danger")
            return redirect(url_for("routes.sign_up"))

        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            role="user"
        )

        db.session.add(user)
        db.session.commit()

        db.session.add(Profile(user_id=user.id))
        db.session.commit()

        flash("Registration successful", "success")
        return redirect(url_for("routes.sign_in"))

    return render_template("auth/sign-up.html", form=form)

@routes_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No record with that email. Please, contact the admin or sign up', 'danger')
            return redirect(url_for('routes.forgot_password'))
        
        flash('Please, reset your password', 'info')
        session['email'] = user.email
        return redirect(url_for('routes.reset_password'))
    
    return render_template('auth/forgot_password.html', form=form)

@routes_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        confirm_password = form.confirm_password.data
        password = form.password.data

        email = session.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No record found, please, sign up', 'warning')
            return redirect(url_for('routes.sign_up'))
       
        password_hash = generate_password_hash(password)
        user.password = password_hash
        db.session.commit()

        flash('Password reset successfully, please, sign in', 'success')
        return redirect(url_for('routes.sign_in'))

    return render_template('auth/reset_password.html', form=form)


@routes_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for("routes.sign_in"))
