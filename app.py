from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from forms import RegistrationForm, LoginForm, NoteForm  # Убедитесь, что у Вас есть эти формы
from models import db, User, Note
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # Укажите Вашу БД
app.config['SECRET_KEY'] = 'your_secret_key'  # Замените на Ваш секретный ключ
db.init_app(app)

# Инициализация LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)  # Устанавливаем хэш пароля
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(url_for('notes'))
    return render_template('login.html', form=form)

@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    form = NoteForm()
    search_query = request.args.get('search')  # Получаем запрос поиска
    user_notes = Note.query.filter_by(user_id=current_user.id)

    if search_query:
        user_notes = user_notes.filter(Note.content.contains(search_query))

    user_notes = user_notes.all()  # Получаем все заметки

    if form.validate_on_submit():
        new_note = Note(
            content=form.content.data,
            category=form.category.data,
            user_id=current_user.id
        )
        db.session.add(new_note)
        db.session.commit()
        flash('Your note has been created!', 'success')
        return redirect(url_for('notes'))

    return render_template('notes.html', notes=user_notes, form=form)

@app.route('/notes/edit/<int:note_id>', methods=['GET', 'POST'])
@login_required
def edit_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.owner != current_user:
        flash('You do not have permission to edit this note.', 'danger')
        return redirect(url_for('notes'))

    form = NoteForm()
    if form.validate_on_submit():
        reminder = None
        if form.reminder_date.data and form.reminder_time.data:
            reminder_date = form.reminder_date.data
            reminder_time = form.reminder_time.data
            reminder = datetime.combine(reminder_date, reminder_time)

        note.content = form.content.data
        note.category = form.category.data
        note.reminder_time = reminder
        db.session.commit()
        flash('Your note has been updated!', 'success')
        return redirect(url_for('notes'))
    elif request.method == 'GET':
        form.content.data = note.content
        form.category.data = note.category
        if note.reminder_time:
            form.reminder_date.data = note.reminder_time.date()
            form.reminder_time.data = note.reminder_time.time()
    return render_template('edit_note.html', form=form)

@app.route('/notes/delete/<int:note_id>', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    if note.owner != current_user:
        flash('You do not have permission to delete this note.', 'danger')
        return redirect(url_for('notes'))

    db.session.delete(note)
    db.session.commit()
    flash('Your note has been deleted!', 'success')
    return redirect(url_for('notes'))

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

scheduler = BackgroundScheduler()

def check_reminders():
    with app.app_context():
        now = datetime.now()
        notes = Note.query.filter(Note.reminder_time <= now).all()
        for note in notes:
            # Здесь Вы можете отправить уведомление пользователю
            print(f"Reminder: {note.content} in category {note.category}")
        #После того, как показaли, удаляем напоминание
            note.reminder_time = None
            db.session.commit()

scheduler.add_job(check_reminders, 'interval', minutes=1)  # Проверять каждую минуту

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание всех таблиц
        scheduler.start()
    app.run(debug=True)