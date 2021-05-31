---
title: "Vandaag"
date: "{{ date }}"
---

{{ days_to }} dagen totdat ik {{ milestone }} ben.
{{ days_from }} dagen sinds dat ik geboren ben.
{{ days_covid }} dagen sinds de eerste COVID-besmetting in Nederland.

---

{{ stats.nr_vertices }} totaal aantal *notities*
{{ stats.nr_edges }} totaal aantal *relaties* (gemiddeld {{ stats.avg_edges }} relaties per notitie)
{{ stats.word_count }} totaal aantal *woorden*

---

**{{ inbox }} notities in de inbox**

## {{ notes_24h|length }} nieuwe notitie(s) sinds gisteren.

{% for b, note in notes_24h %}
{{ loop.index }}. {{ note|format_note(b)}}
{% endfor %}

## {{ notes_week|length }} nieuwe notitie(s) in de afgelopen zeven dagen.

{% for b, note in notes_week %}
{{ loop.index }}. {{ note|format_note(b)}}
{% endfor %}
