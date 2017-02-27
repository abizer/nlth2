import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash, jsonify
from collections import defaultdict
import datetime
from datetime import datetime as d

DATABASE = 'nlth2x.db'
DEBUG = True

app = Flask(__name__)
app.config.from_object(__name__)


def connect_db():
    db = sqlite3.connect(app.config['DATABASE'])
    db.row_factory = sqlite3.Row
    return db


def get_transaction(tid, return_wrapper=None):
    transaction = g.db.execute(
        'SELECT ROWID, * FROM transactions WHERE ROWID = ? LIMIT 1', (tid,)).fetchone()
    if return_wrapper:
        return return_wrapper(transaction)
    else:
        return transaction


def get_transactions(limit):
    transactions = g.db.execute(
        'SELECT ROWID, * FROM transactions ORDER BY ROWID DESC LIMIT ?', (limit,)).fetchall()
    return transactions


def reduce_transaction(formdata):
    return {key: val for key, val in formdata.iteritems() if key in ['rowid', 'name', 'iid', 'date', 'price', 'open']}


def insert_transaction(name, iid):
    stmt = "INSERT INTO transactions (name, iid, price, open) VALUES (:name, :iid, (SELECT price FROM items WHERE ROWID = :iid), 1)"
    g.db.execute(stmt, {'name': str(name), 'iid': str(iid)})
    g.db.commit()


def update_transaction(formdata):
    transaction = reduce_transaction(formdata)
    stmt = """
		UPDATE transactions SET
			`name` = :name,
			`iid` = :iid,
			`name` = :name,
			`date` = :date,
			`price` = :price,
			`open` = :open
		WHERE ROWID = :rowid
	"""
    g.db.execute(stmt, transaction)
    d.db.commit()
    return get_transaction(transaction['rowid'], dict)


def remove_transaction(tid):
    stmt = "DELETE FROM transactions WHERE ROWID = :rowid"
    g.db.execute(stmt, {'rowid': tid})
    g.db.commit()


def get_item(iid, return_wrapper=None):
    item = g.db.execute(
        "SELECT ROWID, * FROM items WHERE ROWID = ? LIMIT 1", (iid,)).fetchone()
    if return_wrapper:
        return return_wrapper(item)
    else:
        return item


def get_all_items(hide_disabled_and_popular=True):
    groups = defaultdict(list)
    for row in g.db.execute('SELECT ROWID, * FROM items'):
        if hide_disabled_and_popular:
            if not bool(row['disabled']) and 'popular' not in row['attr'].split(','):
                groups[row['group']].append(row)
        else:
            groups[row['group']].append(row)
    return groups


def get_items_by_attr(attr):
    items = []
    for row in g.db.execute('SELECT ROWID, * FROM items'):
        if attr in row['attr'].split(','):
            items.append(row)
    return items


def get_most_popular_items(limit):
    stmt = """
		SELECT items.name, items.price, items.ROWID, COUNT(transactions.iid) as sales 
		FROM transactions INNER JOIN items ON transactions.iid=items.ROWID 
		GROUP BY transactions.iid ORDER BY COUNT(transactions.iid) DESC LIMIT ?;
		"""
    return list(g.db.execute(stmt, (limit,)))


def reduce_item(formdata):
    return {key: val for key, val in formdata.iteritems() if key in ['rowid', 'name', 'group', 'price', 'cost', 'disabled', 'attr']}


def insert_item(name, group, price, cost, disabled, attr):
    stmt = "INSERT INTO items (`name`, `group`, `price`, `cost`, `disabled`, `attr`) VALUES (:name, :group, :price, :cost, :disabled, :attr)"
    g.db.execute(stmt, {'name': str(name), 'group': str(group), 'price': str(
        price), 'cost': str(cost), 'disabled': str(disabled), 'attr': str(attr)})
    g.db.commit()


def update_item(formdata):
    item = reduce_item(formdata)
    stmt = """
				UPDATE items SET
					`name` = :name,
					`group` = :group,
					`price` = :price,
					`cost` = :cost,
					`disabled` = :disabled,
					`attr` = :attr
				WHERE ROWID = :rowid
			"""
    g.db.execute(stmt, item)
    g.db.commit()
    return get_item(item['rowid'], dict)


def remove_item(iid):
    stmt = "DELETE FROM items WHERE ROWID = :rowid"
    g.db.execute(stmt, {'rowid': iid})
    g.db.commit()


@app.before_request
def before_request():
    g.db = connect_db()


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'db', None)
    if db is not None:
        db.close()


