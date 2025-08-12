function gen(markdownContent) {
    // 创建虚拟容器并设置id为"content"
    const virtualContainer = document.createElement('div');
    virtualContainer.id = 'content';

    // 保护公式块内的反斜杠（防止Marked.js转义）
    const protectedMarkdown = markdownContent.replace(/(\${2}[\s\S]*?\${2})/g, function(match) {
        return match.replace(/\\\\/g, '\\\\\\\\');
    });

    // 配置Marked.js
    marked.setOptions({
        highlight: function(code, lang) {
            const language = lang || 'plaintext';
            if (hljs.getLanguage(language)) {
                try {
                    return hljs.highlight(code, { language }).value;
                } catch (e) {
                    console.error(e);
                }
            }
            return hljs.highlightAuto(code).value;
        }
    });
    marked.use(markedFootnote());

    // 渲染Markdown
    virtualContainer.innerHTML = marked.parse(protectedMarkdown);

    // 删除原有的 renderCodeblockMath 函数
    // 添加新的处理函数
    function generateShortId() {
        // console.log(Math.random().toString(36).substring(2, 12));
        // + Date.now().toString(36).substring(4)
        return Math.random().toString(36).substring(2, 12);
    }
    function processCodeBlockWithFormulas(container) {
        container.querySelectorAll('pre code').forEach((block) => {
            // 保存原始代码和行号处理
            let rawCode = block.textContent;
            // 排除末尾换行（空代码除外）
            if (rawCode !== '\n' && rawCode.endsWith('\n')) {
                const matches = rawCode.match(/\n+$/);
                if (matches) {
                    const trailingNewlines = matches[0].length;
                    rawCode = rawCode.slice(0, -trailingNewlines);
                }
            }
            // console.log(rawCode);
            block.dataset.raw = rawCode.replace(/\\\\\\\\/g, '\\\\');
            
            // 判断是否有明确语言标识（排除hljs自动识别）
            const hasExplicitLanguage = block.closest('pre').querySelector('code[class*="language-"]') && 
                                        !block.classList.contains('language-plaintext');
            
            // 公式处理
            const formulaMap = new Map();
            
            const inlineRegex = /\$(.*?)\$/g;
            const blockRegex = /\$\$(.*?)\$\$/gs;
            
            let processedCode = rawCode;
            
            if (!hasExplicitLanguage) {
                processedCode = rawCode.replace(blockRegex, (match, formula) => {
                    const placeholder = `__KATEXBLOCK${generateShortId()}__`;
                    formulaMap.set(placeholder, {
                        formula: formula.replace(/\\\\\\\\/g, '\\\\'),
                        displayMode: true
                    });
                    return placeholder;
                });
                
                processedCode = processedCode.replace(inlineRegex, (match, formula) => {
                    const placeholder = `__KATEXINLINE${generateShortId()}__`;
                    formulaMap.set(placeholder, {
                        formula: formula.replace(/\\\\\\\\/g, '\\\\'),
                        displayMode: false
                    });
                    return placeholder;
                });
            }
            
            block.textContent = processedCode;
            
            hljs.highlightElement(block);
            
            let finalHTML = block.innerHTML;
            
            // 添加行号结构（仅针对有语言标识的代码块）
            if (hasExplicitLanguage) {
                const preBlock = block.closest('pre');
                const lines = finalHTML.split('\n');
                if (lines[lines.length - 1] === '') lines.pop();
                
                const codeContent = document.createElement('div');
                codeContent.className = 'code-content';
                
                const codeLines = document.createElement('div');
                codeLines.className = 'code-lines';
                
                // console.log(lines);
                lines.forEach((lineHtml, index) => {
                    // console.log(lineHtml);
                    // console.log(index);
                    const line = document.createElement('div');
                    line.className = 'line';
                    line.dataset.lineNumber = index + 1;
                    
                    const lineNum = document.createElement('div');
                    lineNum.className = 'line-number';
                    lineNum.textContent = index + 1;
                    line.appendChild(lineNum);
                    
                    // console.log(formulaMap);
                    formulaMap.forEach((value, placeholder) => {
                        // console.log(value);
                        // console.log(placeholder);
                        let rendered = katex.renderToString(value.formula, {
                            throwOnError: false,
                            displayMode: value.displayMode
                        });
                        // console.log(lineHtml.split(placeholder));
                        lineHtml = lineHtml.split(placeholder).join(rendered);
                        // console.log("---");
                        // console.log(lineHtml);
                    });
                    
                    const lineCode = document.createElement('div');
                    lineCode.className = 'line-code';
                    lineCode.innerHTML = lineHtml || ' ';
                    line.appendChild(lineCode);
                    
                    codeLines.appendChild(line);
                });
                
                codeContent.appendChild(codeLines);
                
                const wrapper = document.createElement('div');
                wrapper.className = 'code-block-wrapper';
                wrapper.appendChild(codeContent);
                wrapper.dataset.raw = rawCode;
                
                preBlock.replaceWith(wrapper);
            }else{
                formulaMap.forEach((value, placeholder) => {
                    // console.log(value);
                    // console.log(placeholder);
                    let rendered = katex.renderToString(value.formula, {
                        throwOnError: false,
                        displayMode: value.displayMode
                    });
                    // console.log(finalHTML.split(placeholder));
                    finalHTML = finalHTML.split(placeholder).join(rendered);
                    // console.log("---");
                    // console.log(finalHTML);
                });
                // console.log("***");
                // console.log(finalHTML);
                
                block.innerHTML = finalHTML;
                // console.log(block.innerHTML);
            }
        });
    }

    // 添加代码操作按钮到所有代码块
    function addCodeActions(container) {
        container.querySelectorAll('pre').forEach((preBlock) => {
            // 检查是否已有操作按钮
            if (preBlock.querySelector('.code-actions')) return;
            
            const container = document.createElement('div');
            container.className = 'code-actions';
            
            // 创建自动换行按钮
            const wrapBtn = document.createElement('button');
            wrapBtn.className = 'wrap-btn';
            wrapBtn.title = '自动换行';
            wrapBtn.innerHTML = '<i data-feather="align-left"></i>';
            container.appendChild(wrapBtn);
            
            // 创建复制按钮
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.title = '复制内容';
            copyBtn.innerHTML = '<i data-feather="copy"></i>';
            container.appendChild(copyBtn);
            
            preBlock.appendChild(container);
        });
        container.querySelectorAll('div').forEach((preBlock) => {
            // 检查是否已有操作按钮
            if (preBlock.querySelector('.code-actions')) return;
            // 检查是否是代码片段
            if (!preBlock.querySelector('.code-content')) return;
            
            const container = document.createElement('div');
            container.className = 'code-actions';
            
            // 创建自动换行按钮
            const wrapBtn = document.createElement('button');
            wrapBtn.className = 'wrap-btn-div';
            wrapBtn.title = '自动换行';
            wrapBtn.innerHTML = '<i data-feather="align-left"></i>';
            container.appendChild(wrapBtn);
            
            // 创建复制按钮
            const copyBtn = document.createElement('button');
            copyBtn.className = 'copy-btn';
            copyBtn.title = '复制内容';
            copyBtn.innerHTML = '<i data-feather="copy"></i>';
            container.appendChild(copyBtn);
            
            preBlock.appendChild(container);
        });
        feather.replace();
    }

    // 先处理代码块内的公式
    processCodeBlockWithFormulas(virtualContainer);

    // 添加代码操作按钮
    addCodeActions(virtualContainer);

    // 渲染页面中的LaTeX公式
    renderMathInElement(virtualContainer, {
        delimiters: [
            {left: '$$', right: '$$', display: true},
            {left: '$', right: '$', display: false}
        ],
        throwOnError: false,
        ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"], // 忽略代码块
        ignoredClasses: ["code-block-wrapper"] // 忽略有语言标识的代码块
    });

    // 添加：修改脚注标题为"脚注"
    const footnotesHeading = virtualContainer.querySelector('.footnotes h2');
    if (footnotesHeading && footnotesHeading.textContent === 'Footnotes') {
        footnotesHeading.textContent = '脚注';
    }

    // 返回包含在<div id="content">中的完整HTML
    return virtualContainer.outerHTML;
}

