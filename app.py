from flask import Flask, render_template, request, redirect, jsonify, send_file
df = pd.DataFrame([{
'Name': pl.name,
'Age': pl.age,
'Nationality': pl.nationality,
'Position': pl.position,
'GRL': pl.grl,
'Goals': pl.goals,
'Assists': pl.assists,
'MarketValue': pl.market_value,
'Salary': pl.salary
} for pl in players])


totals = {
'Name': 'Totals',
'Age': '',
'Nationality': '',
'Position': '',
'GRL': df['GRL'].sum() if 'GRL' in df else 0,
'Goals': df['Goals'].sum() if 'Goals' in df else 0,
'Assists': df['Assists'].sum() if 'Assists' in df else 0,
'MarketValue': df['MarketValue'].sum() if 'MarketValue' in df else 0,
'Salary': df['Salary'].sum() if 'Salary' in df else 0,
}
df = df.append(totals, ignore_index=True)
output = BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
df.to_excel(writer, index=False, sheet_name='Plantilla')
output.seek(0)
return send_file(output, download_name='plantilla.xlsx', as_attachment=True)


@app.route('/partidos')
def partidos():
matches = MatchNote.query.order_by(MatchNote.date.desc()).all()
return render_template('partidos.html', matches=matches)


@app.route('/match/<int:mid>')
def match_detail(mid):
m = MatchNote.query.get_or_404(mid)
# placeholders para ultimos 5 resultados - integrar API real
last5_home = [('1','V'),('2','E'),('3','P'),('4','V'),('5','V')]
last5_away = [('1','P'),('2','P'),('3','E'),('4','V'),('5','V')]
# cuotas y probabilidades placeholder
odds = {'home':2.0,'draw':3.4,'away':3.1}
probs = {'home':40.0,'draw':25.0,'away':35.0}
return render_template('match.html', match=m, last5_home=last5_home, last5_away=last5_away, odds=odds, probs=probs)


@app.route('/add_match', methods=['POST'])
def add_match():
date = request.form.get('date')
competition = request.form.get('competition')
home = request.form.get('home')
away = request.form.get('away')
comment = request.form.get('comment')
m = MatchNote(date=date, competition=competition, home=home, away=away, comment=comment)
db.session.add(m)
db.session.commit()
return redirect('/partidos')


if __name__ == '__main__':
app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
