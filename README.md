# 前言

此项目根据MIT许可证获得许可。有关详细信息，请参阅[LICENSE](LICENSE)文件。

如果您觉得这个项目对您有帮助，请不要忘记点个 Star，或者[赞助一下](https://afdian.com/a/qjwh_mingyueye)。

# 介绍

更高级的轻量 Markdown/LaTeX 网页渲染器。/ More Advanced Markdown/LaTeX Render.

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
