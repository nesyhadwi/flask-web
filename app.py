from flask import Flask, render_template, request, redirect, url_for, session, send_file
import json
import secrets
import pymysql
import openpyxl
from io import BytesIO
secrets.token_hex(16)

from flask import Blueprint

auth = Blueprint('auth', __name__)

app = Flask(__name__)
app.secret_key = 'rahasia123'

conn = pymysql.connect(
    host='localhost',
    user='root',          # ganti sesuai username MySQL kamu
    password='',          # ganti sesuai password MySQL kamu
    database='aplikasi_minimarket',  # ganti sesuai nama database kamu
)


def load_admin_data():
    with open('data/dummy_admin.json') as f:
        return json.load(f)
    

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='aplikasi_minimarket'
        )
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[3]

            if user[3] == 'admin':
                return redirect(url_for('users'))  
            elif user[3] == 'kasir':
                return redirect(url_for('dashboard'))  

        return render_template('login.html', error='Username atau password salah')

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='aplikasi_minimarket'
    )
    c = conn.cursor(pymysql.cursors.DictCursor)
    c.execute("""
        SELECT 
            p.name_product, 
            p.category,
            SUM(td.qty) AS total_terjual
        FROM 
            transaction_details td
        JOIN 
            products p ON td.product_id = p.id_product
        GROUP BY 
            td.product_id
        ORDER BY 
            total_terjual DESC
        LIMIT 10
    """)
    data_produk_terlaris = c.fetchall()
    conn.close()
    return render_template('dashboard.html', produk=data_produk_terlaris)


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/users')
def users():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='aplikasi_minimarket'  # ganti sesuai nama database kamu
    )
    c = conn.cursor()
    c.execute('SELECT * FROM users')
    data = c.fetchall()
    conn.close()
    return render_template('users.html', users=data)


@app.route('/user/create', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='aplikasi_minimarket'
        )
        c = conn.cursor()
        # `%s` untuk pymysql
        c.execute('INSERT INTO users (username, password, role) VALUES (%s, %s, %s)',
                  (username, password, role))
        conn.commit()
        conn.close()

        return redirect(url_for('users'))

    return render_template('user_form.html', user=None)


@app.route('/user/edit/<int:id>', methods=['GET', 'POST'])
def edit_user(id):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='aplikasi_minimarket'
    )
    c = conn.cursor()
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        c.execute('UPDATE users SET username=%s, password=%s, role=%s WHERE id=%s',
                  (username, password, role, id))
        conn.commit()
        conn.close()
        return redirect(url_for('users'))
    else:
        c.execute('SELECT * FROM users WHERE id=%s', (id,))
        user = c.fetchone()
        conn.close()
        return render_template('user_form.html', user=user)


@app.route('/user/delete/<int:id>', methods=['POST'])
def delete_user(id):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='aplikasi_minimarket'
    )
    c = conn.cursor()
    c.execute('DELETE FROM users WHERE id=%s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('users'))

@app.route('/products')
def products():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='aplikasi_minimarket'  # ganti sesuai nama database kamu
    )
    c = conn.cursor()
    c.execute('SELECT * FROM products')
    data = c.fetchall()
    conn.close()
    return render_template('products.html', products=data)


@app.route('/product/create', methods=['GET', 'POST'])
def create_product():
    if request.method == 'POST':
        product_code = request.form['product_code']
        category = request.form['category']
        name_product = request.form['name_product']
        harga = request.form['harga']
        stock = request.form['stock']

        conn = pymysql.connect(
            host='localhost',
            user='root',
            password='',
            database='aplikasi_minimarket'
        )
        c = conn.cursor()
        # `%s` untuk pymysql
        c.execute('INSERT INTO products (product_code, category, name_product, harga, stock) VALUES (%s, %s, %s, %s, %s)',
                  (product_code, category, name_product, harga, stock))
        conn.commit()
        conn.close()

        return redirect(url_for('products'))

    return render_template('product_form.html', product=None)

@app.route('/product/edit/<int:id>', methods=['GET', 'POST'])
def edit_product(id):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='aplikasi_minimarket'
    )
    c = conn.cursor()
    if request.method == 'POST':
        product_code = request.form['product_code']
        category = request.form['category']
        name_product = request.form['name_product']
        harga = request.form['harga']
        stock = request.form['stock']
        c.execute('UPDATE products SET product_code=%s, category=%s, name_product=%s, harga=%s, stock=%s WHERE id_product=%s',
                  (product_code, category, name_product, harga, stock, id))
        conn.commit()
        conn.close()
        return redirect(url_for('products'))
    else:
        c.execute('SELECT * FROM products WHERE id_product=%s', (id,))
        product = c.fetchone()
        conn.close()
        return render_template('product_form.html', product=product)


@app.route('/product/delete/<int:id>', methods=['POST'])
def delete_product(id):
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='aplikasi_minimarket'
    )
    c = conn.cursor()
    c.execute('DELETE FROM products WHERE id_product=%s', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('products'))


from flask import Flask, render_template
import pymysql.cursors

