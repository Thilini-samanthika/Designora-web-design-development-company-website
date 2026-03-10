document.addEventListener('DOMContentLoaded', function () {
    const navbar = document.getElementById('navbar');
    const navToggle = document.getElementById('nav-toggle');
    const navMenu = document.getElementById('nav-menu');
    const navLinks = document.querySelectorAll('.nav-link');
    const contactForm = document.getElementById('contact-form');
    const formMessage = document.getElementById('form-message');

    window.addEventListener('scroll', function () {
        if (window.scrollY > 50) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    });

    navToggle.addEventListener('click', function () {
        navMenu.classList.toggle('active');
        navToggle.classList.toggle('active');
    });

    navLinks.forEach(function (link) {
        link.addEventListener('click', function () {
            navMenu.classList.remove('active');
            navToggle.classList.remove('active');
        });
    });

    document.querySelectorAll('a[href^="#"]').forEach(function (anchor) {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                const offset = navbar.offsetHeight + 20;
                const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - offset;
                window.scrollTo({ top: targetPosition, behavior: 'smooth' });
            }
        });
    });

    const sections = document.querySelectorAll('section[id]');
    window.addEventListener('scroll', function () {
        const scrollY = window.pageYOffset;
        sections.forEach(function (section) {
            const sectionHeight = section.offsetHeight;
            const sectionTop = section.offsetTop - 200;
            const sectionId = section.getAttribute('id');
            if (scrollY > sectionTop && scrollY <= sectionTop + sectionHeight) {
                navLinks.forEach(function (link) {
                    link.classList.remove('active');
                    if (link.getAttribute('href') === '#' + sectionId) {
                        link.classList.add('active');
                    }
                });
            }
        });
    });

    contactForm.addEventListener('submit', function (e) {
        e.preventDefault();
        const btnText = contactForm.querySelector('.btn-text');
        const btnLoader = contactForm.querySelector('.btn-loader');
        const btnIcon = contactForm.querySelector('.fa-paper-plane');
        const submitBtn = contactForm.querySelector('button[type="submit"]');

        btnText.textContent = 'Sending...';
        btnLoader.style.display = 'inline-block';
        btnIcon.style.display = 'none';
        submitBtn.disabled = true;

        const data = {
            name: document.getElementById('name').value,
            email: document.getElementById('email').value,
            company: document.getElementById('company').value,
            message: document.getElementById('message').value
        };

        fetch('/contact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        })
        .then(function (response) { return response.json(); })
        .then(function (result) {
            formMessage.textContent = result.message;
            formMessage.className = 'form-message ' + (result.success ? 'success' : 'error');
            formMessage.style.display = 'block';
            if (result.success) {
                contactForm.reset();
            }
        })
        .catch(function () {
            formMessage.textContent = 'Something went wrong. Please try again later.';
            formMessage.className = 'form-message error';
            formMessage.style.display = 'block';
        })
        .finally(function () {
            btnText.textContent = 'Send Message';
            btnLoader.style.display = 'none';
            btnIcon.style.display = 'inline-block';
            submitBtn.disabled = false;
            setTimeout(function () {
                formMessage.style.display = 'none';
            }, 5000);
        });
    });

    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    const observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);

    document.querySelectorAll('.service-card, .portfolio-card, .process-card, .testimonial-card, .stat-card, .contact-info-card').forEach(function (el) {
        el.classList.add('animate-element');
        observer.observe(el);
    });

    const statNumbers = document.querySelectorAll('.stat-number');
    const statsObserver = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                const target = parseInt(entry.target.getAttribute('data-target'));
                animateCounter(entry.target, target);
                statsObserver.unobserve(entry.target);
            }
        });
    }, { threshold: 0.5 });

    statNumbers.forEach(function (num) {
        statsObserver.observe(num);
    });

    function animateCounter(element, target) {
        var current = 0;
        var duration = 2000;
        var step = target / (duration / 16);
        function update() {
            current += step;
            if (current >= target) {
                element.textContent = target;
                return;
            }
            element.textContent = Math.floor(current);
            requestAnimationFrame(update);
        }
        update();
    }
});
