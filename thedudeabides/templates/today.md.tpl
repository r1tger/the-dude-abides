---
title: "Vandaag"
date: "{{ date }}"
---

{{ '{:,}'.format(days_to) }} dagen totdat ik {{ milestone }} ben.
{{ '{:,}'.format(days_from) }} dagen sinds dat ik geboren ben.

{{ '{:,}'.format(days_covid) }} dagen sinds de eerste COVID-besmetting in Nederland.

---

{{ days_hh }} dagen tot Hacker Hotel 2023

---

{{ '{:,}'.format(stats.nr_vertices) }} *notities*
{{ '{:,}'.format(stats.nr_edges) }} *relaties* (gemiddeld {{ stats.avg_edges }} relaties per notitie)
{{ '{:,}'.format(stats.word_count) }} *woorden*

---

**{{ inbox }} notities in de INBOX**

{% if suggestions|length > 0 %}
## {{ suggestions|length }} nieuwe/aangepaste notitie(s) in de afgelopen {{ days }} dagen

{% for note, review in suggestions %}
{{ loop.index }}. {{ note[1]|format_note(note[0]) }}
{% for b, source in review %}
    * {{ source|format_note(b) }}
{% endfor %}
{% endfor %}
{% endif %}
