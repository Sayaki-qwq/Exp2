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
    try:
        # 获取游戏基本信息和好评率
        query = '''
            SELECT 
                g.id, g.title, g.description, g.type, 
                DATE_FORMAT(g.release_date, '%Y-%m-%d') as release_date,
                g.price, g.developer, g.publisher, g.image_url, g.created_at,
                COALESCE(
                    ROUND(
                        (SUM(CASE WHEN gr.rating = 'like' THEN 1 ELSE 0 END) * 100.0 / 
                         NULLIF(COUNT(gr.rating), 0)
                        ), 1
                    ), 0
                ) as like_percentage
            FROM games g
            LEFT JOIN game_reviews gr ON g.id = gr.game_id
            GROUP BY g.id, g.title, g.description, g.type, g.release_date, 
                     g.price, g.developer, g.publisher, g.image_url, g.created_at
            ORDER BY g.id
        '''
        cur.execute(query)
        games = cur.fetchall()
        return jsonify(games)
    except Exception as e:
        return jsonify({'message': f'获取游戏列表失败: {str(e)}'}), 400
    finally:
        cur.close()

# 搜索游戏
@app.route('/api/games/search', methods=['GET'])
def search_games():
    search_term = request.args.get('q', '').strip()
    
    if not search_term:
        return jsonify([])
    
    cur = mysql.connection.cursor()
    try:
        # 搜索游戏并包含好评率信息
        query = '''
            SELECT 
                g.id, g.title, g.description, g.type, 
                DATE_FORMAT(g.release_date, '%%Y-%%m-%%d') as release_date,
                g.price, g.developer, g.publisher, g.image_url, g.created_at,
                COALESCE(
                    ROUND(
                        (SUM(CASE WHEN gr.rating = 'like' THEN 1 ELSE 0 END) * 100.0 / 
                         NULLIF(COUNT(gr.rating), 0)
                        ), 1
                    ), 0
                ) as like_percentage
            FROM games g
            LEFT JOIN game_reviews gr ON g.id = gr.game_id
            WHERE g.title LIKE CONCAT('%%', %s, '%%')
            GROUP BY g.id, g.title, g.description, g.type, g.release_date, 
                     g.price, g.developer, g.publisher, g.image_url, g.created_at
            ORDER BY g.title
        '''
        cur.execute(query, (search_term,))
        games = cur.fetchall()
        return jsonify(games)
    except Exception as e:
        return jsonify({'message': f'搜索失败: {str(e)}'}), 400
    finally:
        cur.close()

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

# 游戏评论和评分相关API

# 获取游戏评分统计
@app.route('/api/games/<int:game_id>/ratings', methods=['GET'])
def get_game_ratings(game_id):
    cur = mysql.connection.cursor()
    try:
        # 获取该游戏的所有评分统计
        cur.execute('''
            SELECT 
                rating,
                COUNT(*) as count
            FROM game_reviews 
            WHERE game_id = %s 
            GROUP BY rating
        ''', (game_id,))
        
        ratings_data = cur.fetchall()
        
        # 计算统计数据
        like_count = 0
        dislike_count = 0
        
        for rating in ratings_data:
            if rating['rating'] == 'like':
                like_count = rating['count']
            elif rating['rating'] == 'dislike':
                dislike_count = rating['count']
        
        total_count = like_count + dislike_count
        like_percentage = round((like_count / total_count * 100) if total_count > 0 else 0, 1)
        
        return jsonify({
            'like_count': like_count,
            'dislike_count': dislike_count,
            'total_count': total_count,
            'like_percentage': like_percentage
        })
    except Exception as e:
        return jsonify({'message': f'获取评分失败: {str(e)}'}), 400
    finally:
        cur.close()

