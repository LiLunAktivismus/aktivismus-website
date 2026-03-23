// header-loader.js - 异步注入核心脚本 (v3.2 - 移动端折叠菜单优化)
(function() {
    const cacheKey = 'aktivismus_layout_cache';
    const layoutUrl = '/header.html'; 
    const workerApiUrl = 'https://contact-email-via-resend.lilun.workers.dev';

    const modalHTML = `
    <div id="contactModal" class="contact-modal">
        <div class="modal-content">
            <span class="close-modal">&times;</span>
            <h2>Get in Touch</h2>
            <form id="activismusContactForm" class="contact-form">
                <input type="text" id="form_name" placeholder="Full Name *" required>
                <input type="email" id="form_email" placeholder="Work Email *" required>
                <input type="text" id="form_company" placeholder="Company Name *" required>
                <select id="form_region" required>
                    <option value="" disabled selected>Select Region *</option>
                    <option value="USA">USA</option><option value="Germany">Germany</option>
                    <option value="France">France</option><option value="Spain">Spain</option>
                    <option value="Italy">Italy</option><option value="China">China</option>
                    <option value="SEA">SEA</option>
                </select>
                <select id="form_service" required>
                    <option value="" disabled selected>Select Service *</option>
                    <option value="AI Content Production">AI Content Production</option>
                    <option value="Matrix Distribution">Matrix Distribution</option>
                    <option value="Others">Others</option>
                </select>
                <textarea id="form_message" rows="4" placeholder="How can we help? *" required></textarea>
                <button type="submit" class="submit-btn">SEND MESSAGE</button>
                <div id="formResponse" style="margin-top:15px; font-size:0.9rem; text-align:center;"></div>
            </form>
        </div>
    </div>`;

    function inject(html) {
        if (!html) return;
        const temp = document.createElement('div');
        temp.innerHTML = html;
        const headerContent = temp.querySelector('#layout-header-container');
        const footerContent = temp.querySelector('#layout-footer-container');

        const performInjection = () => {
            if (headerContent && !document.querySelector('header')) {
                document.body.insertAdjacentHTML('afterbegin', headerContent.innerHTML);
            }
            if (footerContent && !document.querySelector('.global-footer')) {
                document.body.insertAdjacentHTML('beforeend', footerContent.innerHTML);
            }
            if (!document.getElementById('contactModal')) {
                document.body.insertAdjacentHTML('beforeend', modalHTML);
            }
            initializeNavigation();
            initializeContactForm();
            highlightCurrentPage();
        };

        if (document.readyState === 'loading') {
            window.addEventListener('DOMContentLoaded', performInjection);
        } else {
            performInjection();
        }
    }

    const cached = localStorage.getItem(cacheKey);
    if (cached) {
        if (document.body) inject(cached);
        else window.addEventListener('DOMContentLoaded', () => inject(cached));
    }

    fetch(layoutUrl).then(r => r.text()).then(latest => {
        if (latest !== cached) {
            localStorage.setItem(cacheKey, latest);
            if (!cached) inject(latest);
            else {
                const h = document.querySelector('header'); if (h) h.remove();
                const f = document.querySelector('.global-footer'); if (f) f.remove();
                const m = document.getElementById('contactModal'); if (m) m.remove();
                inject(latest);
            }
        }
    }).catch(err => console.error("Layout fetch failed:", err));

    function initializeNavigation() {
        const toggle = document.getElementById('menu-toggle');
        const nav = document.getElementById('main-nav');
        if (!toggle || !nav) return;

        // 1. 主菜单开关
        toggle.onclick = (e) => {
            e.preventDefault();
            toggle.classList.toggle('open');
            nav.classList.toggle('open');
            // 菜单打开时锁定滚动
            document.body.style.overflow = nav.classList.contains('open') ? 'hidden' : '';
        };

        // 2. 移动端子菜单折叠逻辑
        const parentItems = nav.querySelectorAll('ul > li');
        parentItems.forEach(item => {
            const link = item.querySelector('a');
            const hasSubmenu = item.querySelector('.submenu');

            if (hasSubmenu && window.innerWidth <= 768) {
                link.onclick = (e) => {
                    // 只有在点击父级链接时切换折叠，阻止跳转
                    e.preventDefault();
                    
                    // 关闭其他已打开的子菜单（手风琴效果）
                    parentItems.forEach(otherItem => {
                        if (otherItem !== item) otherItem.classList.remove('open');
                    });

                    item.classList.toggle('open');
                };
            }
        });

        window.onscroll = () => {
            const h = document.querySelector('header');
            if (h) h.style.padding = window.scrollY > 50 ? "15px 5%" : "25px 5%";
        };
    }

    function initializeContactForm() {
        const modal = document.getElementById('contactModal');
        const form = document.getElementById('activismusContactForm');
        const resDiv = document.getElementById('formResponse');
        if (!modal || !form) return;
        modal.querySelector('.close-modal').onclick = () => modal.classList.remove('active');
        window.addEventListener('click', (e) => { if (e.target == modal) modal.classList.remove('active'); });

        form.onsubmit = async (e) => {
            e.preventDefault();
            resDiv.innerHTML = "Sending...";
            try {
                const res = await fetch(workerApiUrl, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        name: document.getElementById('form_name').value,
                        email: document.getElementById('form_email').value,
                        company: document.getElementById('form_company').value,
                        region: document.getElementById('form_region').value,
                        service: document.getElementById('form_service').value,
                        message: document.getElementById('form_message').value
                    })
                });
                if (res.ok) {
                    resDiv.style.color = "#00EEFF";
                    resDiv.innerHTML = "Success! We'll talk soon.";
                    form.reset();
                    setTimeout(() => modal.classList.remove('active'), 3000);
                } else { throw new Error(); }
            } catch (err) {
                resDiv.style.color = "#ff4444";
                resDiv.innerHTML = "Error. Please try again.";
            }
        };
        window.openContactForm = () => modal.classList.add('active');
    }

    function highlightCurrentPage() {
        const path = window.location.pathname;
        document.querySelectorAll('nav a').forEach(link => {
            const h = link.getAttribute('href');
            if (h && h !== '/' && path.includes(h.replace('.html', '').replace('/index.html', ''))) {
                link.classList.add('active');
            }
        });
    }
})();
