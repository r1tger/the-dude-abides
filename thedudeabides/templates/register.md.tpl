---
title: "Register"
date: "{{ date }}"
---

{% if stats %}
|Notities           |Totaal                                |Gemiddeld                  |
|:------------------|-------------------------------------:|--------------------------:|
|Notities           |{{ '{:,}'.format(stats.nr_vertices) }}|n.v.t.                     |
|Relaties           |{{ '{:,}'.format(stats.nr_edges) }}   |{{ stats.avg_edges }}      |
|Minst verbonden    |{{ '{:,}'.format(stats.min_edges) }}  |n.v.t.                     |
|Meest verbonden    |{{ '{:,}'.format(stats.max_edges) }}  |n.v.t.                     |
|Aantal woorden     |{{ '{:,}'.format(stats.word_count) }} |{{ stats.avg_word_count }} |
|Ingangnotities     |{{ '{:,}'.format(stats.nr_entry) }}   |{{ stats.nr_entry_perc }}% |
|Uitgangnotities (Ω)|{{ '{:,}'.format(stats.nr_exit) }}    |{{ stats.nr_exit_perc }}%  |
|Lengte van paden   |                                      |{{ stats.avg_path_length }}|
{% endif %}

## Recent

{% if recent_notes|length == 0 %}Er zijn geen recent bijgewerkte notities.{% endif %}

{% for b, note in recent_notes %}
* {{ note|format_note(b, exit_notes) }}
{% endfor %}

{% for k, v in notes %}

## {{ k }}

{% for _, b, note, ref in v %}
* {{ note|format_note(b, exit_notes) }}
{% for n, text in ref %}
[{{ n.get_id() }}]({{ n.get_id() }}.html "{{ text|replace('"', '&quot;') }}"){% if not loop.last %}, {% endif %}

{% endfor %}
{% endfor %}
{% endfor %}
