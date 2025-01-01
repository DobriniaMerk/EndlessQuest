from questsite import librarian
from flask import Blueprint, redirect, render_template, request, url_for
from markdown import markdown
import bleach
import re

bp = Blueprint('paragraph', __name__, url_prefix='/')

langs = ['ru', 'en']

#TODO: Translation to all text (links, titles, etc.)

locale = {
    'ru': {
        'not_written': {
            'title': '???',
            'story': 'События с этого момента покрываются туманом, и решительно ничего нельзя разобрать.'
        },
        'translate': {
            'title': '???',
            'story': 'Что было дальше никто не знает, но люди знающие утверждают что такое уже происходило, \
            только тогда все было по-английски и никто ничего не понял. Если вы переводчик, можете объяснить тем, кто не столь сведущ.'
        },
        'edittitle': 'Редактировать',
        'edit': 'Изменить',
        'add': 'Добавить',
        'goto': 'Перейти',
    },
    'en': {
        'not_written': {
            'title': '???',
            'story': 'The story from this point is uncertain. Decide the outcome yourself, if you dare.'
        },
        'translate': {
            'title': '???',
            'story': 'What happened next is unclear, but those who have the knowledge of Russian can transfer the truth from over the Edge.'
        },
      'edittitle': 'Edit Paragraph',
      'edit': 'Edit',
      'add': 'Add',
      'goto': 'Goto',
    }
}


def new_paragraph():
    db = librarian.ask_for_index()
    ids = []
    for row in db.execute('SELECT id FROM paragraphs').fetchall():
        ids.append(row['id'])
    raise NotImplementedError  # TODO: select a new index with items in mind


def clean(text):
    return bleach.clean(text, tags=[])


def escape(text):
    # BEWARE: regex black magic
    # It escapes all links that contain anything aside numbers
    return re.sub(r'\[([^]]+)\]\(([^)]*[^\d)][^)]*)\)', r'\[\1\]\(\2\)', text)


def fill_links(text):
    def callback(match):
        return f'[{match.group(1)}]({new_paragraph()})'

    return re.sub(r'\[([^]]*)\]\(\)', callback, text)


@bp.route('/', methods=['GET'])
def index():
    return redirect(url_for('paragraph.show', id=0, lang=langs[0]))

@bp.route('<lang>/<int:id>', methods=['GET', 'POST'])
def show(lang, id):
   if lang not in langs:
        return redirect(url_for('paragraph.show', id=id, lang=langs[0]))

   if request.method == 'POST':
        return redirect(url_for('paragraph.show', id=request.form['id'], lang=lang))

   raw = librarian.ask_for_index().execute('SELECT * FROM paragraphs WHERE id = ?', (id,)).fetchone()
   e = True

   paragraph = {
     'id': id,
     'lang': lang,
     'title': '',
     'story': '',
     'protected': False
   }

   if raw is None:
     paragraph['title'] = locale[lang]['not_written']['title']
     paragraph['story'] = locale[lang]['not_written']['story']
     e = False
   elif raw[ 'title_' + lang] is None:
     paragraph['title'] = locale[lang]['translate']['title']
     paragraph['story'] = locale[lang]['translate']['story']
     print(paragraph)
   else:
     paragraph['title'] = raw['title_' + lang]
     paragraph['story'] = raw['story_' + lang]
     paragraph['protected'] = raw['protected']
   paragraph['rendered'] = markdown(escape(paragraph['story']))
   return render_template('paragraph/show.html', paragraph=paragraph, exists=e, locale=locale[lang])


#TODO: Show "edit" when redirected by edit link and same for add
@bp.route('<lang>/<int:id>/edit', methods=('GET', 'POST'))
def edit(lang, id):
    if lang not in langs:
        return redirect(url_for('paragraph.show', id=id, lang=langs[0]))

    if request.method == 'POST':
        title = clean(request.form['title'])
        story = fill_links(clean(request.form['story']))

        if not title:
            return redirect(url_for('paragraph.show', id=4046, lang=lang))

        db = librarian.ask_for_index()
        if db.execute('SELECT * FROM paragraphs WHERE id = ?', (id,)).fetchone() is None:
            db.execute(f'INSERT INTO paragraphs (id, title_{lang}, story_{lang}) VALUES (?, ?, ?)', (id, title, story))
        else:
            db.execute(f'UPDATE paragraphs SET title_{lang} = ?, story_{lang} = ? WHERE id = ?', (title, story, id))
        db.commit()
        return redirect(url_for('paragraph.show', id=id, lang=lang))

    raw = librarian.ask_for_index().execute('SELECT * FROM paragraphs WHERE id = ?', (id,)).fetchone()
    if raw is None:
      paragraph = {
        'id': id,
        'title': '',
        'story': ''
      }
    else:
      paragraph = {
        'id': id,
        'title': raw['title_' + lang],
        'story': raw['story_' + lang]
      }

    return render_template('paragraph/edit.html', paragraph=paragraph, ln=lang, locale=locale[lang])
