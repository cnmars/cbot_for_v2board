import os, logging, pymysql, configparser, datetime, time
from dbutils.pooled_db import PooledDB
from pymysql.cursors import DictCursor
logger = logging.getLogger(__name__)


class V2Database:
    def __init__(self):
        MODULE_REAL_DIR = os.path.dirname(os.path.realpath(__file__))
        config = configparser.ConfigParser()
        config.read(MODULE_REAL_DIR + '/../conf/config.conf')   # 读取配置文件

        host = config.get('Database', 'host')
        user = config.get('Database', 'user')
        pwd = config.get('Database', 'pwd')
        db = config.get('Database', 'db')

        self.pool = PooledDB(
            creator=pymysql,  # 使用pymysql作为连接库
            maxconnections=8,  # 连接池允许的最大连接数
            mincached=2,  # 初始化时，连接池中至少创建的空闲连接数
            maxcached=5,  # 连接池中最多闲置的连接数
            maxshared=1,  # 连接池中最多共享的连接数
            blocking=True,  # 连接池中如果没有可用连接后，是否阻塞等待
            maxusage=None,  # 一个链接最多被重复使用的次数，None表示无限制
            setsession=[],  # 开始会话前执行的命令列表
            cursorclass=DictCursor,  # 设置默认的 cursor 类型
            ping=0,
            # ping MySQL服务端，检查是否服务可用。
            # 0 = 无 = 从不，
            # 1 = 默认 = 无论何时请求，
            # 2 = 创建游标时，
            # 4 = 执行查询时，
            # 7 = 总是
            host=host,
            port=3306,
            user=user,
            password=pwd,
            database=db,
        )

    def __enter__(self):
        self.conn = self.pool.connection()
        self.cursor = self.conn.cursor()
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cursor.close()
        self.conn.close()

    def execute_sql(self, sql, args=None):
        '''执行语句'''
        with self as cursor:
            try:
                cursor.execute(sql, args)
                self.conn.commit()
                return True
            except Exception as e:
                logger.error('execute except %s', e)
                self.conn.rollback()
                return False

    def select_one(self, sql, args=None):
        '''查询一条数据'''
        with self as cursor:
            try:
                cursor.execute(sql, args)
                result = cursor.fetchone()
                return result
            except Exception as e:
                logger.error('select one except %s', e)
                return None

    def select_all(self, sql, args=None):
        '''查询全部数据'''
        with self as cursor:
            try:
                cursor.execute(sql, args)
                result = cursor.fetchall()
                return result
            except Exception as e:
                logger.warning('select all except %s', e)
                return None

    def insert_one(self, sql, args=None):
        '''插入数据'''
        return self.execute_sql(sql, args)

    def delete_one(self, sql, args=None):
        '''删除数据'''
        return self.execute_sql(sql, args)

    def update_one(self, sql, args=None):
        '''更新数据'''
        return self.execute_sql(sql, args)

    def begin_transaction(self):
        '''开始事务'''
        self.conn.begin()

    def commit_transaction(self):
        '''执行事务'''
        self.conn.commit()

    def rollback_transaction(self):
        '''回滚事物'''
        self.conn.rollback()


V2_DB = V2Database()
