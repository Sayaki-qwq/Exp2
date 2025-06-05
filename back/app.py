from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
import secrets

app = Flask(__name__)
CORS(app, supports_credentials=True)

# MySQL配置
app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_PORT'] = 3306
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Pai31415926.mysql'
app.config['MYSQL_DB'] = 'exp2'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['MYSQL_CHARSET'] = 'utf8mb4'

# JWT配置
app.config['SECRET_KEY'] = secrets.token_hex(32)

mysql = MySQL(app)

# @app.route('/')
# def check_connection():
#     try:
#         conn = mysql.connection  # 尝试获取连接
#         cursor = conn.cursor()
#         cursor.execute("SELECT 1")  # 执行简单查询测试
#         cursor.close()
#         return "✅ MySQL 连接成功！"
#     except pymysql.MySQLError as e:
#         return f"❌ MySQL 连接失败: {str(e)}"
#     except Exception as e:
#         return f"❌ 发生错误: {str(e)}"

# JWT验证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少token!'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
        except:
            return jsonify({'message': '无效的token!'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

# 管理员验证装饰器
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': '缺少token!'}), 401
        try:
            token = token.split(' ')[1]
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            current_user_id = data['user_id']
            
            # 验证用户是否为管理员
            cur = mysql.connection.cursor()
            cur.execute('SELECT is_admin FROM users WHERE id = %s', (current_user_id,))
            user = cur.fetchone()
            cur.close()
            
            if not user or not user['is_admin']:
                return jsonify({'message': '需要管理员权限!'}), 403
                
        except:
            return jsonify({'message': '无效的token!'}), 401
        return f(current_user_id, *args, **kwargs)
    return decorated

# 用户注册
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({'message': '请提供完整的注册信息'}), 400
    
    hashed_password = generate_password_hash(password)
    
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            'INSERT INTO users (username, email, password) VALUES (%s, %s, %s)',
            (username, email, hashed_password)
        )
        mysql.connection.commit()
        return jsonify({'message': '注册成功'}), 201
    except Exception as e:
        return jsonify({'message': '用户名或邮箱已存在'}), 400
    finally:
        cur.close()

# 用户登录
@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')
    
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM users WHERE username = %s', (username,))
    user = cur.fetchone()
    cur.close()
    
    if user and check_password_hash(user['password'], password):
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.utcnow() + timedelta(days=1)
        }, app.config['SECRET_KEY'])
        
        return jsonify({
            'message': '登录成功',
            'token': token,
            'user': {
                'id': user['id'],
                'username': user['username'],
                'email': user['email'],
                'is_admin': user['is_admin']
            }
        })
    
    return jsonify({'message': '用户名或密码错误'}), 401

# 获取游戏列表
@app.route('/api/games', methods=['GET'])
def get_games():
    cur = mysql.connection.cursor()
    # 使用单引号包裹 MySQL 日期格式
    query = '''
        SELECT 
            id, title, description, type, 
            DATE_FORMAT(release_date, '%Y-%m-%d') as release_date,
            price, developer, publisher, image_url, created_at 
        FROM games
    '''
    cur.execute(query)
    games = cur.fetchall()
    cur.close()
    return jsonify(games)

# 搜索游戏
@app.route('/api/games/search', methods=['GET'])
def search_games():
    search_term = request.args.get('q', '').strip()
    
    if not search_term:
        return jsonify([])
    
    cur = mysql.connection.cursor()
    try:
        # 仅根据游戏标题进行模糊搜索，支持中文
        query = '''
            SELECT 
                id, title, description, type, 
                DATE_FORMAT(release_date, '%Y-%m-%d') as release_date,
                price, developer, publisher, image_url, created_at 
            FROM games 
            WHERE title LIKE CONCAT('%', %s, '%')
            ORDER BY title
        '''
        cur.execute(query, (search_term,))
        games = cur.fetchall()
        cur.close()
        return jsonify(games)
    except Exception as e:
        cur.close()
        return jsonify({'message': f'搜索失败: {str(e)}'}), 400

# 获取用户购物车
@app.route('/api/cart', methods=['GET'])
@token_required
def get_cart(current_user_id):
    cur = mysql.connection.cursor()
    cur.execute(
        '''SELECT g.* 
           FROM cart_items ci 
           JOIN games g ON ci.game_id = g.id 
           WHERE ci.user_id = %s''',
        (current_user_id,)
    )
    items = cur.fetchall()
    cur.close()
    return jsonify({'items': items})

# 添加到购物车
@app.route('/api/cart/add', methods=['POST'])
@token_required
def add_to_cart(current_user_id):
    data = request.get_json()
    game_id = data.get('gameId')
    
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            '''INSERT IGNORE INTO cart_items (user_id, game_id) 
               VALUES (%s, %s)''',
            (current_user_id, game_id)
        )
        mysql.connection.commit()
        return jsonify({'message': '添加成功'})
    except Exception as e:
        return jsonify({'message': f'添加失败: {str(e)}'}), 400
    finally:
        cur.close()

