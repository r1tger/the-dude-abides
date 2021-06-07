---
title: "{{ source }}"
date: "{{ date }}"
---

{% for t, path in lattice %}

## {{ t }}

{% for b, note in path %}
* {{ note|format_note(b) }}
{% endfor %}
{% endfor %}

{% if lattice|length == 0 %}
Geen relaties tot een ingang gevonden.
{% endif %}
