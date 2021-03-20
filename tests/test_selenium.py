import os
import re
import threading
import unittest

from selenium import webdriver

from app import create_app, db, fake
from app.models import Role, User


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # 啟動 Firefox
        options = webdriver.FirefoxOptions()
        options.add_argument('-private')
        options.add_argument('-headless')
        try:
            cls.client = webdriver.Firefox(options=options)
        except Exception:
            pass

        # 如果瀏覽器無法啟動，就跳過這些測試
        if cls.client:
            # 建立 app
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()

            # 禁止紀錄，來讓 unittest 有簡明的輸出
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')

            # 建立資料庫並填入一些偽造資料
            db.create_all()
            Role.insert_roles()
            fake.users(10)
            fake.posts(10)

            # 加入一位管理員使用者
            admin_role = Role.query.filter_by(permissions=0xfff).first()
            admin = User(
                email='john@example.com',
                username='john',
                password='cat',
                role=admin_role,
                confirmed=True,
            )
            db.session.add(admin)
            db.session.commit()

            # 在執行緒中啟動 Flask 伺服器
            os.environ['FLASK_RUN_FROM_CLI'] = 'false'
            cls.server_thread = threading.Thread(
                target=cls.app.run,
                kwargs={
                    'debug': 'false',
                    'use_reloader': False,
                    'use_debugger': False,
                },
            )
            cls.server_thread.start()

    @classmethod
    def tearDownClass(cls):
        if cls.client:
            # 停止 Flask 伺服器與瀏覽器
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.quit()
            cls.server_thread.join()

            # 銷毀資料庫
            db.drop_all()
            db.session.remove()

            # 移除 app context
            cls.app_context.pop()

    def setUp(self):
        if not self.client:
            self.skipTest('Web browser is not available.')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        # 前往首頁
        self.client.get('http://localhost:5000/')
        self.assertTrue(
            re.search(r'Hello,\s+Stranger', self.client.page_source),
        )

        # 前往登入
        self.client.find_element_by_link_text('Log In').click()
        self.assertIn('<h1>Login</h1>', self.client.page_source)

        # 登入
        self.client.find_element_by_name('email').send_keys('john@example.com')
        self.client.find_element_by_name('password').send_keys('cat')
        self.client.find_element_by_name('submit').click()
        self.assertTrue(re.search(r'Hello,\s+john', self.client.page_source))

        # 前往使用者的個人資訊網頁
        self.client.find_element_by_link_text('Profile').click()
        self.assertIn('<h1>john</h1>', self.client.page_source)
