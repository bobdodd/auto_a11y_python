/**
 * Progressive enhancements for the public frontend.
 * All enhancements are opt-in via data-enhance attributes.
 * Pages work fully without JavaScript.
 */

(function () {
    "use strict";

    var liveRegion = document.getElementById("live-region");

    function announce(message) {
        if (liveRegion) {
            liveRegion.textContent = message;
        }
    }

    // -------------------------------------------------------
    // Accordion enhancement
    // -------------------------------------------------------
    function initAccordions() {
        var accordions = document.querySelectorAll('[data-enhance="accordion"]');

        accordions.forEach(function (accordion) {
            var triggers = accordion.querySelectorAll(".accordion-trigger");

            // Collapse all panels except the first
            triggers.forEach(function (trigger, index) {
                var panelId = trigger.getAttribute("aria-controls");
                var panel = document.getElementById(panelId);
                if (!panel) return;

                if (index > 0) {
                    trigger.setAttribute("aria-expanded", "false");
                    panel.hidden = true;
                } else {
                    trigger.setAttribute("aria-expanded", "true");
                    panel.hidden = false;
                }

                trigger.addEventListener("click", function () {
                    var expanded = trigger.getAttribute("aria-expanded") === "true";
                    trigger.setAttribute("aria-expanded", String(!expanded));
                    panel.hidden = expanded;
                });
            });
        });
    }

    // -------------------------------------------------------
    // Sortable table enhancement
    // -------------------------------------------------------
    function initSortableTables() {
        var tables = document.querySelectorAll('[data-enhance="sortable"]');

        tables.forEach(function (table) {
            var tbody = table.querySelector("tbody");
            if (!tbody) return;

            var rows = tbody.querySelectorAll("tr");
            // Only enhance small tables client-side
            if (rows.length === 0 || rows.length >= 100) return;

            var sortLinks = table.querySelectorAll("thead .sort-link");

            sortLinks.forEach(function (link) {
                link.addEventListener("click", function (e) {
                    e.preventDefault();

                    var th = link.closest("th");
                    var headerRow = th.parentElement;
                    var headers = Array.from(headerRow.children);
                    var colIndex = headers.indexOf(th);

                    // Determine sort direction
                    var currentSort = th.getAttribute("aria-sort");
                    var direction =
                        currentSort === "ascending" ? "descending" : "ascending";

                    // Clear aria-sort from all headers
                    headers.forEach(function (h) {
                        h.removeAttribute("aria-sort");
                    });
                    th.setAttribute("aria-sort", direction);

                    // Sort rows
                    var rowsArray = Array.from(tbody.querySelectorAll("tr"));
                    rowsArray.sort(function (a, b) {
                        var aText = a.children[colIndex]
                            ? a.children[colIndex].textContent.trim()
                            : "";
                        var bText = b.children[colIndex]
                            ? b.children[colIndex].textContent.trim()
                            : "";

                        // Try numeric comparison
                        var aNum = parseFloat(aText);
                        var bNum = parseFloat(bText);
                        if (!isNaN(aNum) && !isNaN(bNum)) {
                            return direction === "ascending"
                                ? aNum - bNum
                                : bNum - aNum;
                        }

                        // String comparison
                        var cmp = aText.localeCompare(bText, undefined, {
                            sensitivity: "base",
                        });
                        return direction === "ascending" ? cmp : -cmp;
                    });

                    // Re-append sorted rows
                    rowsArray.forEach(function (row) {
                        tbody.appendChild(row);
                    });

                    // Announce to screen readers
                    var columnName = link.textContent.trim();
                    var dirLabel =
                        direction === "ascending" ? "ascending" : "descending";
                    announce("Sorted by " + columnName + ", " + dirLabel);
                });
            });
        });
    }

    // -------------------------------------------------------
    // Init on DOMContentLoaded
    // -------------------------------------------------------
    document.addEventListener("DOMContentLoaded", function () {
        initAccordions();
        initSortableTables();
    });
})();
