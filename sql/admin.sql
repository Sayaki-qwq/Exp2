-- Active: 1749026464239@@127.0.0.1@3306@exp2

-- 插入管理员用户（使用新生成的密码哈希，密码为：123456）
INSERT INTO users (username, email, password, is_admin) VALUES
('root', 'root@mail.ustc.edu.cn', '452c6846eacb62011774460864c7629726d057ea82f8f7c62f8a694f732b8', TRUE); 