(function bootstrapDashboard() {
  const root = document.querySelector("[data-dashboard-ready]");
  if (!root) {
    return;
  }
  root.setAttribute("data-ui-ready", "true");

  const cards = Array.from(document.querySelectorAll(".repo-card"));
  const priorityFilter = document.getElementById("filter-priority");
  const lifecycleFilter = document.getElementById("filter-lifecycle");
  const agentFilter = document.getElementById("filter-agent");

  function applyFilters() {
    const priority = priorityFilter ? priorityFilter.value : "all";
    const lifecycle = lifecycleFilter ? lifecycleFilter.value : "all";
    const agent = agentFilter ? agentFilter.value : "all";

    cards.forEach((card) => {
      const matchPriority = priority === "all" || card.dataset.priority === priority;
      const matchLifecycle = lifecycle === "all" || card.dataset.lifecycle === lifecycle;
      const matchAgent = agent === "all" || card.dataset.agent === agent;
      card.hidden = !(matchPriority && matchLifecycle && matchAgent);
    });
  }

  [priorityFilter, lifecycleFilter, agentFilter].forEach((el) => {
    if (el) {
      el.addEventListener("change", applyFilters);
    }
  });

  document.querySelectorAll(".copy-prompt").forEach((button) => {
    button.addEventListener("click", async () => {
      const text = button.getAttribute("data-prompt") || "";
      try {
        await navigator.clipboard.writeText(text);
        button.textContent = "已复制";
        setTimeout(() => {
          button.textContent = "复制 Prompt";
        }, 1500);
      } catch (_err) {
        button.textContent = "复制失败";
      }
    });
  });
})();
