from flask import Flask, render_template ,request ,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tint.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Tint(db.Model):
    Sno= db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"{self.Sno} - {self.title}"

@app.route('/', methods=['GET', 'POST'])
def hello_world() :
    if request.method=='POST':
        title=request.form['title']
        desc=request.form['desc']
        print(title,desc)
        tint = Tint(title=title , desc=desc)       
        db.session.add(tint)
        db.session.commit()
    allTint = Tint.query.all()
    print(allTint)
    return render_template('index.html' , allTint=allTint)

@app.route('/show')
def product():
    allTint = Tint.query.all()
    print(allTint)
    return 'this is product page'

@app.route('/update/<int:Sno>', methods=['GET', 'POST'])
def update(Sno):
    tint = Tint.query.filter_by(Sno=Sno).first()
    if request.method == 'POST':
        tint.title = request.form['title']
        tint.desc = request.form['desc']
        db.session.commit()
        return redirect('/')
    return render_template('update.html', tint=tint)
   


@app.route('/delete/<int:Sno>')
def delete(Sno):
    tint = Tint.query.filter_by(Sno=Sno).first()
    db.session.delete(tint)
    db.session.commit()

    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)