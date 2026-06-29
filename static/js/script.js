document.addEventListener("DOMContentLoaded", function () {

    // ==========================
    // AOS Animation
    // ==========================
    if (typeof AOS !== "undefined") {
        AOS.init({
            duration: 700,
            once: true
        });
    }

    // ==========================
    // Dark Mode
    // ==========================
    const body = document.body;
    const themeToggle = document.getElementById("theme-toggle");

    if (localStorage.getItem("theme") === "dark") {
        body.classList.add("dark-mode");

        if (themeToggle) {
            themeToggle.innerHTML = "☀️";
        }
    }

    if (themeToggle) {

        themeToggle.addEventListener("click", function () {

            body.classList.toggle("dark-mode");

            if (body.classList.contains("dark-mode")) {

                localStorage.setItem("theme", "dark");
                themeToggle.innerHTML = "☀️";

            } else {

                localStorage.setItem("theme", "light");
                themeToggle.innerHTML = "🌙";

            }

        });

    }

    // ==========================
    // Add To Cart (AJAX)
    // ==========================
    document.querySelectorAll(".add-to-cart-btn").forEach(function (button) {

        button.addEventListener("click", function () {

            const url = this.dataset.url;
            const btn = this;

            fetch(url)
                .then(response => response.json())
                .then(data => {

                    if (data.cart_count !== undefined) {

                        const cartCount = document.getElementById("cart-count");

                        if (cartCount) {
                            cartCount.innerText = data.cart_count;
                        }

                        btn.innerHTML = "Added ✓";
                        btn.classList.add("added");

                        setTimeout(function () {
                            btn.innerHTML = "ADD";
                            btn.classList.remove("added");
                        }, 1000);

                    }

                })
                .catch(function (error) {
                    console.log(error);
                });

        });

    });

    // ==========================
    // Auto Hide Alerts
    // ==========================
    setTimeout(function () {

        document.querySelectorAll(".alert").forEach(function (alert) {

            alert.style.transition = "0.5s";
            alert.style.opacity = "0";

            setTimeout(function () {
                alert.remove();
            }, 500);

        });

    }, 3000);

});