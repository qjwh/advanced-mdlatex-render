# 前言

此项目根据MIT许可证获得许可。有关详细信息，请参阅[LICENSE](LICENSE)文件。

如果您觉得这个项目对您有帮助，请不要忘记点个Star，或者[赞助一下](https://afdian.com/a/qjwh_mingyueye)。

# 介绍

更高级的轻量 Markdown/LaTeX 网页渲染器。/ More Advanced Markdown/LaTeX Render.

## 为何选择本项目？

所有依赖项都集中在一个脚本内，初始化方便。

项目长期维护，有新功能建议请发 Issue，本人会尽快解决。

样式文件、加载依赖项脚本、主脚本分开，您可以将样式文件下载下来，然后自由发挥您的创意，定值出您自己的渲染器。

在原生的语法之外，还添加了以下新功能：
- 纯文本代码块内嵌 LaTeX 公式渲染。
- 非纯文本代码块的行号显示与鼠标悬停高亮本行。
- 代码块一键切换自动换行与一键复制。（感谢 feather 图标库对本项目的支持）
- 更多功能敬请期待...

## 准备工作

本渲染器的核心就在仓库文件夹的[main.css](resources/main.css)和[load.js](resources/load.js)文件。

在您的HTML代码中，只要先引用一下main.css：

```html
<link rel="stylesheet" type="text/css" href="https://cdn.jsdelivr.net/gh/qjwh/advanced-mdlatex-render@main/resources/main.css">
```

> 也可以使用`https://fastly.jsdelivr.net/gh/qjwh/advanced-mdlatex-render@main/resources/main.css`，应该访问会更快

还有load.js：

```html
<script src="https://cdn.jsdelivr.net/gh/qjwh/advanced-mdlatex-render@main/resources/load.js" crossorigin="anonymous"></script>
```

> 也可以使用`https://fastly.jsdelivr.net/gh/qjwh/advanced-mdlatex-render@main/resources/load.js`，应该访问会更快，但**千万不要使用`raw.githubusercontent.com`，会报错**。

> 为了加速渲染，这个脚本调用的是本仓库内每天更新一次的依赖资源内容，如果您需要使用最新的版本，但 JSDelivr 更新不及时，您可以将 load.js 换成 load-newest.js，此时便会访问原网站数据进行渲染。

就可以开始使用了。

## 开始编写

因为HTML加载资源是并行加载，所以您使用本项目进行渲染的时候，请在您的 JavaScript 代码外面加这样的代码片段：

```html
<script>
    resourcesLoaded.then(() => {
        // your code...
    });
</script>
```

本项目提供两个函数，`autoappend`和`gen`。前者是懒人党专用，后者则有更大的自由度。

具体而言，您需要先准备您的 Markdown/LaTeX 文本，假设您使用的变量名为`mdcontent`，那么您可以这么写：

```html
<script>
    resourcesLoaded.then(() => {
        autoappend(mdcontent);
    });
</script>
```

随后本项目会在您的网页的最后加上这个文本的渲染结果，并自动初始化交互。

如果您想要在您的网页的某个地方加上渲染结果，请使用：

```html
<script>
    resourcesLoaded.then(() => {
        // 生成 HTML 源码
        const renderedHTML = gen(mdcontent);
        // 把 renderedHTML 插入到您的网页内
        // your code...
        // 初始化交互
        init();
    });
</script>
```

**注意一定要写上`init();`这句话，否则您的网页上只会出现渲染结果，但无法交互。**

## 不想自己写代码？

本项目还提供了`gen.exe`（见 Release 界面），用法是在终端内定位到这个应用程序所在文件夹，然后输入以下指令：

```bash
gen.exe [您要渲染的.md文档] [输出.html路径]
```

随后本程序就会自动把`.md`内容渲染，然后输出到`.html`文件内，双击这个文件，就可以查看结果了！

首次打开可能会有几秒钟的延迟，如果在界面上方提示“资源加载失败”可以考虑使用 VPN，后面访问就很快了。
