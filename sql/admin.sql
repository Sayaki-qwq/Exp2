-- Active: 1749026464239@@127.0.0.1@3306@exp2

-- 插入管理员用户（使用新生成的密码哈希，密码为：123456）
INSERT INTO users (username, email, password, is_admin) VALUES
('root', 'root@mail.ustc.edu.cn', 'scrypt:32768:8:1$MjGGYpVCWyebZwrM$e1b700b477e080a7c418dc201f6abc764c19330bd6e679cd35483cebab9206ff48628464d848e64fd736491a79e28a92a4f795748946e3d37d1231a5720c8623', TRUE); 