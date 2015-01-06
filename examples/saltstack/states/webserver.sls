apache2:
  pkg:
    - installed
  service:
    - running
    - require:
      - pkg: apache2


mywebsite:
  file.managed:
    - name: /var/www/index.html
    - source: salt://index.html

