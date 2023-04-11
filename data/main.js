//
rows = [];

/*
 */
function initialise(page) {
    // Create a network of associated notes
    network(page);
    // If a search box is found, add an event listener
    search(page);
    // Mark any links as already opened
    urls = $('.page').map(function(index, page) {
        return $(page).data('url');
    });
    $(page).find('a').each(async function(index, a) {
        if (-1 != $.inArray(URI(a.href).pathname(), urls))
            $(a).toggleClass('highlight');
    });
    // Render any texmath equations
    $(page).find('eq').each(function(index, eq) {
        katex.render(eq.textContent, eq);
    });
    // Scroll to the added page
    page.scrollIntoView(/*{behavior: 'smooth'}*/);
    page.animate([{ opacity: 0 }, { opacity: 1 }], 200);

    // Catch any onclick events on the page
    $(page).click(function(event) {
        try {
            url = URI(event.target.href);
            // Only process "internal" links with format: /234.html
            if (!/^\/(?:moc-)?[0-9]+\.html/.test(url.pathname()))
                return true;
        } catch {
            // No valid URL found
            return false;
        }
        event.preventDefault();
        // Check if page is already loaded
        pages = $('.page');
        has_url = $(pages).is(function(index, page) {
            return (url.pathname() == $(page).data('url'));
        });
        if (has_url)
            return false;
        $('.page').each(function(index, page) {

        });
        // Load the new page
        load(url, this);
    });
}

/* Create a new URL for use in events and history.
 */
function create_url(note) {
    return '/' + note + '.html';
}

/* Load a single or multiple URLs. If multiple URLs are provided, they're
 * loaded in order.
 */
function load(urls, currentPage) {
    urls = $.makeArray(urls);
    if (0 == urls.length) {
        notes = $.makeArray($('.page').map(function(i, page) {
            return create_url(page.dataset.note);
        }));
        notes.shift();
        // Update the address bar to reflect opened pages
        history.pushState([], '', URI().query({ note: notes }));
        return true;
    }

    url = urls.shift();
    $.ajax({url: url}).done(function(data) {
        // Delete all pages after this page
        if (currentPage)
            $(pages).slice($(pages).index(currentPage) + 1).remove();
        // Add page to the grid
        $('.grid').append($(data).find('.page'));
        page = $('.page').last()[0];
        $(page).data('url', url.pathname());
        // Initialise the new page
        initialise(page);
        // Load the remaining URLs
        load(urls);
    });
}

function network(page) {
    if (0 == $(page).find('.network').length)
        return false;
    // Render a directed graph using vis-network
    options = {
        autoResize: true,
        width: '100%',
        height: '100%',
        nodes: {
            shape: 'dot',
            size: 15,
            shadow: true
        },
        edges: {
            arrows: 'to'
        },
        physics: {
            forceAtlas2Based: {
                gravitationalConstant: -26,
                centralGravity: 0.005,
                springLength: 230,
                springConstant: 0.18,
            },
            maxVelocity: 146,
            solver: 'forceAtlas2Based',
            timestep: 0.35,
            stabilization: { iterations: 150 },
        },
    };
    nodes = JSON.parse($(page).find('.nodes').text());
    edges = JSON.parse($(page).find('.edges').text());
    var network = new vis.Network(
        $(page).find('.network')[0],
        {
            nodes: nodes,
            edges: edges
        },
        options
    );
    network.on('doubleClick', function(params) {
        if (0 == params.nodes.length)
            return;
        event = $.Event('click');
        event.target = { href: create_url(params.nodes[0]) };
        // Raise click event
        $(params.event.target).trigger(event);
    });
}

function search(page) {
    if (0 == $(page).find('#search').length)
        return;
    // Attach an event listener to the search field
    $(page).find('#search').keyup(function (e) {
        e.preventDefault();
        // Filter value to search on
        token = this.value.toLowerCase();
        if (token.length < 3)
            token = 'f3b87388-984d-479b-bcec-31b67a2256fd';
        if (0 == rows.length) {
            tbody = document.querySelector('#tokens');
            // rows = Array.prototype.slice.call(tbody.querySelectorAll('tr'));
            rows = $('#tokens').find('tr');
        }
        // Hide or show table row based on filter value
        rows.each(async function (index, tr) {
            // Do not use .hide() due to performance reasons
            tr.style.display = 'none';
            if (tr.dataset.token.toLowerCase().indexOf(token) > -1)
                tr.style.display = '';
        });
    });
}

/*
 */
$(document).ready(function() {
    // Show a spinner when loading pages
    $(document)
        .ajaxStart(function() { $('#spinner').show(); })
        .ajaxStop(function() { $('#spinner').hide(); });
    // Load any notes provided as part of the URL
    uri = URI();
    if (uri.hasQuery('note')) {
        notes = $.makeArray(uri.query(true).note);
        // Fetch all notes defined in the url
        load($(notes).map(function(index, url) { return URI(url); }));
    }
    // Initialise the first page
    initialise($('.page').first()[0]);
});

/* Someting happened to the history ...
 */
$(window).bind('popstate', function(event) {
    console.log('popstate: ' + URI());
    $('.grid').empty();
    // Load any notes provided as part of the URL
    uri = URI();
    if (uri.hasQuery('note')) {
        notes = $.makeArray(uri.query(true).note);
        // Fetch all notes defined in the url
        load($(notes).map(function(index, url) { return URI(url); }));
    }
});
