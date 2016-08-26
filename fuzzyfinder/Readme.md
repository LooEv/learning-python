# 模糊查询FuzzyFinder

模糊查询可以算是现代编辑器（在选择打开的文件时）的一个必备特性了，它所做的工作就是根据用户输入的部分内容，猜测用户想要的文件名，并提供一个推荐列表供用户选择。“模糊匹配”这是一个极为有用的特性，同时也非常易于实现。

很容易想到，使用python的re模块可以轻松实现。此脚本是用来模糊搜索指定路径下用户想看搜索的文件名

## 实现过程

* 由于我想实现中文查询，所以一定要解决好编码问题。
```python
def system_detect():
    system = platform.system()
    # 此处只考虑这几种常见的情况，Windows环境下请使用cmd运行此脚本
    systems = {'Windows': ('gbk', True), 'Linux': ('utf-8', False), 'Darwin': ('utf-8', True)}
    if systems.get(system, None):
        return systems[system]
    else:
        raise Exception("your system is out of my consideration,sorry.The Chinese maybe display abnormally!")
```
systems字典的键表示运行此脚本的计算机的系统，值为一个元组，第一个元素为系统采用的编码方式，第二个元素为该系统是否忽略文件名的大小写

* 为了使查询结果根据符合用户的要求，需要对匹配结果进行筛选
  * 首先，使用非贪婪模式匹配，`len(match.group(0)`反应匹配的紧凑程度，`match.start()`反应匹配到的起始位置
  * 用 `len(match.group(0)) < (len(keyword) + 5)`来去掉匹配结果不紧凑的情况，比如想要匹配包含"mux"的文件，如果不使用限制条件，会匹配到"my stupid fuzzy find results.txt"，这个匹配结果非常不紧凑。
  * 将匹配结果存入suggestions列表里面，列表的元素为元组，然后根据匹配结果的紧凑程度和起始位置排序，将最符合用户要求的结果呈现在最前面
```python
pattern = '.*?'.join(user_input)
regex = re.compile(pattern)
for parent, filenames in collections.iteritems():
    for fn in filenames:
        if ignore:
            match = regex.search(fn.lower())
        else:
            match = regex.search(fn)
        if match:
            if len(match.group(0)) < (len(keyword) + 5):
                the_path_of_file = os.path.join(parent, fn)
                # len(match.group(0)反应匹配的紧凑程度，match.start()反应匹配到的起始位置
                suggestions.append((len(match.group(0)), match.start(), the_path_of_file))
return [fn for _, _, fn in sorted(suggestions)]
```