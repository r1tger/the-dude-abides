---
title: "Ingang"
date: "{{ date }}"
---

{% for b, note in entry_notes %}
{{ loop.index }}. {{ note|format_note(b)}}
{% endfor %}

# Inbox

{% for b, note in inbox %}
{{ loop.index }}. {{ note|format_note(b)}}
{% endfor %}
