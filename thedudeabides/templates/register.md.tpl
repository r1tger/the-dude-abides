---
title: "Register"
date: "{{ date }}"
---

{% if stats %}
|Notities           |Totaal                 |Gemiddeld                 |
|:------------------|----------------------:|-------------------------:|
|Notities           |{{ stats.nr_vertices }}|n.v.t.                    |
|Relaties           |{{ stats.nr_edges }}   |{{ stats.avg_edges }}     |
|Minst verbonden    |{{ stats.min_edges }}  |n.v.t.                    |
|Meest verbonden    |{{ stats.max_edges }}  |n.v.t.                    |
|Aantal woorden     |{{ stats.word_count }} |{{ stats.avg_word_count }}|
|Ingangnotities     |{{ stats.nr_entry }}   |{{ stats.nr_entry_perc }}%|
|Uitgangnotities (Ω)|{{ stats.nr_exit }}    |{{ stats.nr_exit_perc }}% |
{% endif %}

{% for k, v in notes %}

## {{ k }}

{% for _, b, note, ref in v %}
* {{ note|format_note(b, exit_notes) }}
{% for n, text in ref %}
[{{ n.get_id() }}]({{ n.get_id() }}.html "{{ text }}"){% if not loop.last %}, {% endif %}

{% endfor %}
{% endfor %}
{% endfor %}
