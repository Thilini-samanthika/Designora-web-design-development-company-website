// NAVBAR MOBILE TOGGLE
const navToggle = document.getElementById("nav-toggle");
const navMenu = document.getElementById("nav-menu");
const navLinks = document.querySelectorAll(".nav-link");
const navbar = document.getElementById("navbar");

if (navToggle) {
    navToggle.addEventListener("click", () => {
        navMenu.classList.toggle("active");
    });
}

navLinks.forEach(link => {
    link.addEventListener("click", () => {
        navMenu.classList.remove("active");
    });
});

// NAVBAR SCROLL EFFECT
window.addEventListener("scroll", () => {
    if (window.scrollY > 30) {
        navbar.classList.add("scrolled");
    } else {
        navbar.classList.remove("scrolled");
    }
});

// ACTIVE NAV LINK ON SCROLL
const sections = document.querySelectorAll("section[id]");

function setActiveLink() {
    let current = "";

    sections.forEach(section => {
        const sectionTop = section.offsetTop - 140;
        const sectionHeight = section.offsetHeight;

        if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
            current = section.getAttribute("id");
        }
    });

    navLinks.forEach(link => {
        link.classList.remove("active");
        if (link.getAttribute("href") === `#${current}`) {
            link.classList.add("active");
        }
    });
}

window.addEventListener("scroll", setActiveLink);
setActiveLink();

// REVEAL ANIMATION
const revealItems = document.querySelectorAll(".reveal");

const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("active");
        }
    });
}, {
    threshold: 0.15
});

revealItems.forEach(item => revealObserver.observe(item));

// TEAM CAROUSEL
const teamTrack = document.getElementById("teamTrack");
const teamPrev = document.getElementById("teamPrev");
const teamNext = document.getElementById("teamNext");
const teamDots = document.getElementById("teamDots");
const teamCarousel = document.getElementById("teamCarousel");

if (teamTrack && teamPrev && teamNext && teamDots && teamCarousel) {
    const cards = Array.from(teamTrack.children);
    let currentIndex = 0;
    let cardsPerView = getCardsPerView();
    let autoSlide;

    function getCardsPerView() {
        if (window.innerWidth <= 768) return 1;
        if (window.innerWidth <= 1024) return 2;
        return 3;
    }

    function getMaxIndex() {
        return Math.max(0, cards.length - cardsPerView);
    }

    function createDots() {
        teamDots.innerHTML = "";
        const pages = getMaxIndex() + 1;

        for (let i = 0; i < pages; i++) {
            const dot = document.createElement("button");
            dot.className = "team-dot";

            if (i === currentIndex) {
                dot.classList.add("active");
            }

            dot.addEventListener("click", () => {
                currentIndex = i;
                updateCarousel();
                restartAutoSlide();
            });

            teamDots.appendChild(dot);
        }
    }

    function updateActiveCenter() {
        cards.forEach(card => card.classList.remove("active-center"));

        for (let i = 0; i < cardsPerView; i++) {
            if (cards[currentIndex + i]) {
                cards[currentIndex + i].classList.add("active-center");
            }
        }
    }

    function updateCarousel() {
        cardsPerView = getCardsPerView();

        const gap = 24;
        const carouselWidth = teamCarousel.offsetWidth;
        const cardWidth = (carouselWidth - gap * (cardsPerView - 1)) / cardsPerView;
        const moveAmount = currentIndex * (cardWidth + gap);

        teamTrack.style.transform = `translateX(-${moveAmount}px)`;

        const dots = document.querySelectorAll(".team-dot");
        dots.forEach((dot, index) => {
            dot.classList.toggle("active", index === currentIndex);
        });

        updateActiveCenter();

        teamPrev.disabled = currentIndex === 0;
        teamNext.disabled = currentIndex === getMaxIndex();

        teamPrev.style.opacity = teamPrev.disabled ? "0.5" : "1";
        teamNext.style.opacity = teamNext.disabled ? "0.5" : "1";
        teamPrev.style.cursor = teamPrev.disabled ? "not-allowed" : "pointer";
        teamNext.style.cursor = teamNext.disabled ? "not-allowed" : "pointer";
    }

    function nextSlide() {
        if (currentIndex < getMaxIndex()) {
            currentIndex++;
            updateCarousel();
        }
    }

    function prevSlide() {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
        }
    }

    function startAutoSlide() {
        stopAutoSlide();

        autoSlide = setInterval(() => {
            if (currentIndex < getMaxIndex()) {
                currentIndex++;
            } else {
                currentIndex = 0;
            }

            updateCarousel();
        }, 3000);
    }

    function stopAutoSlide() {
        clearInterval(autoSlide);
    }

    function restartAutoSlide() {
        stopAutoSlide();
        startAutoSlide();
    }

    teamNext.addEventListener("click", () => {
        nextSlide();
        restartAutoSlide();
    });

    teamPrev.addEventListener("click", () => {
        prevSlide();
        restartAutoSlide();
    });

    teamCarousel.addEventListener("mouseenter", stopAutoSlide);
    teamCarousel.addEventListener("mouseleave", startAutoSlide);

    window.addEventListener("resize", () => {
        const newCardsPerView = getCardsPerView();

        if (newCardsPerView !== cardsPerView) {
            cardsPerView = newCardsPerView;
            currentIndex = Math.min(currentIndex, getMaxIndex());
            createDots();
        }

        updateCarousel();
    });

    createDots();
    updateCarousel();
    startAutoSlide();
}

// CONTACT FORM DEMO MESSAGE
const contactForm = document.getElementById("contact-form");
const formMessage = document.getElementById("form-message");

if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
        e.preventDefault();
        formMessage.textContent = "Your message has been sent successfully.";
        contactForm.reset();

        setTimeout(() => {
            formMessage.textContent = "";
        }, 3000);
    });
}
// SIGN IN FORM REDIRECT
const signinForm = document.getElementById("signin-form");

if (signinForm) {
    signinForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const email = document.getElementById("signin-email").value.trim();
        const password = document.getElementById("signin-password").value.trim();
        const msg = document.getElementById("signin-msg");

        if (!email || !password) {
            msg.textContent = "Please fill in email and password.";
            msg.style.color = "red";
            return;
        }

        msg.textContent = "Sign in successful. Redirecting...";
        msg.style.color = "lime";

        setTimeout(() => {
            window.location.href = "/";
        }, 1000);
    });
}

// SIGN UP FORM REDIRECT
const signupForm = document.getElementById("signup-form");

if (signupForm) {
    signupForm.addEventListener("submit", function (e) {
        e.preventDefault();

        const name = document.getElementById("signup-name").value.trim();
        const email = document.getElementById("signup-email").value.trim();
        const password = document.getElementById("signup-password").value.trim();
        const confirm = document.getElementById("signup-confirm").value.trim();
        const terms = document.getElementById("terms").checked;
        const msg = document.getElementById("signup-msg");

        if (!name || !email || !password || !confirm) {
            msg.textContent = "Please fill in all fields.";
            msg.style.color = "red";
            return;
        }

        if (password !== confirm) {
            msg.textContent = "Passwords do not match.";
            msg.style.color = "red";
            return;
        }

        if (!terms) {
            msg.textContent = "Please accept the terms.";
            msg.style.color = "red";
            return;
        }

        msg.textContent = "Account created successfully. Redirecting to Sign In...";
        msg.style.color = "lime";

        setTimeout(() => {
            window.location.href = "/signin";
        }, 1000);
    });
}