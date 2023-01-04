---
title: "Groepen"
date: "{{ date }}"
---

{% for k, v in notes %}

## {{ k|escape }}

{% for b, note in v %}
{{ loop.index }}. {{ note|format_note(b, exit_notes)}}
{% endfor %}

{% endfor %}
