// 在脚本开头获取当前脚本路径
const currentScript = document.currentScript || (function() {
  const scripts = document.getElementsByTagName('script');
  return scripts[scripts.length - 1];
})();

// 资源列表（严格按顺序）
const resources = [
  // 第三方资源
  { type: 'script', url: 'https://unpkg.com/feather-icons' },
  { type: 'link'  , url: 'https://cdn.jsdelivr.net/npm/katex/dist/katex.min.css', attrs: { crossorigin: 'anonymous' } },
  { type: 'script', url: 'https://cdn.jsdelivr.net/npm/katex/dist/katex.min.js', attrs: { defer: true, crossorigin: 'anonymous' } },
  { type: 'script', url: 'https://cdn.jsdelivr.net/npm/katex/dist/contrib/auto-render.min.js', attrs: { defer: true, crossorigin: 'anonymous' } },
  { type: 'link'  , url: 'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release/build/styles/github-dark-dimmed.min.css' },
  { type: 'script', url: 'https://cdn.jsdelivr.net/gh/highlightjs/cdn-release/build/highlight.min.js' },
  { type: 'script', url: 'https://cdn.jsdelivr.net/npm/marked/marked.min.js' },
  { type: 'script', url: 'https://cdn.jsdelivr.net/npm/marked-footnote/dist/index.umd.js' },
  
  // 本地资源（放在最后）
  // { type: 'link', url: 'main.css' },
  { type: 'script', url: 'main.js' }
];

// 暴露全局的加载完成 Promise
window.resourcesLoaded = new Promise((resolve) => {
// 资源加载器函数
function loadResource(resource) {
  return new Promise((resolve, reject) => {
    // 更健壮的路径处理
    let absoluteURL;
    
    if (resource.url.startsWith('http') || resource.url.startsWith('//')) {
      // 已经是绝对路径
      absoluteURL = resource.url;
    } else {
      // 处理相对路径
      const basePath = currentScript ? currentScript.src : document.baseURI;
      absoluteURL = new URL(resource.url, basePath).href;
    }
    
    let element;
    
    if (resource.type === 'script') {
      element = document.createElement('script');
      element.src = absoluteURL;
      element.onload = resolve;
      element.onerror = reject;
    } else if (resource.type === 'link') {
      element = document.createElement('link');
      element.rel = 'stylesheet';
      element.href = absoluteURL;
      element.onload = resolve;
      element.onerror = reject;
    }

    // 设置额外属性
    if (resource.attrs) {
      Object.entries(resource.attrs).forEach(([key, value]) => {
        element.setAttribute(key, value);
      });
    }

    document.head.appendChild(element);
  });
}

// 主加载流程 - 严格按顺序加载
(async function initLoader() {
  try {
    // 按数组顺序逐个加载资源
    for (let i = 0; i < resources.length; i++) {
      const resource = resources[i];
      await loadResource(resource);
      console.log(`✅ [${i+1}/${resources.length}] 已加载: ${resource.url}`);
    }
    
    console.log('🎉 所有资源加载完成！');
    resolve(); // 解决全局 Promise
    
  } catch (error) {
    console.error('❌ 资源加载失败:', error);
    // 添加错误处理UI
    const errorDiv = document.createElement('div');
    errorDiv.style.cssText = `
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      background: #f8d7da;
      color: #721c24;
      padding: 15px;
      text-align: center;
      font-family: sans-serif;
      z-index: 10000;
      font-size: 16px;
      font-weight: bold;
      box-shadow: 0 2px 10px rgba(0,0,0,0.2);
    `;
    errorDiv.textContent = '资源加载失败，请刷新页面重试';
    document.body.prepend(errorDiv);
      
    // 即使失败也解决 Promise，防止页面完全阻塞
    resolve();
  }
})();
});
