+++
date = '{{ .Date }}'
lastmod = "{{ now.Format "2006-01-02T15:04:05Z07:00" }}"
draft = false
title = '{{ replace .File.ContentBaseName "-" " " | title }}'
+++