@app.route('/')
def show_index():
    groups, popular = get_all_items(True), get_items_by_attr(
        'popular')  # , get_10_most_popular_items()

    return render_template('add_transaction.html', groups=groups, popular=popular)


@app.route('/add/transaction', methods=['POST'])
def add_transaction():
    # will come in like {name: 'First Last', items:[123, 456, 789]}
    if request.form['items']:
        for item in request.form['items'].split(','):
            insert_transaction(request.form['name'], item)
        return jsonify(message="{0}'s order was successful.".format(request.form['name']))
    else:
        return jsonify(message='Error: you must specify items ordered.')


@app.route('/modify/transaction/<int:tid>', methods=['GET', 'POST'])
def modify_transaction(tid):
    if not tid:
        flash('Need transaction id to modify! See stats view.')
        return redirect(url_for('show_index'))
    else:
        if request.method == 'POST':
            transaction = update_transaction(request.form)
            return jsonify(message="{0}'s transaction (#{1}) successfully modified.".format(transaction['name'], tid), transaction=transaction)
        else:
            return render_template('transaction.html', transaction=get_transaction(tid))


@app.route('/delete/transaction/<int:tid>', methods=['GET', 'POST'])
def delete_transaction(tid):
    if not tid:
        return jsonify(message="Error: you must specify a transaction to delete.")
    else:
        remove_transaction(tid)
        return jsonify(message="Transaction {0} removed.".format(tid))


@app.route('/add/item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'GET':
        return render_template('add_item.html')
    else:
        item = reduce_item(request.form)
        item = insert_item(**item)
        return redirect(url_for('show_index'))


@app.route('/modify/item/')
@app.route('/modify/item/<int:iid>', methods=['GET', 'POST'])
def modify_item(iid=None):
    if iid is None:
        return render_template('all_items.html', groups=get_all_items(False))
    else:
        if request.method == 'POST':
            item = update_item(request.form)
            # return jsonify(message="{0} successfully
            # modified.".format(item['name']), item=item)
            return redirect(url_for('show_index'))
        else:
            return render_template('item.html', item=get_item(iid))


@app.route('/delete/item/<int:iid>', methods=['GET', 'POST'])
def delete_item(iid):
    if not iid:
        return jsonify(message="Error: you must specify an item to delete.")
    else:
        remove_item(iid)
        return jsonify(message="Item {0} removed.".format(iid))


def get_date(date):
    data = g.db.execute('SELECT transactions.ROWID, items.name as Item, transactions.name, transactions.date, transactions.price FROM transactions JOIN items ON transactions.iid = items.ROWID WHERE date = ?', (date.strftime('%Y-%m-%d'),))
    return data.fetchall()


def get_revenue(today=False):
    stmt = "SELECT SUM(price) as revenue FROM transactions"
    if today:
        stmt += " WHERE date = date()"
    return g.db.execute(stmt).fetchone()


def get_profit(today=False):
    stmt = "SELECT SUM(transactions.price - items.cost) as profit FROM transactions INNER JOIN items ON transactions.iid = items.rowid"
    if today:
        stmt += " WHERE transactions.date = date()"
    # [0] because sqlite.Cursor returns a list
    return g.db.execute(stmt).fetchone()


@app.route('/sales/')
@app.route('/sales/<context>')
def sales(context=None):
    if not context:
        data = dict()
        # get_date(d.today()) + get_date(d.today() - datetime.timedelta(days=1)) + get_date(d.today() - datetime.timedelta(days=3))
        data['recent_transactions'] = get_transactions(15)
        data['popular_items'] = get_most_popular_items(12)
        data['total_revenue'] = get_revenue()
        data['daily_revenue'] = get_revenue(today=True)
        data['total_profit'] = get_profit()
        data['daily_profit'] = get_profit(today=True)
        return render_template('stats-dashboard.html', context=context, data=data)
    elif context == 'today':
        return render_template('stats.html', context=context, data=get_date(d.today()))
    elif context == 'yesterday':
        return render_template('stats.html', context=context, data=get_date(d.today() - datetime.timedelta(days=1)))
    else:
        try:
            date = d.strptime(context, '%Y-%m-%d')
            return render_template('stats.html', context=context, data=get_date(date))
        except Exception as e:
            return render_template('error.html', error=e)


@app.route('/kitchen')
def kitchen_items():
    items = get_items_by_attr('kitchen')
    kichenidmap = {i['ROWID']: i['name'] for i in items}


@app.route('/help')
def help():
    return render_template('help.html')

if __name__ == '__main__':
    app.run(debug=True)
