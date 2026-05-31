/* Static dashboard helper for Round 0. */

(function bootstrapDashboard() {
  const root = document.querySelector("[data-dashboard-ready]");
  if (!root) {
    return;
  }
  root.textContent = "ready";
})();
