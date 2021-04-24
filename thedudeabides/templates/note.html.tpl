<!DOCTYPE html>
<html lang="nl">
    <head>
        <meta charset="UTF-8"/>
        <title>{{ title }}</title>
        <link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto:300,300italic,700,700italic">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/normalize/8.0.1/normalize.css">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/milligram/1.4.1/milligram.css">
        <link rel="stylesheet" href="main.css"/>
        <link href="/favicon.ico" rel="shortcut icon"/>
        <meta name="description" content="{{ title|e }}"/>
    </head>
    <body class="index">
        <div class="grid-container">
            <div class="grid">
                <div class="page" data-level="1">
                    <div class="content">
                        <h1>{% if display_id %}{{ ident }}. {% endif %}{{ title }}</h1>
                        {{ content }}
                    </div>
                </div>
            </div>
        </div>
    </body>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/URI.js/1.19.6/URI.min.js"></script>
    <script src="main.js" type="text/javascript"></script>
</html>
