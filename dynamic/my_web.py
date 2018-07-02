import re
import urllib.parse

# 自动添加数据到字典
import pymysql


def route(my_date):
    def func_out(func):
        # 程序一运行就有参数
        URL_FUNC_DICT[my_date] = func

        def func_in():
            # 这里使用的话需要调用index()才能添加
            # URL_FUNC_DICT[my_date] = func
            func()
        return func_in
    return func_out


# 函数列表
URL_FUNC_DICT = dict()


# 处理动态资源
@route("/index.html")
def index(ret):

    with open("./templates/index.html") as f:
        content = f.read()
    # 创建数据库连接
    db = pymysql.connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                         charset='utf8')
    # 游标
    cursor = db.cursor()
    sql = "select * from info;"
    cursor.execute(sql)
    my_stock = cursor.fetchall()

    html_template = """
    <tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>
            <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
        </td>
    """

    html = ""
    for i in my_stock:
        html += html_template % (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[1])

    content = re.sub(r"\{%content%\}", html, content)
    cursor.close()
    db.close()
    return content


@route("/center.html")
def center(ret):
    with open("./templates/center.html") as f:
        content = f.read()

    # 创建数据库连接
    db = pymysql.connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                         charset='utf8')
    # 游标
    cursor = db.cursor()
    sql = "select i.code,i.short,i.chg,i.turnover,i.price,i.highs,f.note_info from info as i inner join focus as f on i.id = f.id;"
    cursor.execute(sql)
    my_stock = cursor.fetchall()

    html_template = """<tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>
                <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
            </td>
            <td>
                <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
            </td>
        </tr>"""

    html = ""
    for i in my_stock:
        html += html_template % (i[0], i[1], i[2], i[3], i[4], i[5], i[6], i[0], i[0])

    content = re.sub(r"\{%content%\}", html, content)
    return content


@route(r"/add/(\d+)\.html")
def add(ret):
    stock_code = ret.group(1)
    # 创建数据库连接
    db = pymysql.connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                         charset='utf8')
    # 游标
    cursor = db.cursor()
    # 1.检查股票是否存在
    sql = "select * from info where code=%s"
    cursor.execute(sql, [stock_code])
    info_result = cursor.fetchall()
    if not info_result:
        cursor.close()
        db.close()
        return "没有这个股票"

    # 2.股票是否关注了
    sql = "select * from focus where id=(select id from info where code=%s)"
    cursor.execute(sql, [stock_code])
    focus_result = cursor.fetchall()
    if focus_result:
        cursor.close()
        db.close()
        return "股票已被关注"

    # 3.添加数据
    # sql = "select short from info where code=%s"
    sql = "insert into focus(id) (select id from info where code=%s)"
    cursor.execute(sql, [stock_code])
    db.commit()
    cursor.close()
    db.close()
    return "添加成功:%s" % stock_code


@route(r"/del/(\d+)\.html")
def my_delete(ret):
    stock_code = ret.group(1)
    # 创建数据库连接
    db = pymysql.connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                         charset='utf8')
    # 游标
    cursor = db.cursor()
    # 1.检查股票是否存在
    sql = "select * from info where code=%s"
    cursor.execute(sql, [stock_code])
    info_result = cursor.fetchall()
    if not info_result:
        cursor.close()
        db.close()
        return "没有这个股票,无法删除"

    # 2.股票是否关注了
    sql = "select * from focus where id=(select id from info where code=%s)"
    cursor.execute(sql, [stock_code])
    focus_result = cursor.fetchall()
    if not focus_result:
        cursor.close()
        db.close()
        return "股票没有被关注，无法删除"

    # 3.添加数据
    # sql = "select short from info where code=%s"
    sql = "delete from focus where id=(select id from info where code=%s)"
    cursor.execute(sql, [stock_code])
    db.commit()
    cursor.close()
    db.close()
    return "删除成功:%s" % stock_code


@route(r"/update/(\d+)\.html")
def my_update(ret):
    stock_code = ret.group(1)
    with open("./templates/update.html") as f:
        content = f.read()

    # 创建数据库连接
    db = pymysql.connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                         charset='utf8')
    # 游标
    cursor = db.cursor()

    sql = "select note_info from focus where id=(select id from info where code=%s);"
    cursor.execute(sql, [stock_code])
    stock_info = cursor.fetchone()[0]

    content = re.sub(r"\{%code%\}", stock_code, content)
    content = re.sub(r"\{%note_info%\}", stock_info, content)

    cursor.close()
    db.close()

    return content


@route(r"/update/(\d+)/(.*)\.html")
def my_change_info(ret):
    stock_code = ret.group(1)
    my_note_info = ret.group(2)

    my_note_info = urllib.parse.unquote(my_note_info)

    # 创建数据库连接
    db = pymysql.connect(host='localhost', port=3306, user='root', password='mysql', database='stock_db',
                         charset='utf8')
    # 游标
    cursor = db.cursor()

    sql = "update focus set note_info=%s where id=(select id from info where code=%s);"
    cursor.execute(sql, [my_note_info, stock_code])
    db.commit()

    cursor.close()
    db.close()

    return "修改成功"


def application(environ, start_response):
    file_name = environ["url"]
    start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
    try:
        # key是键，value是值
        for key, values in URL_FUNC_DICT.items():
            ret = re.match(key, file_name)
            if ret:
                return values(ret)
            # else:
            #     return values()
        else:
            return "%s 没有发现对应的函数 or 异常" % file_name
    except:
        return "异常"
