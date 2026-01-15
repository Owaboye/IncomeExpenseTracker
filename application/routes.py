from application import app, login_required
from flask import render_template, url_for, flash, redirect, session,  Blueprint
from application.forms import IncomeExpForm, SignUpForm, LoginForm, ForgotPasswordForm, ResetPasswordForm
from application.models import db, IncomeExpTracker, User, Profile
from sqlalchemy import case
from werkzeug.security import generate_password_hash, check_password_hash

routes_bp = Blueprint("routes", __name__)

routes_bp.route('/')
@login_required
def dashboard():
    
    inc_total = db.session.query(
        db.func.sum(IncomeExpTracker.amount)
    ).filter(IncomeExpTracker.type == 'Income',
             IncomeExpTracker.id == session["user_id"]).scalar()
    
    cash_cat = db.session.query(
    IncomeExpTracker.type,
    db.func.sum(IncomeExpTracker.amount).label("Amount")
    ).filter(IncomeExpTracker.id == session["user_id"]).group_by(IncomeExpTracker.type).all()

    data = {row[0]: float(row[1]) for row in cash_cat}

    # Income by Category
    income_by_Category = db.session.query(
        IncomeExpTracker.category,
        db.func.sum(IncomeExpTracker.amount).label("Amount")
    ).filter(IncomeExpTracker.type == 'Income', 
             IncomeExpTracker.id == session["user_id"]).group_by(IncomeExpTracker.category).all()

    # Expenses by Category
    exp_by_Category = db.session.query(
        IncomeExpTracker.category,
        db.func.sum(IncomeExpTracker.amount).label("Amount")
    ).filter(IncomeExpTracker.type == 'Expenses', IncomeExpTracker.id == session["user_id"]).group_by(IncomeExpTracker.category).all()

    monthly_expenses = db.session.query(
        db.func.strftime('%Y-%m', IncomeExpTracker.created_at).label("month"),
        db.func.sum(IncomeExpTracker.amount).label("total")
    ).filter(IncomeExpTracker.type == 'Expenses', IncomeExpTracker.id == session["user_id"]).group_by("month").all()

    
    monthly_income = db.session.query(
        db.func.strftime('%Y-%m', IncomeExpTracker.created_at).label("month"),
        db.func.sum(IncomeExpTracker.amount).label("total")
    ).filter(IncomeExpTracker.type == 'Income', IncomeExpTracker.id == session["user_id"]).group_by("month").all()

    return render_template('dashboard.html', title='Dashboard', 
                           inc_total=inc_total, 
                           data=data,
                           income_by_Category=income_by_Category,
                           exp_by_Category=exp_by_Category,
                           monthly_expenses=monthly_expenses,
                           monthly_income= monthly_income
                           )

routes_bp.route('/get_cashflow')
@login_required
def get_cashflow():
    entries = IncomeExpTracker.query.filter(IncomeExpTracker.id == session["user_id"]).order_by(IncomeExpTracker.created_at.desc()).all()
    cash_cat = db.session.query(
    IncomeExpTracker.type,
    db.func.sum(IncomeExpTracker.amount).label("Amount")
    ).filter(IncomeExpTracker.id == session["user_id"]).group_by(IncomeExpTracker.type).all()

    data = {row[0]: float(row[1]) for row in cash_cat}
    return render_template('cashflow/index.html', entries=entries, data=data, title='All entries')

