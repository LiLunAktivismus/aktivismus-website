// header-loader.js
document.addEventListener("DOMContentLoaded", function() {
    // 1. 加载 Header HTML
    fetch('/header.html')
        .then(response => response.text())
        .then(data => {
            document.body.insertAdjacentHTML('afterbegin', data);
            initializeNavigation();
            highlightCurrentPage();
        })
        .catch(error => console.error('Error loading header:', error));

    // 2. 初始化导航交互 (汉堡菜单、滚动效果等)
    function initializeNavigation() {
        const menuToggle = document.getElementById('menu-toggle');
        const mainNav = document.getElementById('main-nav');

        if (menuToggle && mainNav) {
            menuToggle.addEventListener('click', function() {
                this.classList.toggle('open');
                mainNav.classList.toggle('open');
            });
        }

        // 滚动时 Header 变色
        window.addEventListener('scroll', function() {
            const header = document.querySelector('header');
            if (window.scrollY > 50) {
                header.style.background = "rgba(13, 13, 13, 0.98)";
                header.style.padding = "15px 5%";
            } else {
                header.style.background = "rgba(19, 19, 19, 0.95)";
                header.style.padding = "25px 5%";
            }
        });
    }

    // 3. 自动高亮当前页面的导航项
    function highlightCurrentPage() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('nav a');

        navLinks.forEach(link => {
            const linkPath = link.getAttribute('href');
            // 如果是首页
            if (currentPath === "/" || currentPath === "/index.html") {
                if (linkPath === "/" || linkPath === "#hero") {
                    link.classList.add('active');
                }
            } 
            // 如果是子页面，匹配路径
            else if (linkPath !== "/" && currentPath.includes(linkPath.replace('.html', ''))) {
                link.classList.add('active');
            }
        });
    }
});