@app.route('/transactions')
def show_transactions():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='aplikasi_minimarket',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            t.id AS transaksi_id,
            t.unique_number,
            t.time AS tanggal,
            t.total,
            p.name_product AS nama_produk,
            p.harga,
            td.qty AS jumlah,
            td.subtotal
        FROM transaction t
        JOIN transaction_details td ON t.id = td.transaction_id
        JOIN products p ON td.product_id = p.id_product
        ORDER BY t.id DESC
    """)
    rows = cursor.fetchall()

    # Gabungkan data per transaksi
    transactions = {}
    for row in rows:
        trx_id = row['transaksi_id']
        if trx_id not in transactions:
            transactions[trx_id] = {
                'id': trx_id,
                'tanggal': row['tanggal'],
                'total': row['total'],
                'items': []
            }
        transactions[trx_id]['items'].append({
            'nama_produk': row['nama_produk'],
            'harga': row['harga'],
            'jumlah': row['jumlah'],
            'subtotal': row['subtotal']
        })

    conn.close()
    return render_template('transaction.html', transactions=list(transactions.values()))


@app.route('/transaction/add', methods=['GET', 'POST'])
def add_transaction():
    conn = pymysql.connect(host='localhost', user='root', password='', database='aplikasi_minimarket')
    c = conn.cursor()

    if request.method == 'POST':
        product_ids = request.form.getlist('product_id[]')
        quantities = request.form.getlist('quantity[]')

        c.execute('SELECT COUNT(*) FROM transaction')
        count = c.fetchone()[0] + 1
        kode_transaksi = f'11{count:03d}'

        total_harga = 0
        subtotal_list = []

        for i in range(len(product_ids)):
            id_product = int(product_ids[i])
            quantity = int(quantities[i])

            # Ambil harga produk
            c.execute('SELECT harga FROM products WHERE id_product=%s', (id_product,))
            result = c.fetchone()
            if not result:
                continue  # jika produk tidak ditemukan, skip
            harga = result[0]
            subtotal = harga * quantity
            subtotal_list.append((id_product, quantity, subtotal))
            total_harga += subtotal

        # Simpan transaksi
        c.execute('INSERT INTO transaction (unique_number, total) VALUES (%s, %s)', (kode_transaksi, total_harga))
        transaction_id = c.lastrowid

        # Simpan detail transaksi
        for id_product, quantity, subtotal in subtotal_list:
            c.execute('INSERT INTO transaction_details (transaction_id, product_id, qty, subtotal) VALUES (%s, %s, %s, %s)',
              (transaction_id, id_product, quantity, subtotal))
            
            # Kurangi stok produk
        c.execute('UPDATE products SET stock = stock - %s WHERE id_product = %s', (quantity, id_product))


        conn.commit()
        conn.close()
        return redirect(url_for('show_transactions'))

    else:
        c.execute('SELECT id_product, name_product, harga FROM products')
        products = c.fetchall()
        conn.close()
        return render_template('add_transaction.html', products=products)
    

@app.route('/riwayat-transaksi', methods=['GET'])
def riwayat_transaksi():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='aplikasi_minimarket',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    query = """
        SELECT 
            t.id AS transaksi_id,
            t.unique_number,
            t.time AS tanggal,
            t.total,
            p.name_product AS nama_produk,
            td.qty AS jumlah,
            td.subtotal
        FROM transaction t
        JOIN transaction_details td ON t.id = td.transaction_id
        JOIN products p ON td.product_id = p.id_product
    """
    params = []
    if start_date and end_date:
        query += " WHERE DATE(t.time) BETWEEN %s AND %s"
        params = [start_date, end_date]

    query += " ORDER BY t.time DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()

    # Gabung berdasarkan transaksi
    transactions = {}
    for row in rows:
        trx_id = row['transaksi_id']
        if trx_id not in transactions:
            transactions[trx_id] = {
                'id': trx_id,
                'unique_number': row['unique_number'],
                'tanggal': row['tanggal'],
                'total': row['total'],
                'items': []
            }
        transactions[trx_id]['items'].append({
            'nama_produk': row['nama_produk'],
            'jumlah': row['jumlah'],
            'subtotal': row['subtotal']
        })

    conn.close()
    return render_template(
        'transaction.html',
        transactions=list(transactions.values()),
        start_date=start_date,
        end_date=end_date
    )


@app.route('/export-excel')
def export_excel():
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')

    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='',
        database='aplikasi_minimarket',
        cursorclass=pymysql.cursors.DictCursor
    )
    cursor = conn.cursor()

    query = """
        SELECT 
            t.unique_number,
            t.time AS tanggal,
            p.name_product AS nama_produk,
            td.qty AS jumlah,
            td.subtotal,
            t.total
        FROM transaction t
        JOIN transaction_details td ON t.id = td.transaction_id
        JOIN products p ON td.product_id = p.id_product
    """
    params = []
    if start_date and end_date:
        query += " WHERE DATE(t.time) BETWEEN %s AND %s"
        params = [start_date, end_date]

    query += " ORDER BY t.time DESC"
    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    # Buat file Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Riwayat Transaksi"
    ws.append(['Kode Unik', 'Tanggal', 'Nama Produk', 'Jumlah', 'Subtotal', 'Total'])

    for row in rows:
        ws.append([
            row['unique_number'],
            row['tanggal'].strftime('%Y-%m-%d %H:%M:%S'),
            row['nama_produk'],
            row['jumlah'],
            row['subtotal'],
            row['total']
        ])

    file_stream = BytesIO()
    wb.save(file_stream)
    file_stream.seek(0)

    return send_file(
        file_stream,
        as_attachment=True,
        download_name='riwayat_transaksi.xlsx',
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


if __name__ == "__main__":
    app.run(debug=True)

