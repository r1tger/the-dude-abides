<!DOCTYPE html>
<html lang="nl">
    <head>
        <meta charset="UTF-8"/>
        <title>{{ title }}</title>
        <link rel="stylesheet" href="https://unpkg.com/wingcss"/>
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
    <script src="https://unpkg.com/urijs@1"></script>
    <script src="main.js" type="text/javascript"></script>
</html>
