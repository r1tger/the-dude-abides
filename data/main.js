/* Simplified from: https://github.com/jethrokuan/cortex */

let pages = [window.location.pathname];
let animationLength = 200;
let rows = [];

function stackNote(href, level) {
    level = Number(level) || pages.length;
    href = URI(href);
    uri = URI(window.location);
    stacks = [];
    if (uri.hasQuery("n")) {
        stacks = uri.query(true).n;
        if (!Array.isArray(stacks)) {
            stacks = [stacks];
        }
        stacks = stacks.slice(0, level - 1);
    }
    if (-1 != stacks.indexOf(href.path())) {
        // If href is already in stack, do not open again
        return false;
    }
    stacks.push(href.path());
    uri.setQuery("n", stacks);

    old_stacks = stacks.slice(0, level - 1);
    state = { stacks: old_stacks, level: level };
    window.history.pushState(state, "", uri.href());
    return true;
}

function unstackNotes(level) {
    let container = document.querySelector(".grid");
    let children = Array.prototype.slice.call(container.children);

    for (let i = level; i < pages.length; i++) {
        container.removeChild(children[i]);
    }
    pages = pages.slice(0, level);
}

function displayNote(href, text, level, animate=true) {
    //
    unstackNotes(level);
    let container = document.querySelector(".grid");
    let fragment = document.createElement("template");
    fragment.innerHTML = text;
    let element = fragment.content.querySelector(".page");
    container.appendChild(element);
    pages.push(URI(href).path());

    setTimeout(
        function (element, level) {
            element.dataset.level = level + 1;
            initializeLinks(element, level + 1);
            element.scrollIntoView();
            if (animate) {
                element.animate([{ opacity: 0 }, { opacity: 1 }], animationLength);
            }
        }.bind(null, element, level),
        10
    );
}

function fetchNotes(hrefs) {
    // number of ajax requests to wait for
    var count = hrefs.length;
    // results of individual requests get stuffed here
    var results = [];

    // Empty urls don't display anything
    hrefs.forEach(function(href, index) {
        const request = new Request(href);
        fetch(request)
            .then((response) => response.text())
            .then((text) => {
                results[index] = text;
                count = count - 1;
                if (0 === count) {
                    results.forEach(function(text, index) {
                        displayNote(hrefs[index], text, index + 1);
                    });
                }
            });
    });
}

function fetchNote(href, level, animate=true) {
    level = Number(level) || pages.length;

    const request = new Request(href);
    fetch(request)
        .then((response) => response.text())
        .then((text) => {
            // Render the note
            displayNote(href, text, level);
        });
}

function search(searchField) {
    if (!searchField)
        return;
    // Attach an event listener to the search field
    searchField.addEventListener("keyup", function (e) {
        if (e.ctrlKey && e.metaKey)
            return;
        e.preventDefault();

        // Filter value to search on
        token = this.value.toLowerCase();
        if (token.length < 3)
            token = 'f3b87388-984d-479b-bcec-31b67a2256fd';
        // Populate list of rows once (performance)
        if (0 == rows.length) {
            tbody = document.querySelector("#tokens");
            rows = Array.prototype.slice.call(tbody.querySelectorAll("tr"));
        }
        // Hide or show table row based on filter value
        rows.forEach(async function (tr) {
            tr.style.display = "none";
            if (tr.dataset.token.toLowerCase().indexOf(token) > -1)
                tr.style.display = "";
        });
    });
}

function initializeLinks(page, level) {
    level = level || pages.length;
    links = Array.prototype.slice.call(page.querySelectorAll("a"));
    links.forEach(async function (element) {
        var rawHref = element.getAttribute("href");
        element.dataset.level = level;
        if (
            rawHref &&
            !(
                rawHref.indexOf("http://") === 0 ||
                rawHref.indexOf("https://") === 0 ||
                rawHref.indexOf("#") === 0 ||
                rawHref.includes(".pdf") ||
                rawHref.includes(".svg")
            ) &&
            !rawHref.includes("n=")
        ) {
            if (-1 != pages.indexOf(rawHref)) {
                element.className = "highlight"
            }
            element.addEventListener("click", function (e) {
                if (!e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                    if (stackNote(element.href, this.dataset.level)) {
                        fetchNote(element.href, this.dataset.level, (animate=true));
                    } else {
                        // blink element
                        element.animate([{ opacity: 0 }, { opacity: 1 }], animationLength);
                    }
                }
            });
        }
    });
}

window.addEventListener("popstate", function (event) {
    // TODO: check state and pop pages if possible, rather than reloading.
    window.location = window.location; // this reloads the page.
});

window.onload = function () {
    initializeLinks(document.querySelector(".page"));
    search(document.querySelector("#search"));

    uri = URI(window.location);
    if (uri.hasQuery("n")) {
        stacks = uri.query(true).n;
        if (!Array.isArray(stacks)) {
            stacks = [stacks];
        }
        // Fetch all notes defined in the url
        fetchNotes(stacks);
    }
};