// 在页面插入渲染结果后调用此函数，否则将无法交互
function init() {
    // 处理复制功能
    function setupCopyButtons() {
        document.addEventListener('click', function(e) {
            if (e.target.closest('.copy-btn')) {
                const button = e.target.closest('.copy-btn');
                const wrapper = button.closest('.code-block-wrapper');
                let rawText = '';
                
                if (wrapper && wrapper.dataset.raw) {
                    // 从包装容器获取原始代码
                    rawText = wrapper.dataset.raw;
                } else {
                    // 回退到从代码块获取
                    const codeBlock = button.closest('pre').querySelector('code');
                    if (codeBlock) {
                        rawText = codeBlock.dataset.raw || codeBlock.textContent;
                    }
                }
                
                // 获取原始代码（未渲染的原始文本）
                rawText = rawText.replace(/\n$/, ''); // 去除尾部换行
                
                navigator.clipboard.writeText(rawText).then(() => {
                    // 复制成功反馈
                    button.classList.add('copied');
                    button.innerHTML = '<i data-feather="check"></i>';
                    feather.replace();
                    
                    setTimeout(() => {
                        button.classList.remove('copied');
                        button.innerHTML = '<i data-feather="copy"></i>';
                        feather.replace();
                    }, 2000);
                }).catch(err => {
                    console.error('复制失败:', err);
                });
            }
        });
    }
    // 处理自动换行功能
    function setupWrapButtons() {
        document.addEventListener('click', function(e) {
            if (e.target.closest('.wrap-btn')) {
                const button = e.target.closest('.wrap-btn');
                const preBlock = button.closest('pre');
                preBlock.classList.toggle('wrap-code');
                button.classList.toggle('active');
            }else if (e.target.closest('.wrap-btn-div')) {
                const button = e.target.closest('.wrap-btn-div');
                const wrapper = button.closest('.code-block-wrapper');
                if (wrapper) {
                    const codeContent = wrapper.querySelector('.code-content');
                    if (codeContent) {
                        codeContent.classList.toggle('wrap-lines');
                        button.classList.toggle('active');
                    }
                }
            }
        });
    }

    // 修改setupLineHighlight函数
    function setupLineHighlight() {
        document.querySelectorAll('.code-content').forEach(content => {
            content.addEventListener('mouseover', (e) => {
                const line = e.target.closest('.line');
                if (line) {
                    // 移除其他高亮
                    content.querySelectorAll('.line').forEach(l => {
                        l.classList.remove('highlight');
                    });
                    // 添加当前高亮
                    line.classList.add('highlight');
                }
            });
            
            content.addEventListener('mouseout', (e) => {
                const line = e.target.closest('.line');
                if (line) {
                    line.classList.remove('highlight');
                }
            });
        });
    }

    setupCopyButtons();
    setupWrapButtons();
    setupLineHighlight();

    feather.replace();
}

function autoappend (markdownContent) {
    const renderedHTML = gen(markdownContent);
    document.body.insertAdjacentHTML('beforeend', renderedHTML);
    init();
}
