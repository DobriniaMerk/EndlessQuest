from questsite import librarian
from flask import Blueprint, flash, g, redirect, render_template, request, url_for
from markdown import markdown
import bleach

bp = Blueprint('paragraph', __name__, url_prefix='/paragraph')


def clean(text):
    return bleach.clean(text, tags=[], strip=True)


@bp.route('/<int:id>', methods=['GET'])
def show(id):
    paragraph = librarian.ask_for_index().execute('SELECT * FROM paragraphs WHERE id = ?', (id,)).fetchone()
    e = True
    if paragraph is None:
        paragraph = {
            'id': id,
            'title': '???',
            'story': 'The story from this point is uncertain. Decide the outcome yourself, if you dare.'
        }
        e = False

    return render_template('paragraph/show.html', paragraph=paragraph, rendered=markdown(paragraph['story']), exists=e)


@bp.route('/<int:id>/edit', methods=('GET', 'POST'))
def edit(id):
    if request.method == 'POST':
        title = clean(request.form['title'])
        story = clean(request.form['story'])
        error = None

        if not title:
            return redirect(url_for('paragraph.show', id=4096))

        db = librarian.ask_for_index()
        if db.execute('SELECT * FROM paragraphs WHERE id = ?', (id,)).fetchone() is None:
            db.execute('INSERT INTO paragraphs (id, title, story) VALUES (?, ?, ?)', (id, title, story))
        else:
            db.execute('UPDATE paragraphs SET title = ?, story = ? WHERE id = ?', (title, story, id))
        db.commit()
        return redirect(url_for('paragraph.show', id=id))

    paragraph = librarian.ask_for_index().execute('SELECT * FROM paragraphs WHERE id = ?', (id,)).fetchone()
    if paragraph is None:
        paragraph = {
            'id': id,
            'title': '',
            'story': ''
        }
    return render_template('paragraph/edit.html', paragraph=paragraph)