# 获取用户对游戏的评分
@app.route('/api/games/<int:game_id>/ratings/user', methods=['GET'])
@token_required
def get_user_rating(current_user_id, game_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute('''
            SELECT rating, comment 
            FROM game_reviews 
            WHERE user_id = %s AND game_id = %s
        ''', (current_user_id, game_id))
        
        result = cur.fetchone()
        
        return jsonify({
            'rating': result['rating'] if result else None,
            'comment': result['comment'] if result else None
        })
    except Exception as e:
        return jsonify({'message': f'获取用户评分失败: {str(e)}'}), 400
    finally:
        cur.close()

# 获取游戏的所有评论
@app.route('/api/games/<int:game_id>/reviews', methods=['GET'])
def get_game_reviews(game_id):
    cur = mysql.connection.cursor()
    try:
        # 检查用户是否拥有该游戏 (只有拥有游戏的用户才能发表评论)
        cur.execute('''
            SELECT 
                gr.id,
                gr.rating,
                gr.comment,
                gr.created_at,
                gr.updated_at,
                u.username
            FROM game_reviews gr
            JOIN users u ON gr.user_id = u.id
            JOIN user_library ul ON gr.user_id = ul.user_id AND gr.game_id = ul.game_id
            WHERE gr.game_id = %s
            ORDER BY gr.created_at DESC
        ''', (game_id,))
        
        reviews = cur.fetchall()
        
        # 格式化时间戳
        for review in reviews:
            review['created_at'] = review['created_at'].strftime('%Y-%m-%d %H:%M:%S')
            review['updated_at'] = review['updated_at'].strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify(reviews)
    except Exception as e:
        return jsonify({'message': f'获取评论失败: {str(e)}'}), 400
    finally:
        cur.close()

# 用户对游戏进行评论和评分
@app.route('/api/games/<int:game_id>/reviews', methods=['POST'])
@token_required
def add_review(current_user_id, game_id):
    data = request.get_json()
    rating = data.get('rating')
    comment = data.get('comment', '').strip()
    
    if rating not in ['like', 'dislike']:
        return jsonify({'message': '评分必须是 like 或 dislike'}), 400
    
    if not comment:
        return jsonify({'message': '评论内容不能为空'}), 400
    
    if len(comment) > 1000:
        return jsonify({'message': '评论内容不能超过1000字符'}), 400
    
    cur = mysql.connection.cursor()
    try:
        # 检查游戏是否存在
        cur.execute('SELECT id FROM games WHERE id = %s', (game_id,))
        if not cur.fetchone():
            return jsonify({'message': '游戏不存在'}), 404
        
        # 检查用户是否拥有该游戏
        cur.execute('''
            SELECT 1 FROM user_library 
            WHERE user_id = %s AND game_id = %s
        ''', (current_user_id, game_id))
        
        if not cur.fetchone():
            return jsonify({'message': '只有拥有该游戏的玩家才能发表评论'}), 403
        
        # 使用 INSERT ... ON DUPLICATE KEY UPDATE 来处理重复评论
        cur.execute('''
            INSERT INTO game_reviews (user_id, game_id, rating, comment) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            rating = VALUES(rating),
            comment = VALUES(comment),
            updated_at = CURRENT_TIMESTAMP
        ''', (current_user_id, game_id, rating, comment))
        
        mysql.connection.commit()
        
        return jsonify({'message': '评论发表成功', 'rating': rating, 'comment': comment})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': f'评论发表失败: {str(e)}'}), 400
    finally:
        cur.close()

# 删除用户对游戏的评论
@app.route('/api/games/<int:game_id>/reviews', methods=['DELETE'])
@token_required
def delete_review(current_user_id, game_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute('''
            DELETE FROM game_reviews 
            WHERE user_id = %s AND game_id = %s
        ''', (current_user_id, game_id))
        
        mysql.connection.commit()
        
        return jsonify({'message': '评论已删除'})
    except Exception as e:
        mysql.connection.rollback()
        return jsonify({'message': f'删除评论失败: {str(e)}'}), 400
    finally:
        cur.close()

# 保持旧的 rating API 用于兼容性 (重定向到新的 review API)
@app.route('/api/games/<int:game_id>/ratings', methods=['POST'])
@token_required
def rate_game(current_user_id, game_id):
    data = request.get_json()
    rating = data.get('rating')
    
    if rating not in ['like', 'dislike']:
        return jsonify({'message': '评分必须是 like 或 dislike'}), 400
    
    # 如果只是评分没有评论，创建一个默认评论
    default_comment = "推荐" if rating == 'like' else "不推荐"
    
    # 调用新的评论API
    from flask import request as flask_request
    original_json = flask_request.get_json()
    flask_request._cached_json = {'rating': rating, 'comment': default_comment}
    
    return add_review(current_user_id, game_id)

# 删除用户对游戏的评分 (兼容性API)
@app.route('/api/games/<int:game_id>/ratings', methods=['DELETE'])
@token_required
def delete_rating(current_user_id, game_id):
    return delete_review(current_user_id, game_id)

if __name__ == '__main__':
    app.run(debug=True, port=5000)