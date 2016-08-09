# coding=utf-8

"""
    It's used to get the winning lottery numbers from the "http://baidu.lecai.com/lottery/draw/list/3".
"""
from __future__ import division
import urllib, urllib2
import sys, re, time
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

try:
    from bs4 import BeautifulSoup
except:
    from BeautifulSoup import BeautifulSoup


class GetWinningNumbers(object):
    def __init__(self, url):
        self.url = url
        self.record = 0
        self.connect_db()
        self.get_years()

    def connect_db(self):
        self.db = sqlite3.connect('winning_numbers.db')
        self.cursor = self.db.cursor()
        create_table = '''create table lottery (
                      id      int unsigned not null   primary key,
                      first   int unsigned not null,
                      second  int unsigned not null,
                      third   int unsigned not null
        )'''

        try:
            self.cursor.execute('SELECT max(id) FROM lottery')
            self.max_id_inserted = self.cursor.fetchall()[0][0]
        except:
            self.cursor.execute(create_table)
            self.max_id_inserted = None

    def get_webpage(self):
        data = urllib.urlencode(self.req_data)
        requests = urllib2.Request(self.url, data=data)
        requests.add_header('User-Agent',
                            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
                            Chrome/51.0.2704.103 Safari/537.36')
        try:
            response = urllib2.urlopen(requests)
        except Exception as error:
            print error
            sys.exit(1)
        return response.read()

    def get_years(self):
        # self.this_year = time.strftime('%Y')
        self.req_data = {'d': '2004-01-01'}
        content = self.get_webpage()
        soup = BeautifulSoup(content)
        years = soup.find('select', attrs={'name': "d"})
        self.years = [int(year) for year in years.stripped_strings]
        self.years.reverse()

    def get_winning_numbers(self, content):
        counter = []
        win_numbers = []
        soup = BeautifulSoup(content)
        # 获取期号
        counts = soup.find_all('a', href=re.compile(r"/lottery/draw/view/3/"))
        # 获取中奖号码
        luck_numbers = soup.find_all('span', class_='ball_1')
        if len(counts) == 0 or len(luck_numbers) == 0:
            print u"网页代码发生变化，需要改变查询规则。"
            sys.exit(1)

        for count in counts:
            counter.append(int(count.string))
        for num in luck_numbers:
            win_numbers.append(int(num.string))
        return counter[::-1], win_numbers[::-1]

    def insert_data(self, year, flag):
        self.req_data = {'d': str(year) + '-01-01'}
        content = self.get_webpage()
        counter, win_num = self.get_winning_numbers(content)
        if flag == "all":
            position = None
            self.record += len(counter)
        else:
            position = flag - counter[-1]
            self.record += -1 * position
            if position == 0:
                return
        insert = 'insert into lottery(id,first,second,third) values (?,?,?,?)'
        for index, id in enumerate(counter[position:]):
            value = [id, win_num[index * 3 + 2], win_num[index * 3 + 1], win_num[index * 3]]
            self.cursor.execute(insert, value)
        self.db.commit()

    def update_data(self):
        max_year = max(self.years)
        vacancy = max_year % 100 - self.max_id_inserted // 1000
        for year in range(max_year - vacancy, max_year + 1):
            if year == max_year - vacancy:
                print u"正在补插%d年的中奖记录..." % year
                self.insert_data(year, self.max_id_inserted)
            else:
                print u"正在插入%d年的中奖记录..." % year
                self.insert_data(year, "all")
        print u"中奖号码数据库更新了%d条记录" % self.record

    def start_Spider(self):
        if self.max_id_inserted is None:
            t = time.time()
            for year in self.years:
                print u"正在插入%d年的中奖记录..." % year
                self.insert_data(year, "all")
            print u"共计插入%d条记录" % self.record
            print u"耗时%.2f秒" % (time.time() - t)
        else:
            t = time.time()
            self.update_data()
            print u"耗时%.2f秒" % (time.time() - t)

    def close(self):
        self.db.commit()
        self.cursor.close()
        self.db.close()


class DataAnalysis(object):
    def __init__(self, db_name):
        self.df = pd.read_sql('select * from lottery order by id desc', sqlite3.connect(db_name))
        self.table_length = 0
        self.filter_df = self.df.copy()

    def add_col_sum(self):
        self.df['sum'] = pd.Series(self.df['first'] + self.df['second'] + self.df['third'], index=self.df.index)

    def draw_table(self, data):
        row = '  |  '.join([str(d) for d in data[1]])
        table_width = len(row)
        print u"最近%d期的中奖号码：" % self.table_length
        print u"期号".center(9) + u"百位".center(4) + u"十位".center(4) + u"个位".center(4)
        for i in range(self.table_length):
            row = '  |  '.join([str(d) for d in data[i]])
            print '+' + (table_width + 4) * '-' + '+'
            print '|  ' + row + '  |'
        print '+' + (table_width + 4) * '-' + '+'

    def filter(self, how_many):
        # 查看最近的中奖号码
        self.table_length = how_many
        data = self.filter_df.iloc[:how_many, :].values.tolist()
        self.draw_table(data)

    def numbers_frequency(self):
        df2 = pd.DataFrame()
        count1 = pd.Series(self.df['first'].value_counts())
        count2 = pd.Series(self.df['second'].value_counts())
        count3 = pd.Series(self.df['third'].value_counts())
        df2['counts'] = count1 + count2 + count3
        plt.plot(df2)
        plt.title("the distribution of winning numbers 0-9")
        plt.xlabel('numbers')
        plt.ylabel('frequency of number')
        plt.show()

    def normal_distribution(self):
        self.add_col_sum()
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        ax.hist(self.df['sum'], bins=100, color='red')
        plt.title("the distribution of sum")
        plt.xlabel('sum')
        plt.ylabel('Count of sum')
        plt.show()
        # fig.savefig('fig.pdf')


if __name__ == '__main__':
    url = "http://baidu.lecai.com/lottery/draw/list/3"
    lottery = GetWinningNumbers(url)
    lottery.start_Spider()
    lottery.close()

    analysis = DataAnalysis('winning_numbers.db')
    analysis.normal_distribution()
    analysis.numbers_frequency()
    analysis.filter(10)
