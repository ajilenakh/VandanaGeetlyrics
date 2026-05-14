// Theme Toggle
function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "light" ? "dark" : "light";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
}

// Font Size Controls
function initFontSize() {
  const savedSize = localStorage.getItem("fontSize") || "medium";
  setFontSize(savedSize);
}

function setFontSize(size) {
  const sizes = {
    tiny: "14px",
    small: "16px",
    medium: "18px",
    large: "20px",
    extra_large: "22px",
  };
  document.documentElement.style.setProperty("--base-font-size", sizes[size]);
  localStorage.setItem("fontSize", size);
}

// Initialize on page load
document.addEventListener("DOMContentLoaded", () => {
  initFontSize();

  // Theme toggle button
  const themeToggle = document.getElementById("theme-toggle");
  if (themeToggle) {
    themeToggle.addEventListener("click", toggleTheme);
  }

  // Font size buttons
  const fontIncrease = document.getElementById("font-increase");
  const fontDecrease = document.getElementById("font-decrease");
  const fontReset = document.getElementById("font-reset");

  if (fontIncrease) {
    fontIncrease.addEventListener("click", () => {
      const currentSize = localStorage.getItem("fontSize") || "medium";
      const sizes = ["tiny", "small", "medium", "large", "extra_large"];
      const currentIndex = sizes.indexOf(currentSize);
      const nextIndex = Math.min(currentIndex + 1, sizes.length - 1);
      setFontSize(sizes[nextIndex]);
    });
  }

  if (fontDecrease) {
    fontDecrease.addEventListener("click", () => {
      const currentSize = localStorage.getItem("fontSize") || "medium";
      const sizes = ["tiny", "small", "medium", "large", "extra_large"];
      const currentIndex = sizes.indexOf(currentSize);
      const prevIndex = Math.max(currentIndex - 1, 0);
      setFontSize(sizes[prevIndex]);
    });
  }

  if (fontReset) {
    fontReset.addEventListener("click", () => {
      setFontSize("medium");
    });
  }

  // Remove no-transition class after initial load
  setTimeout(() => {
    document.body.classList.remove("no-transition");
  }, 100);

  // Register service worker
  if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
      navigator.serviceWorker.register("/sw.js").catch((err) => {
        console.log("ServiceWorker registration failed:", err);
      });
    });
  }

  // PWA Install Detection
  let deferredPrompt = null;

  window.addEventListener("beforeinstallprompt", (e) => {
    // Don't preventDefault - allows native banner + custom button
    deferredPrompt = e;
    const installBtn = document.getElementById("install-btn");
    if (installBtn) {
      installBtn.style.display = "block";
    }
  });

  // iOS detection - show manual install instructions
  const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && 
                navigator.maxTouchPoints > 1 && 
                !window.matchMedia('(display-mode: standalone)').matches;

  if (isIOS) {
    const hint = document.getElementById("ios-install-hint");
    if (hint) {
      hint.style.display = "block";
      // Auto-hide after 8 seconds
      setTimeout(() => {
        hint.style.display = "none";
      }, 8000);
    }
  }

  window.addEventListener("appinstalled", async () => {
    deferredPrompt = null;
    const installBtn = document.getElementById("install-btn");
    if (installBtn) {
      installBtn.style.display = "none";
    }
    // Trigger precaching of all songs
    if ("serviceWorker" in navigator) {
      try {
        const registration = await navigator.serviceWorker.ready;
        if (registration.active) {
          registration.active.postMessage({ type: "PRECACHE_ALL_SONGS" });
        }
      } catch (err) {
        console.log("[App] Could not trigger precaching:", err);
      }
    }
  });

  // Install button click handler
  const installBtn = document.getElementById("install-btn");
  if (installBtn) {
    installBtn.addEventListener("click", async () => {
      if (!deferredPrompt) return;
      deferredPrompt.prompt();
      const { outcome } = await deferredPrompt.userChoice;
      if (outcome === "accepted") {
        deferredPrompt = null;
        installBtn.style.display = "none";
        // Trigger precaching
        if ("serviceWorker" in navigator) {
          try {
            const registration = await navigator.serviceWorker.ready;
            if (registration.active) {
              registration.active.postMessage({ type: "PRECACHE_ALL_SONGS" });
            }
          } catch (err) {
            console.log("[App] Could not trigger precaching:", err);
          }
        }
      }
    });
  }
});
