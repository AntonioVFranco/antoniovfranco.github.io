(() => {
  'use strict';

  const language = document.documentElement.lang;
  const labels = {
    en: ['Table', 'Chart', 'Download CSV', 'Sort by', 'Scroll to see all columns', 'Article data'],
    pt: ['Tabela', 'Gráfico', 'Baixar CSV', 'Ordenar por', 'Role para ver todas as colunas', 'Dados do artigo'],
    es: ['Tabla', 'Gráfico', 'Descargar CSV', 'Ordenar por', 'Desplaza para ver todas las columnas', 'Datos del artículo'],
    zh: ['表格', '图表', '下载 CSV', '排序依据', '滑动以查看全部列', '文章数据'],
    ar: ['الجدول', 'الرسم البياني', 'تنزيل CSV', 'فرز حسب', 'مرّر لعرض كل الأعمدة', 'بيانات المقال'],
    ru: ['Таблица', 'График', 'Скачать CSV', 'Сортировать по', 'Прокрутите, чтобы увидеть все столбцы', 'Данные статьи'],
    it: ['Tabella', 'Grafico', 'Scarica CSV', 'Ordina per', 'Scorri per vedere tutte le colonne', 'Dati dell’articolo'],
    fr: ['Tableau', 'Graphique', 'Télécharger le CSV', 'Trier par', 'Faites défiler pour voir toutes les colonnes', 'Données de l’article'],
    de: ['Tabelle', 'Diagramm', 'CSV herunterladen', 'Sortieren nach', 'Scrollen, um alle Spalten zu sehen', 'Artikeldaten'],
    ja: ['表', 'グラフ', 'CSV をダウンロード', '並べ替え', 'スクロールしてすべての列を表示', '記事データ'],
    ko: ['표', '차트', 'CSV 다운로드', '정렬 기준', '스크롤하여 모든 열 보기', '기사 데이터'],
  };
  const [tableLabel, chartLabel, downloadLabel, sortLabel, scrollLabel, dataLabel] = labels[language.split('-')[0]] || labels.en;
  const collator = new Intl.Collator(language, { numeric: true, sensitivity: 'base' });

  function element(tag, className, text) {
    const node = document.createElement(tag);
    if (className) node.className = className;
    if (text !== undefined) node.textContent = text;
    return node;
  }

  function svg(tag, attributes) {
    const node = document.createElementNS('http://www.w3.org/2000/svg', tag);
    for (const [name, value] of Object.entries(attributes)) node.setAttribute(name, String(value));
    return node;
  }

  function cellText(cell) {
    return cell.textContent.trim().replace(/\s+/g, ' ');
  }

  function cellValue(cell) {
    const explicit = cell.dataset.value;
    return explicit?.trim() && Number.isFinite(Number(explicit)) ? Number(explicit) : null;
  }

  function chartRange(entries) {
    const min = Math.min(0, ...entries.map(entry => entry.value));
    const max = Math.max(0, ...entries.map(entry => entry.value));
    return { min, range: max - min || 1 };
  }

  function barPlot(entries) {
    const plot = element('ul', 'plot-bars');
    const { min, range } = chartRange(entries);
    for (const entry of entries) {
      const bar = element('li');
      if (entry.negative) bar.dataset.tone = 'negative';
      const head = element('div', 'plot-bar-head');
      head.append(element('span', '', entry.label), element('bdi', 'plot-value', entry.display));
      const track = element('span', 'plot-track');
      track.setAttribute('aria-hidden', 'true');
      const fill = element('span', 'plot-fill');
      fill.style.setProperty('--bar-start', `${100 * (Math.min(0, entry.value) - min) / range}%`);
      fill.style.setProperty('--bar-width', `${100 * Math.abs(entry.value) / range}%`);
      track.append(fill);
      bar.append(head, track);
      plot.append(bar);
    }
    return plot;
  }

  function linePlot(entries, title) {
    const { min, range } = chartRange(entries);
    const rtl = document.documentElement.dir === 'rtl';
    const points = entries.map((entry, index) => {
      const position = (index / (entries.length - 1)) * 442;
      return { x: rtl ? 461 - position : 19 + position, y: 146 - ((entry.value - min) / range) * 126 };
    });
    const plot = element('div');
    const chart = svg('svg', {
      class: 'plot-svg', viewBox: '0 0 480 164', role: 'img',
      'aria-label': `${title}. ${entries.map(point => point.label + ' ' + point.display).join('. ')}`,
    });
    const zero = 146 - ((0 - min) / range) * 126;
    chart.append(svg('line', { x1: 19, x2: 461, y1: zero, y2: zero, class: 'plot-base' }));
    chart.append(svg('polyline', { points: points.map(point => `${point.x},${point.y}`).join(' '), class: 'plot-stroke' }));

    const detail = element('p', 'plot-detail');
    detail.setAttribute('aria-live', 'polite');
    const show = entry => {
      detail.textContent = `${entry.label} · ${entry.display}`;
    };
    entries.forEach((entry, index) => {
      const point = svg('circle', {
        cx: points[index].x, cy: points[index].y, r: 5, class: 'plot-point',
      });
      const hint = svg('title', {});
      hint.textContent = `${entry.label} · ${entry.display}`;
      point.addEventListener('pointerenter', () => show(entry));
      point.append(hint);
      chart.append(point);
    });

    const controls = element('div', 'plot-line-labels');
    entries.forEach(entry => {
      const button = element('button', 'data-button', entry.label);
      button.type = 'button';
      button.addEventListener('click', () => show(entry));
      button.addEventListener('focus', () => show(entry));
      controls.append(button);
    });
    show(entries[0]);
    plot.append(chart, detail, controls);
    return plot;
  }

  function chartFor(table, panel, headers, rows) {
    const mode = panel.dataset.chart || table.dataset.chart;
    if (mode !== 'bar' && mode !== 'line') return null;
    const column = Number(panel.dataset.seriesColumn || table.dataset.seriesColumn || 1);
    if (!Number.isInteger(column) || column < 1 || column >= headers.length) return null;
    const entries = rows.filter(row => !row.hasAttribute('data-fixed-row')).map(row => {
      const cell = row.cells[column];
      return {
        label: cellText(row.cells[0]), value: cellValue(cell), display: cellText(cell),
        negative: cell.dataset.tone === 'negative',
      };
    });
    if (entries.length < 2 || entries.some(entry => entry.value === null)) return null;
    const title = cellText(headers[column]);
    const figure = element('figure', 'data-plot');
    figure.hidden = true;
    figure.append(element('figcaption', '', title), mode === 'bar' ? barPlot(entries) : linePlot(entries, title));
    return figure;
  }

  function initSort(table, headers) {
    let active = -1;
    let ascending = true;
    headers.forEach((header, column) => {
      const button = element('button', 'data-sort');
      button.type = 'button';
      button.setAttribute('aria-label', sortLabel + ' ' + cellText(header));
      const marker = element('span', 'data-sort-marker');
      marker.setAttribute('aria-hidden', 'true');
      button.append(...header.childNodes, marker);
      header.append(button);
      button.addEventListener('click', () => {
        ascending = active !== column || !ascending;
        if (active !== -1) headers[active].removeAttribute('aria-sort');
        active = column;
        header.setAttribute('aria-sort', ascending ? 'ascending' : 'descending');
        const body = table.tBodies[0];
        const rows = [...body.rows];
        const regular = rows.filter(row => !row.hasAttribute('data-fixed-row'));
        const numeric = regular.every(row => cellValue(row.cells[column]) !== null);
        regular.sort((first, second) => {
          const a = first.cells[column];
          const b = second.cells[column];
          const difference = numeric ? cellValue(a) - cellValue(b) : collator.compare(cellText(a), cellText(b));
          return ascending ? difference : -difference;
        });
        body.append(...regular, ...rows.filter(row => row.hasAttribute('data-fixed-row')));
      });
    });
  }

  function csvCell(cell) {
    let value = cellText(cell);
    if (cellValue(cell) === null && /^[=+@-]/.test(value)) value = "'" + value;
    return '"' + value.replaceAll('"', '""') + '"';
  }

  function downloadCsv(table, index) {
    const csv = [...table.rows].map(row => [...row.cells].map(csvCell).join(',')).join('\r\n');
    const url = URL.createObjectURL(new Blob(['\ufeff', csv, '\r\n'], { type: 'text/csv;charset=utf-8' }));
    const download = element('a');
    download.href = url;
    download.download = `article-data-${index + 1}.csv`;
    document.body.append(download);
    download.click();
    download.remove();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  function wrap(table) {
    let scroll = table.parentElement;
    if (!scroll.classList.contains('data-scroll')) {
      scroll = element('div', 'data-scroll');
      table.before(scroll);
      scroll.append(table);
    }
    let panel = scroll.parentElement;
    if (!panel.hasAttribute('data-article-data')) {
      panel = element('div', 'article-data');
      panel.setAttribute('data-article-data', '');
      scroll.before(panel);
      panel.append(scroll);
    }
    scroll.tabIndex = 0;
    scroll.setAttribute('role', 'region');
    if (!scroll.hasAttribute('aria-label')) {
      scroll.setAttribute('aria-label', table.caption?.textContent.trim() || dataLabel);
    }
    return { panel, scroll };
  }

  function enhance(table, index) {
    const { panel, scroll } = wrap(table);
    const headers = [...(table.tHead?.rows[0]?.cells || [])];
    const rows = [...(table.tBodies[0]?.rows || [])];
    const plainGrid = table.tHead?.rows.length === 1 && table.tBodies.length === 1 && headers.length && rows.length &&
      [headers, ...rows.map(row => [...row.cells])].every(cells =>
        cells.length === headers.length && cells.every(cell => cell.colSpan === 1 && cell.rowSpan === 1)
      );

    if (plainGrid) {
      const toolbar = element('div', 'data-toolbar');
      const plot = chartFor(table, panel, headers, rows);
      if (plot) {
        const viewGroup = element('div', 'data-views');
        viewGroup.setAttribute('role', 'group');
        viewGroup.setAttribute('aria-label', dataLabel);
        const tableButton = element('button', 'data-button', tableLabel);
        const chartButton = element('button', 'data-button', chartLabel);
        function setView(showPlot) {
          plot.hidden = !showPlot;
          scroll.hidden = showPlot;
          tableButton.setAttribute('aria-pressed', String(!showPlot));
          chartButton.setAttribute('aria-pressed', String(showPlot));
        }
        tableButton.type = 'button';
        chartButton.type = 'button';
        tableButton.addEventListener('click', () => setView(false));
        chartButton.addEventListener('click', () => setView(true));
        viewGroup.append(tableButton, chartButton);
        toolbar.append(viewGroup);
        panel.append(plot);
        setView(false);
      }
      const download = element('button', 'data-button', 'CSV');
      download.type = 'button';
      download.title = downloadLabel;
      download.setAttribute('aria-label', downloadLabel);
      const icon = svg('svg', { viewBox: '0 0 24 24', fill: 'none', stroke: 'currentColor', 'stroke-width': 1.7, 'stroke-linecap': 'round', 'stroke-linejoin': 'round', 'aria-hidden': true });
      icon.append(svg('path', { d: 'M12 3v12m-4-4 4 4 4-4M5 16v5h14v-5' }));
      download.prepend(icon);
      download.addEventListener('click', () => downloadCsv(table, index));
      toolbar.append(download);
      scroll.before(toolbar);
      if (rows.filter(row => !row.hasAttribute('data-fixed-row')).length > 1 && !table.hasAttribute('data-no-sort')) {
        initSort(table, headers);
      }
    }
    if ('ResizeObserver' in window) {
      const hint = element('p', 'data-scroll-hint', scrollLabel);
      hint.hidden = true;
      scroll.after(hint);
      new ResizeObserver(() => {
        hint.hidden = scroll.hidden || scroll.scrollWidth <= scroll.clientWidth + 1;
      }).observe(scroll);
    }
  }

  [...document.querySelectorAll('article.prose table')].forEach(enhance);
})();
