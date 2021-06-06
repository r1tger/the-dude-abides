---
title: "Vandaag"
date: "{{ date }}"
---

{{ days_to }} dagen totdat ik {{ milestone }} ben.
{{ days_from }} dagen sinds dat ik geboren ben.
{{ days_covid }} dagen sinds de eerste COVID-besmetting in Nederland.

---

{{ stats.nr_vertices }} *notities*
{{ stats.nr_edges }} *relaties* (gemiddeld {{ stats.avg_edges }} relaties per notitie)
{{ stats.word_count }} *woorden*

---

**{{ inbox }} notities in de INBOX**

## {{ suggestions|length }} nieuwe/aangepaste notitie(s) in de afgelopen {{ days }} dagen

{% for note, review in suggestions %}
{{ loop.index }}. {{ note[1]|format_note(note[0]) }}
{% for b, source in review %}
    * {{ source|format_note(b) }}
{% endfor %}
{% endfor %}
