<!DOCTYPE html>
<html lang="nl">
    <head>
        <meta charset="UTF-8"/>
        <title>{{ title }}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/milligram/1.4.1/milligram.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis-network.min.css">
        <link rel="stylesheet" href="main.css"/>
        <link href="/favicon.ico" rel="shortcut icon"/>
        <meta name="description" content="{{ title|e }}"/>
    </head>
    <body class="index">
        <nav class="navigation">
            <!--<a class="navigation-title" href="#">The Dude Abides</a>-->
            <ul class="navigation-list">
                <li class="navigation-item"><a class="navigation-link" href="/">Index</a></li>
                <li class="navigation-item"><a class="navigation-link" href="register.html">Register</a></li>
                <li class="navigation-item"><a class="navigation-link" href="groups.html">Groepen</a></li>
                <li class="navigation-item"><a class="navigation-link" href="search.html">Zoeken</a></li>
                <!--<li class="navigation-item"><a class="navigation-link" href="tags.html">Tags</a></li>-->
                <li class="navigation-item"><a class="navigation-link" href="https://sive.rs/books" target="_blank">Book notes&hellip;</a></li>
                <li class="navigation-item"><a class="navigation-link" href="https://rr.reuser.biz" target="_blank">OSINT&hellip;</a></li>
                <li class="navigation-item" id="spinner" style="display: none;">Loading</li>
            </ul>
        </nav>
        <div class="grid-container">
            <div class="grid">
                <div class="page" data-level="1" data-note="{{ ident }}">
                    <div class="content">
                        <h1>{% if display_id %}{{ ident }}. {% endif %}{{ title }}</h1>
                        {{ content }}
                    </div>
                    {% if display_graph %}
                    <div class="content">
                        <h2>Netwerk</h2>
                        <div class="network"></div>
                    </div>
                    <!-- Nodes/edges for network -->
                    <script type="text/json" class="nodes">
                        {{ nodes }}
                    </script>
                    <script type="text/json" class="edges">
                        {{ edges }}
                    </script>
                    {% endif %}
                </div>
            </div>
        </div>
    </body>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jquery/3.6.0/jquery.min.js" referrerpolicy="no-referrer"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/URI.js/1.19.7/URI.min.js" integrity="sha512-NhN7q/gDer3nrBNMxW5MSHNAxDMwKD4AvVj/ikQnrp0U2+PHJsxgHoE72ugplv1RWFwLADBiBXEPf/hVDXefpg==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis-network.min.js" integrity="sha512-GE9mKnPrTn2DY5AZuIC9yE6K4FF8T+9lsO7jwHn+RW9rEjnHzF/in0oGwlPzRwjhQ+oJiawmtfvleX+l6h5/cA==" crossorigin="anonymous" referrerpolicy="no-referrer"></script>
    <script src="main.js" type="text/javascript"></script>
</html>