routes_bp.route('/edit_cashflow/<int:id>', methods=['GET', 'POST'])
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
        income_source = form.income_source.data
        expense_category = form.expense_category.data

        record.category = income_source if form.type.data == 'Income' else expense_category
        
        try:
            db.session.commit()
            flash('Item Edited successfully', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error editing item: {e}', 'danger')
        finally:
            db.session.close()

        return redirect(url_for('get_cashflow'))

    return render_template('cashflow/edit.html', title='Edit cash flow', form=form)

routes_bp.route('/create_cashflow', methods=['GET', 'POST'])
@login_required
def create_cashflow():
    form = IncomeExpForm()
    if form.validate_on_submit():
        amount = form.amount.data
        cash_type = form.type.data
        description = form.description.data
        income_source = form.income_source.data
        expense_category = form.expense_category.data
        if cash_type == 'Income':
            category = income_source
        else:
            category = expense_category

        # Save data into DB
        user_id = session.get('user_id')
        newItem = IncomeExpTracker(
                    user_id = user_id,
                    amount=amount, 
                    type=cash_type, 
                    category=category, 
                    description=description
                    )
        db.session.add(newItem)
        db.session.commit()

        flash('Item added successfully', 'success')
        return redirect(url_for('dashboard'))

    return render_template('cashflow/create.html', title='Add new cash flow', form=form)

routes_bp.route('/delete_cashflow/<int:id>')
@login_required
def delete_cashflow(id):
    record = IncomeExpTracker.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    flash('Item Delete successfully', 'success')
    return redirect(url_for('get_cashflow'))

    return render_template('cashflow/create.html', title='Add new cash flow', form=form)

routes_bp.route('/income/<month>')
@login_required
def monthly_income_items(month):
    items = db.session.query(IncomeExpTracker).filter(
        IncomeExpTracker.type == 'Income',
        db.func.strftime('%Y-%m', IncomeExpTracker.created_at) == month
    ).filter(IncomeExpTracker.id == session["user_id"]).all()
    total = sum( item.amount for item in items)
    return render_template("cashflow/monthly_income_items.html", items=items, month=month, total=total)

routes_bp.route('/expenses/<month>')
@login_required
def monthly_expenses_items(month):
    items = db.session.query(IncomeExpTracker).filter(
        IncomeExpTracker.type == 'Expenses',
        db.func.strftime('%Y-%m', IncomeExpTracker.created_at) == month
    ).filter(IncomeExpTracker.id == session["user_id"]).all()
    total = sum( item.amount for item in items)
    return render_template("cashflow/monthly_expenses_items.html", items=items, month=month, total=total)

# Auth route
routes_bp.route('/sign-in', methods=['GET', 'POST'])
def sign_in():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No record found, please, sign up', 'warning')
            return redirect(url_for('sign_in'))
       
        if not check_password_hash(user.password, password):
            flash('Wrong password', 'danger')
            return redirect(url_for('sign_in'))
        
        session['authenticated'] = True
        session['user_id'] = user.id
        session['email'] = user.email
        session["role"] = user.role
        session['full_name'] = f"{user.first_name} {user.last_name}"

        return redirect(url_for('dashboard'))

    return render_template('auth/sign-in.html', form=form)

routes_bp.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    form = SignUpForm()
    if form.validate_on_submit():
        fname = form.first_name.data
        lname = form.last_name.data
        email = form.email.data
        password = form.password.data

        password_hash = generate_password_hash(password)
        user = User.query.filter_by(email=email).first()

        if user:
            flash('Email already taken, please, use another one', 'danger')
            return redirect(url_for('sign_up'))
        newUser = User(first_name=fname, last_name=lname, email=email, password=password_hash)
        db.session.add(newUser)
        db.session.commit()

        profile = Profile(user_id=newUser.id)
        db.session.add(profile)
        db.session.commit()

        flash('Registration successful, please, sign in', 'success')
        return redirect(url_for('sign_in'))

    return render_template('auth/sign-up.html', form=form)

routes_bp.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No record with that email. Please, contact the admin or sign up', 'danger')
            return redirect(url_for('forgot_password'))
        
        flash('Please, reset your password', 'info')
        session['email'] = user.email
        return redirect(url_for('reset_password'))
    
    return render_template('auth/forgot_password.html', form=form)

routes_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    form = ResetPasswordForm()
    if form.validate_on_submit():
        confirm_password = form.confirm_password.data
        password = form.password.data

        email = session.get('email')
        user = User.query.filter_by(email=email).first()

        if not user:
            flash('No record found, please, sign up', 'warning')
            return redirect(url_for('sign_up'))
       
        password_hash = generate_password_hash(password)
        user.password = password_hash
        db.session.commit()

        flash('Password reset successfully, please, sign in', 'success')
        return redirect(url_for('sign_in'))

    return render_template('auth/reset_password.html', form=form)


routes_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('sign_in'))