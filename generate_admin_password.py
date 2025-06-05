#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成管理员密码哈希的脚本
密码: 123456
哈希方法: scrypt
"""

from werkzeug.security import generate_password_hash

def generate_admin_password():
    """生成管理员密码哈希"""
    password = "123456"
    
    hashed_password = generate_password_hash(password, method='scrypt')
    
    print(f"哈希密码: {hashed_password}")
    
    return hashed_password

if __name__ == "__main__":
    generate_admin_password() 