# 从购物车移除
@app.route('/api/cart/remove/<int:game_id>', methods=['DELETE'])
@token_required
def remove_from_cart(current_user_id, game_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute(
            'DELETE FROM cart_items WHERE user_id = %s AND game_id = %s',
            (current_user_id, game_id)
        )
        mysql.connection.commit()
        return jsonify({'message': '移除成功'})
    except Exception as e:
        return jsonify({'message': '移除失败'}), 400
    finally:
        cur.close()



# 获取用户游戏库
@app.route('/api/library', methods=['GET'])
@token_required
def get_library(current_user_id):
    cur = mysql.connection.cursor()
    cur.execute(
        '''SELECT g.* 
           FROM user_library ul 
           JOIN games g ON ul.game_id = g.id 
           WHERE ul.user_id = %s''',
        (current_user_id,)
    )
    games = cur.fetchall()
    cur.close()
    return jsonify({'games': games})

# 购买购物车中的游戏
@app.route('/api/purchase', methods=['POST'])
@token_required
def purchase_games(current_user_id):
    cur = mysql.connection.cursor()
    try:
        # 获取购物车中的游戏
        cur.execute(
            'SELECT game_id FROM cart_items WHERE user_id = %s',
            (current_user_id,)
        )
        cart_items = cur.fetchall()
        
        # 将游戏添加到用户的游戏库
        for item in cart_items:
            cur.execute(
                '''INSERT IGNORE INTO user_library (user_id, game_id) 
                   VALUES (%s, %s)''',
                (current_user_id, item['game_id'])
            )
        
        # 清空购物车
        cur.execute(
            'DELETE FROM cart_items WHERE user_id = %s',
            (current_user_id,)
        )
        
        # 获取购买的游戏信息
        game_ids = [item['game_id'] for item in cart_items]
        if game_ids:
            cur.execute(
                'SELECT * FROM games WHERE id IN %s',
                (tuple(game_ids),)
            )
            purchased_games = cur.fetchall()
        else:
            purchased_games = []
        
        mysql.connection.commit()
        return jsonify({
            'message': '购买成功',
            'purchasedGames': purchased_games
        })
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': '购买失败'}), 400
    finally:
        cur.close()

# 添加游戏
@app.route('/api/games', methods=['POST'])
@admin_required
def add_game(current_user_id):
    data = request.get_json()
    required_fields = ['title', 'description', 'type', 'release_date', 'price', 'developer', 'publisher', 'image_url']
    
    # 验证所有必需字段
    for field in required_fields:
        if field not in data:
            return jsonify({'message': f'缺少必需字段: {field}'}), 400
    
    try:
        cur = mysql.connection.cursor()
        cur.execute('''
            INSERT INTO games (title, description, type, release_date, price, developer, publisher, image_url)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            data['title'], data['description'], data['type'], data['release_date'],
            data['price'], data['developer'], data['publisher'], data['image_url']
        ))
        mysql.connection.commit()
        
        # 获取新插入的游戏ID
        game_id = cur.lastrowid
        
        # 获取新插入的游戏数据
        cur.execute('SELECT * FROM games WHERE id = %s', (game_id,))
        new_game = cur.fetchone()
        cur.close()
        
        return jsonify(new_game), 201
    except Exception as e:
        return jsonify({'message': f'添加游戏失败: {str(e)}'}), 400

# 修改游戏
@app.route('/api/games/<int:game_id>', methods=['PUT'])
@admin_required
def update_game(current_user_id, game_id):
    data = request.get_json()
    
    # 验证游戏是否存在
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM games WHERE id = %s', (game_id,))
    game = cur.fetchone()
    
    if not game:
        cur.close()
        return jsonify({'message': '游戏不存在'}), 404
    
    # 预处理数据
    processed_data = {}
    for field in ['title', 'description', 'type', 'release_date', 'price', 'developer', 'publisher', 'image_url']:
        if field in data:
            processed_data[field] = data[field]
    
    # 构建 SQL 更新语句
    if processed_data:
        placeholders = []
        values = []
        for field, value in processed_data.items():
            placeholders.append(f'{field} = %s')
            values.append(value)
        
        values.append(game_id)  # 添加 WHERE 子句的参数
        
        try:
            # 执行更新 - 使用普通字符串而不是f-string
            update_sql = '''
                UPDATE games 
                SET {} 
                WHERE id = %s
            '''.format(', '.join(placeholders))
            
            cur.execute(update_sql, tuple(values))
            mysql.connection.commit()
            
            # 获取更新后的游戏数据，使用简单的日期格式
            # 注意：在MySQL查询中需要使用%%来转义%符号
            select_sql = '''
                SELECT 
                    id, title, description, type,
                    DATE_FORMAT(release_date, '%%Y-%%m-%%d') as release_date,
                    price, developer, publisher, image_url, created_at
                FROM games 
                WHERE id = %s
            '''
            cur.execute(select_sql, (game_id,))
            updated_game = cur.fetchone()
            cur.close()
            
            return jsonify(updated_game)
        except Exception as e:
            mysql.connection.rollback()
            cur.close()
            return jsonify({'message': f'更新游戏失败: {str(e)}'}), 400
    else:
        cur.close()
        return jsonify({'message': '没有提供要更新的字段'}), 400

# 删除游戏
@app.route('/api/games/<int:game_id>', methods=['DELETE'])
@admin_required
def delete_game(current_user_id, game_id):
    cur = mysql.connection.cursor()
    
    # 验证游戏是否存在
    cur.execute('SELECT * FROM games WHERE id = %s', (game_id,))
    game = cur.fetchone()
    
    if not game:
        cur.close()
        return jsonify({'message': '游戏不存在'}), 404
    
    try:
        # 删除相关的购物车记录
        cur.execute('DELETE FROM cart_items WHERE game_id = %s', (game_id,))
        
        # 删除相关的游戏库记录
        cur.execute('DELETE FROM user_library WHERE game_id = %s', (game_id,))
        
        # 删除游戏
        cur.execute('DELETE FROM games WHERE id = %s', (game_id,))
        mysql.connection.commit()
        cur.close()
        
        return jsonify({'message': '游戏删除成功'})
    except Exception as e:
        return jsonify({'message': f'删除游戏失败: {str(e)}'}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)