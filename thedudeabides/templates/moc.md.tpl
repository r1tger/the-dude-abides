---
title: "{{ note.get_title() }}"
date: "{{ date }}"
---

{% for b, n in notes %}
{{ n|format_note(b, exit_notes) }}
: {{ n.get_summary() }}&hellip;

{% endfor %}
