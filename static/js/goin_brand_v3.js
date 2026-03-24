(function () {
    const state = {
        activeTab: "look",
        liked: {},
        gestureStartX: 0,
        gestureStartY: 0
    };

    function switchTab(next) {
        state.activeTab = next;
        document.querySelectorAll("[data-tab]").forEach((el) => {
            el.classList.toggle("active", el.getAttribute("data-tab") === next);
        });
        document.querySelectorAll("[data-module]").forEach((el) => {
            el.classList.toggle("hidden", el.getAttribute("data-module") !== next);
        });
    }

    function setLoading(containerId, duration) {
        const node = document.getElementById(containerId);
        if (!node) return;
        node.classList.remove("hidden");
        setTimeout(() => node.classList.add("hidden"), duration || 480);
    }

    function bindLikeButtons() {
        document.querySelectorAll("[data-like-id]").forEach((btn) => {
            btn.addEventListener("click", function () {
                const id = btn.getAttribute("data-like-id");
                const icon = btn.querySelector(".like-icon");
                const text = btn.querySelector(".like-count");
                const current = parseInt(text.textContent, 10) || 0;
                const liked = !state.liked[id];
                state.liked[id] = liked;
                text.textContent = liked ? current + 1 : Math.max(0, current - 1);
                icon.textContent = liked ? "❤️" : "🤍";
                icon.classList.add("g-like-pop");
                setTimeout(() => icon.classList.remove("g-like-pop"), 320);
            });
        });
    }

    function bindTabButtons() {
        document.querySelectorAll("[data-tab]").forEach((tab) => {
            tab.addEventListener("click", () => switchTab(tab.getAttribute("data-tab")));
        });
    }

    function bindGestures() {
        const area = document.getElementById("gestureArea");
        if (!area) return;
        area.addEventListener("touchstart", (e) => {
            const t = e.changedTouches[0];
            state.gestureStartX = t.clientX;
            state.gestureStartY = t.clientY;
        });
        area.addEventListener("touchend", (e) => {
            const t = e.changedTouches[0];
            const dx = t.clientX - state.gestureStartX;
            const dy = t.clientY - state.gestureStartY;
            if (Math.abs(dx) < 48 || Math.abs(dx) < Math.abs(dy)) return;
            const order = ["look", "in", "stroll"];
            const idx = order.indexOf(state.activeTab);
            const next = dx < 0 ? Math.min(order.length - 1, idx + 1) : Math.max(0, idx - 1);
            switchTab(order[next]);
        });
    }

    function bindQuickActions() {
        document.querySelectorAll("[data-toast]").forEach((btn) => {
            btn.addEventListener("click", () => {
                const text = btn.getAttribute("data-toast") || "操作成功";
                showToast(text);
            });
        });
    }

    function showToast(text) {
        let toast = document.getElementById("gToast");
        if (!toast) return;
        toast.textContent = text;
        toast.classList.remove("hidden");
        setTimeout(() => toast.classList.add("hidden"), 1200);
    }

    window.GoInBrand = {
        switchTab,
        setLoading,
        showToast
    };

    document.addEventListener("DOMContentLoaded", function () {
        bindTabButtons();
        bindLikeButtons();
        bindGestures();
        bindQuickActions();
    });
})();
