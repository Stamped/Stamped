#!/usr/bin/env python
from __future__ import absolute_import

__author__    = "Stamped (dev@stamped.com)"
__version__   = "1.0"
__copyright__ = "Copyright (c) 2011-2012 Stamped.com"
__license__   = "TODO"

COMPARE_HEADER = """
<html>
  <head>
    <title>%s</title>
    <script>
        function setColor(cellId, color) {
            cells = document.getElementsByName(cellId);
            for (var i = 0; i < cells.length; i++)
                cells[i].style.backgroundColor = color;
        }

        function setVisibility(cellId, display) {
            cells = document.getElementsByName(cellId);
            for (var i = 0; i < cells.length; i++)
                cells[i].style.display = display;
        }

        function highlightCell(cellId) {
            setColor(cellId, 'pink');
        }

        function unhighlightCell(cellId) {
            setColor(cellId, 'white');
        }
        function showCell(cellId) {
            setVisibility(cellId, 'table-row');
        }
        function hideCell(cellId) {
            setVisibility(cellId, 'none');
        }
    </script>
    <style type="text/css">
      img {
        max-height: 100;
        max-width: 100;
      }
    </style>
  </head>
  <body>
    <h1>Result comparison for query <code>%s</code></h1>
    <table cellpadding="5" style="width: 100%%">
"""

COMPARE_FOOTER = """
    </table>
  </body>
</html>
"""

SUMMARY_TPL = """
<html>
  <head>
    <title>Query change summary</title>
  </head>
  <body>
    <h1>%s</h1>
    <table cellpadding="5">
    %s
    </table>
  </body>
</html>
"""
