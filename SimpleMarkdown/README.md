## SimpleMarkdown解析器

### 介绍
此小项目来源于《python基础教程》一书中最后的10个项目中的第一个项目。我借鉴项目中的一些优秀的分析方法，经过改编，编写了这个简易的markdown文件解析器。目前实现了解析标题、列表、代码块、图片链接、超链接、段落等常用的语法。
针对这个程序，可以列出如下一些模块：
* **分析器**：增加一个对象用于读取文本，并管理其他的类
* **规则**：可以为每种类型的块制定一条规则，规则能够检测出块的类型并进行相应的格式化
* **过滤器**：使用过滤器来包装一些处理内嵌元素的正则表达式
* **处理程序**：分析器使用处理程序来产生输出。每个处理程序能产生一种不同类型的标记。

### 使用方法
```bash
python simplemarkdown.py < test_input.txt > test_output.html
```

### 难点
此项目的难点在于如何解析列表和代码块，因为列表和代码块往往分布在多行，需要判断列表和代码块什么时候开始、什么时候结束，而且有时候列表中还会出现换行的情况。
我采取的方法是先将列表内容或者代码块内容塞进一个列表中，然后进行统一处理，而不是采用一行一行的方式进行处理。例如，下面是处理代码块的代码
```python
class CodeRule(object):
    type = 'code'
    inside = False
    content = []

    def condition(self, element):
        if element.startswith("```"):
            self.inside = not self.inside
            return True
        if self.inside:
            return True

    def action(self, element, handler, *args):
        if self.condition(element):
            self.content.append(element)
            return 'code'
        if self.content:
            handler.start(self.type)
            for line in self.content[1:-1]:
                handler.feed(line)
            handler.end(self.type)
            self.content = []
```

### 学习到什么
此项目让我对程序模块化有了更深的认识，程序模块化对于程序是否有良好的可扩展性具有重要意义。当程序越来越复杂的时候，往往需要进行一些抽象来使得程序更加可控。