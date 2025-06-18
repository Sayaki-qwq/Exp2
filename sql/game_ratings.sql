-- 游戏评论表 (包含评分和评论内容)
CREATE TABLE game_reviews (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    game_id INT NOT NULL,
    rating ENUM('like', 'dislike') NOT NULL,
    comment TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY unique_user_game (user_id, game_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE
);

-- 创建索引以提高查询性能
CREATE INDEX idx_game_reviews_game_id ON game_reviews(game_id);
CREATE INDEX idx_game_reviews_user_id ON game_reviews(user_id);
CREATE INDEX idx_game_reviews_created_at ON game_reviews(created_at DESC);