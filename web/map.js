(function (root, factory) {
  "use strict";

  let locationContract = root && root.MilitaryEloLocation;
  if (typeof module === "object" && module.exports) {
    locationContract = require("./location.js");
  }

  const api = factory(locationContract);
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.MilitaryEloMap = api;
})(typeof globalThis === "undefined" ? this : globalThis, function (locationContract) {
  "use strict";

  const SVG_NS = "http://www.w3.org/2000/svg";
  const MIN_ZOOM = 1;
  const MAX_ZOOM = 16;
  const DEFAULT_CELL_SIZE = 44;
  const PLOTTABLE_LOCATION_STATUSES = new Set(["unreviewed_source_assertion"]);

  // Deliberately schematic modern land silhouettes. The map does not draw
  // political borders because current boundaries would be anachronistic for
  // most of the historical events represented here.
  const LAND_POLYGONS = [
    [
      [-168, 72], [-151, 70], [-139, 60], [-130, 54], [-124, 48], [-124, 39],
      [-117, 32], [-106, 23], [-97, 16], [-87, 15], [-83, 9], [-77, 8],
      [-79, 20], [-75, 30], [-66, 44], [-55, 52], [-61, 61], [-79, 67],
      [-96, 73], [-118, 73], [-140, 70],
    ],
    [
      [-73, 59], [-52, 59], [-32, 68], [-26, 78], [-42, 83], [-61, 81],
      [-73, 72],
    ],
    [
      [-81, 12], [-72, 8], [-66, 1], [-61, -8], [-54, -15], [-49, -28],
      [-53, -40], [-65, -55], [-73, -50], [-75, -35], [-79, -18],
    ],
    [
      [-10, 36], [-5, 45], [8, 54], [23, 59], [40, 62], [61, 68],
      [91, 76], [126, 72], [153, 60], [166, 51], [155, 43], [140, 36],
      [126, 34], [119, 23], [108, 18], [101, 7], [93, 6], [79, 21],
      [68, 25], [57, 25], [48, 31], [36, 35], [27, 40], [15, 39],
      [4, 43], [-6, 43],
    ],
    [
      [-17, 35], [-5, 37], [10, 35], [25, 31], [34, 23], [43, 12],
      [51, 11], [43, -12], [35, -25], [28, -34], [17, -35], [8, -30],
      [1, -17], [-7, 4], [-16, 14],
    ],
    [
      [34, 31], [47, 31], [57, 23], [54, 13], [45, 12], [38, 20],
    ],
    [
      [68, 23], [78, 30], [88, 27], [92, 22], [87, 8], [78, 7], [72, 16],
    ],
    [
      [95, 6], [107, 8], [119, 2], [126, -6], [119, -9], [108, -6],
      [101, -2],
    ],
    [
      [112, -11], [129, -12], [145, -18], [154, -28], [146, -39],
      [132, -43], [116, -35], [111, -23],
    ],
    [[48, -13], [51, -17], [50, -26], [45, -25], [44, -17]],
    [[130, 32], [141, 45], [146, 44], [143, 35], [136, 31]],
    [[166, -34], [178, -38], [174, -47], [166, -46]],
    [
      [-180, -68], [-145, -72], [-105, -70], [-65, -75], [-20, -72],
      [20, -74], [65, -70], [105, -73], [145, -69], [180, -71],
      [180, -90], [-180, -90],
    ],
  ];

  function finiteNumber(value) {
    return typeof value === "number" && Number.isFinite(value) ? value : null;
  }

  function clamp(value, minimum, maximum) {
    return Math.min(maximum, Math.max(minimum, value));
  }

  function humanize(value) {
    if (value === null || value === undefined || value === "") return "";
    return String(value)
      .replace(/[_-]+/g, " ")
      .replace(/\b\w/g, (letter) => letter.toUpperCase());
  }

  function eventLayer(eventOrType) {
    const type = typeof eventOrType === "object" && eventOrType !== null
      ? eventOrType.type ?? eventOrType.event_type
      : eventOrType;
    if (type === "engagement") return "tactical";
    if (type === "campaign") return "operational";
    return "strategic";
  }

  function confidenceBand(value) {
    const confidence = finiteNumber(value);
    if (confidence === null) return "unknown";
    if (confidence >= 0.8) return "high";
    if (confidence >= 0.55) return "medium";
    return "low";
  }

  function timeWindow(selectedYear, range) {
    const year = finiteNumber(selectedYear);
    if (year === null) return null;
    if (range === "all") return { start: -Infinity, end: year };
    if (range === "year" || range === 0 || range === "0") {
      return { start: year, end: year };
    }
    const radius = Number(range);
    if (!Number.isFinite(radius) || radius < 0) return null;
    return { start: year - radius, end: year };
  }

  function eventOverlapsWindow(event, window) {
    if (!event || !window) return false;
    const start = finiteNumber(event.year);
    const suppliedEnd = finiteNumber(event.end_year);
    const end = suppliedEnd === null ? start : suppliedEnd;
    return start !== null && end !== null && end >= start && end <= window.end && end >= window.start;
  }

  function safeMapEvent(event) {
    if (!event || typeof event !== "object" || !locationContract) return null;
    if (typeof locationContract.normalizeEventLocation !== "function") return null;
    const location = locationContract.normalizeEventLocation(event);
    if (!location.geometry || !location.location_provenance) return null;
    const status = location.location_provenance.assertion_status;
    if (!PLOTTABLE_LOCATION_STATUSES.has(status)) return null;
    const id = typeof event.id === "string" ? event.id.trim() : "";
    if (!id) return null;
    const year = finiteNumber(event.year);
    if (year === null) return null;
    const {
      geometry: _rawGeometry,
      modern_location_country: _rawCountry,
      location_provenance: _rawProvenance,
      hced_candidate_id: _rawCandidateId,
      ...safeEvent
    } = event;
    return {
      ...safeEvent,
      id,
      year,
      end_year: finiteNumber(event.end_year) ?? year,
      hced_candidate_id: location.hced_candidate_id,
      geometry: location.geometry,
      ...(location.modern_location_country === undefined
        ? {}
        : { modern_location_country: location.modern_location_country }),
      location_provenance: location.location_provenance,
      location_status: status,
      layer: eventLayer(event),
    };
  }

  function compareEvents(left, right) {
    return left.year - right.year || left.end_year - right.end_year || left.id.localeCompare(right.id);
  }

  function createMapIndex(events) {
    if (!Array.isArray(events)) return [];
    return events.map(safeMapEvent).filter(Boolean).sort(compareEvents);
  }

  function matchesContext(event, filters, includeLocationStatus) {
    const window = timeWindow(filters.selectedYear, filters.window ?? "25");
    if (!eventOverlapsWindow(event, window)) return false;
    if (filters.domain && filters.domain !== "all" && event.domain !== filters.domain) return false;
    if (filters.layer && filters.layer !== "all" && eventLayer(event) !== filters.layer) return false;
    if (
      filters.confidence &&
      filters.confidence !== "all" &&
      confidenceBand(event.confidence) !== filters.confidence
    ) return false;
    if (
      includeLocationStatus &&
      filters.locationStatus &&
      filters.locationStatus !== "all" &&
      event.location_status !== filters.locationStatus
    ) return false;
    return true;
  }

  function filterMapEvents(index, filters) {
    if (!Array.isArray(index)) return [];
    return index.filter((event) => matchesContext(event, filters || {}, true));
  }

  function normalizeView(view) {
    const zoom = clamp(finiteNumber(view && view.zoom) ?? MIN_ZOOM, MIN_ZOOM, MAX_ZOOM);
    const halfSpan = 0.5 / zoom;
    return {
      zoom,
      centerX: clamp(finiteNumber(view && view.centerX) ?? 0.5, halfSpan, 1 - halfSpan),
      centerY: clamp(finiteNumber(view && view.centerY) ?? 0.5, halfSpan, 1 - halfSpan),
    };
  }

  function normalizedPoint(coordinates) {
    if (!Array.isArray(coordinates) || coordinates.length !== 2) return null;
    const longitude = finiteNumber(coordinates[0]);
    const latitude = finiteNumber(coordinates[1]);
    if (longitude === null || latitude === null) return null;
    if (longitude < -180 || longitude > 180 || latitude < -90 || latitude > 90) return null;
    return {
      x: (longitude + 180) / 360,
      y: (90 - latitude) / 180,
    };
  }

  function projectEquirectangular(coordinates, width, height, view) {
    const point = normalizedPoint(coordinates);
    const safeWidth = finiteNumber(width);
    const safeHeight = finiteNumber(height);
    if (!point || safeWidth === null || safeHeight === null || safeWidth <= 0 || safeHeight <= 0) return null;
    const safeView = normalizeView(view || {});
    return {
      x: (point.x - safeView.centerX) * safeWidth * safeView.zoom + safeWidth / 2,
      y: (point.y - safeView.centerY) * safeHeight * safeView.zoom + safeHeight / 2,
    };
  }

  function clusterEvents(events, options) {
    const width = finiteNumber(options && options.width) ?? 1000;
    const height = finiteNumber(options && options.height) ?? 500;
    const cellSize = Math.max(24, finiteNumber(options && options.cellSize) ?? DEFAULT_CELL_SIZE);
    const view = normalizeView((options && options.view) || {});
    const sorted = Array.isArray(events) ? [...events].sort(compareEvents) : [];
    const bins = new Map();

    for (const event of sorted) {
      const projected = projectEquirectangular(event.geometry && event.geometry.coordinates, width, height, view);
      if (!projected) continue;
      if (projected.x < -cellSize || projected.x > width + cellSize) continue;
      if (projected.y < -cellSize || projected.y > height + cellSize) continue;
      const column = Math.floor(projected.x / cellSize);
      const row = Math.floor(projected.y / cellSize);
      const key = `${column}:${row}`;
      if (!bins.has(key)) bins.set(key, { key, column, row, xTotal: 0, yTotal: 0, events: [] });
      const bin = bins.get(key);
      bin.xTotal += projected.x;
      bin.yTotal += projected.y;
      bin.events.push(event);
    }

    return [...bins.values()]
      .map((bin) => ({
        key: bin.key,
        column: bin.column,
        row: bin.row,
        x: bin.xTotal / bin.events.length,
        y: bin.yTotal / bin.events.length,
        events: bin.events,
      }))
      .sort((left, right) => left.y - right.y || left.x - right.x || left.key.localeCompare(right.key));
  }

  function createSvgElement(tag, attributes, text) {
    const element = document.createElementNS(SVG_NS, tag);
    for (const [name, value] of Object.entries(attributes || {})) {
      element.setAttribute(name, String(value));
    }
    if (text !== undefined) element.textContent = text;
    return element;
  }

  function pathForPolygon(polygon, width, height, view) {
    const points = polygon
      .map((coordinates) => projectEquirectangular(coordinates, width, height, view))
      .filter(Boolean);
    return points.map((point, index) => `${index ? "L" : "M"}${point.x.toFixed(2)},${point.y.toFixed(2)}`).join(" ") + " Z";
  }

  function drawBasemap(svg, width, height, view, description) {
    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.replaceChildren(
      createSvgElement("title", { id: "battle-map-svg-title" }, "Historical military event map"),
      createSvgElement("desc", { id: "battle-map-svg-description" }, description),
    );

    const graticule = createSvgElement("g", { class: "map-graticule", "aria-hidden": "true" });
    for (const longitude of [-120, -60, 0, 60, 120]) {
      const start = projectEquirectangular([longitude, -90], width, height, view);
      const end = projectEquirectangular([longitude, 90], width, height, view);
      graticule.append(createSvgElement("line", { x1: start.x, y1: start.y, x2: end.x, y2: end.y }));
    }
    for (const latitude of [-60, -30, 0, 30, 60]) {
      const start = projectEquirectangular([-180, latitude], width, height, view);
      const end = projectEquirectangular([180, latitude], width, height, view);
      graticule.append(createSvgElement("line", { x1: start.x, y1: start.y, x2: end.x, y2: end.y }));
    }

    const land = createSvgElement("g", { class: "map-land", "aria-hidden": "true" });
    for (const polygon of LAND_POLYGONS) {
      land.append(createSvgElement("path", { d: pathForPolygon(polygon, width, height, view) }));
    }
    svg.append(graticule, land);
  }

  function sameExactCoordinate(events) {
    if (!events.length) return false;
    const first = events[0].geometry.coordinates;
    return events.every((event) => {
      const coordinates = event.geometry.coordinates;
      return coordinates[0] === first[0] && coordinates[1] === first[1];
    });
  }

  function createBattleMap(options) {
    if (typeof document === "undefined") {
      throw new Error("Battle map UI requires a browser document.");
    }
    const required = ["frame", "svg", "markerLayer", "tooltip", "summary", "clusterPanel", "clusterTitle", "clusterList", "clusterClose"];
    for (const name of required) {
      if (!options || !options[name]) throw new Error(`Battle map is missing ${name}.`);
    }

    const frame = options.frame;
    const svg = options.svg;
    const markerLayer = options.markerLayer;
    const tooltip = options.tooltip;
    const summary = options.summary;
    const clusterPanel = options.clusterPanel;
    const clusterTitle = options.clusterTitle;
    const clusterList = options.clusterList;
    const clusterClose = options.clusterClose;
    const entityName = typeof options.entityName === "function" ? options.entityName : (id) => id;
    const formatYear = typeof options.formatYear === "function" ? options.formatYear : String;
    const formatConfidence = typeof options.formatConfidence === "function"
      ? options.formatConfidence
      : (value) => `${Math.round((finiteNumber(value) ?? 0) * 100)}% confidence`;
    const formatSigned = typeof options.formatSigned === "function"
      ? options.formatSigned
      : (value) => `${value >= 0 ? "+" : ""}${Number(value).toFixed(1)}`;
    const onSelectEvent = typeof options.onSelectEvent === "function" ? options.onSelectEvent : () => {};

    let allEvents = [];
    let mapIndex = [];
    let filters = {
      selectedYear: 0,
      window: "25",
      domain: "all",
      layer: "all",
      confidence: "all",
      locationStatus: "all",
      selectedEventId: null,
    };
    let view = normalizeView({ zoom: 1, centerX: 0.5, centerY: 0.5 });
    let lastClusters = [];
    let renderFrame = 0;
    let drag = null;
    let clusterReturnFocus = null;
    let pendingFocusEventId = null;

    function dimensions() {
      const width = Math.max(280, Math.round(frame.clientWidth || 960));
      const measuredHeight = Math.round(frame.clientHeight || 0);
      const height = Math.max(280, measuredHeight || Math.round(width / 2));
      return { width, height };
    }

    function contextEvents() {
      return allEvents.filter((event) => matchesContext(event, filters, false));
    }

    function currentEvents() {
      return filterMapEvents(mapIndex, filters);
    }

    function participantText(participant, layer) {
      const name = entityName(participant.entity_id) || participant.entity_id || "Unknown polity";
      const result = humanize(participant.result_class) || "Unclassified result";
      const delta = finiteNumber(participant.delta);
      const change = delta === null ? "Elo change unavailable" : `${humanize(layer)} Elo Δ ${formatSigned(delta, 1)}`;
      return `${name} · ${result} · ${change}`;
    }

    function singletonAriaLabel(event) {
      const layer = eventLayer(event);
      const participantSummary = (event.participants || []).slice(0, 2).map((participant) => participantText(participant, layer));
      if ((event.participants || []).length > 2) participantSummary.push(`${event.participants.length - 2} more participants`);
      return [
        event.name,
        formatYear(event.year),
        `${humanize(layer)} event`,
        "unreviewed source location; coordinate precision unknown",
        ...participantSummary,
      ].filter(Boolean).join(". ");
    }

    function clusterAriaLabel(cluster) {
      const years = cluster.events.map((event) => event.year);
      const earliest = Math.min(...years);
      const latest = Math.max(...years);
      const range = earliest === latest ? formatYear(earliest) : `${formatYear(earliest)} to ${formatYear(latest)}`;
      return `${cluster.events.length} mapped military events, ${range}. Activate to ${sameExactCoordinate(cluster.events) || view.zoom >= MAX_ZOOM ? "browse events" : "zoom in"}.`;
    }

    function hideTooltip() {
      tooltip.hidden = true;
      tooltip.replaceChildren();
    }

    function placeTooltip(x, y) {
      tooltip.hidden = false;
      const frameBounds = frame.getBoundingClientRect();
      const tooltipBounds = tooltip.getBoundingClientRect();
      let left = x + 16;
      if (left + tooltipBounds.width > frameBounds.width - 6) left = x - tooltipBounds.width - 16;
      const top = clamp(y - tooltipBounds.height / 2, 6, Math.max(6, frameBounds.height - tooltipBounds.height - 6));
      tooltip.style.left = `${clamp(left, 6, Math.max(6, frameBounds.width - tooltipBounds.width - 6))}px`;
      tooltip.style.top = `${top}px`;
    }

    function showTooltip(cluster) {
      tooltip.replaceChildren();
      if (cluster.events.length > 1) {
        const years = cluster.events.map((event) => event.year);
        const earliest = Math.min(...years);
        const latest = Math.max(...years);
        tooltip.append(
          element("div", "map-tooltip-kicker", "Mapped event cluster"),
          element("strong", "map-tooltip-title", `${cluster.events.length} events`),
          element("div", "map-tooltip-meta", earliest === latest ? formatYear(earliest) : `${formatYear(earliest)}–${formatYear(latest)}`),
        );
        for (const event of cluster.events.slice(0, 4)) {
          tooltip.append(element("div", "map-tooltip-cluster-event", `${formatYear(event.year)} · ${event.name}`));
        }
        if (cluster.events.length > 4) {
          tooltip.append(element("div", "map-tooltip-more", `+${cluster.events.length - 4} more`));
        }
      } else {
        const event = cluster.events[0];
        const layer = eventLayer(event);
        tooltip.append(
          element("div", "map-tooltip-kicker", `${humanize(layer)} · ${humanize(event.domain) || "Unknown domain"}`),
          element("strong", "map-tooltip-title", event.name),
          element("div", "map-tooltip-meta", `${formatYear(event.year)} · ${formatConfidence(event.confidence)}`),
        );
        const participants = Array.isArray(event.participants) ? event.participants : [];
        for (const participant of participants.slice(0, 4)) {
          tooltip.append(element("div", "map-tooltip-outcome", participantText(participant, layer)));
        }
        if (participants.length > 4) {
          tooltip.append(element("div", "map-tooltip-more", `+${participants.length - 4} more participants`));
        }
        tooltip.append(element("div", "map-tooltip-status", "Unreviewed source point · coordinate precision unknown"));
      }
      placeTooltip(cluster.x, cluster.y);
    }

    function element(tag, className, text) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text !== undefined) node.textContent = text;
      return node;
    }

    function closeClusterPanel(restoreFocus) {
      clusterPanel.hidden = true;
      clusterList.replaceChildren();
      if (clusterReturnFocus && clusterReturnFocus.isConnected) {
        clusterReturnFocus.setAttribute("aria-expanded", "false");
      }
      if (restoreFocus) {
        const fallback = markerLayer.querySelector(".map-marker.is-selected") || markerLayer.querySelector(".map-marker");
        const target = clusterReturnFocus && clusterReturnFocus.isConnected ? clusterReturnFocus : fallback;
        if (target) target.focus();
      }
      clusterReturnFocus = null;
    }

    function selectEvent(event) {
      hideTooltip();
      closeClusterPanel(false);
      onSelectEvent(event);
    }

    function openClusterPanel(cluster, trigger) {
      hideTooltip();
      clusterReturnFocus = trigger;
      trigger.setAttribute("aria-expanded", "true");
      clusterTitle.textContent = `${cluster.events.length} events at this map cluster`;
      clusterList.replaceChildren();
      for (const event of cluster.events) {
        const item = element("li", "map-cluster-item");
        const button = element("button", "map-cluster-event");
        button.type = "button";
        const layer = eventLayer(event);
        const outcomes = (event.participants || [])
          .slice(0, 2)
          .map((participant) => participantText(participant, layer))
          .join("; ") || "Participant outcomes unavailable";
        button.append(
          element("span", "map-cluster-event-year", formatYear(event.year)),
          element("span", "map-cluster-event-name", event.name),
          element("span", "map-cluster-event-meta", `${humanize(layer)} · ${formatConfidence(event.confidence)}`),
          element("span", "map-cluster-event-outcome", outcomes),
        );
        button.addEventListener("click", () => selectEvent(event));
        item.append(button);
        clusterList.append(item);
      }
      clusterPanel.hidden = false;
      const first = clusterList.querySelector("button");
      if (first) first.focus();
    }

    function zoomAt(pixelX, pixelY, requestedZoom) {
      const { width, height } = dimensions();
      const old = normalizeView(view);
      const nextZoom = clamp(requestedZoom, MIN_ZOOM, MAX_ZOOM);
      const normalizedScreenX = pixelX / width - 0.5;
      const normalizedScreenY = pixelY / height - 0.5;
      const worldX = old.centerX + normalizedScreenX / old.zoom;
      const worldY = old.centerY + normalizedScreenY / old.zoom;
      view = normalizeView({
        zoom: nextZoom,
        centerX: worldX - normalizedScreenX / nextZoom,
        centerY: worldY - normalizedScreenY / nextZoom,
      });
      scheduleRender();
    }

    function markerKeydown(event, index) {
      if (event.key === "Escape") {
        hideTooltip();
        closeClusterPanel(false);
        return;
      }
      const directions = {
        ArrowLeft: [-1, 0],
        ArrowRight: [1, 0],
        ArrowUp: [0, -1],
        ArrowDown: [0, 1],
      };
      const direction = directions[event.key];
      if (!direction) return;
      event.preventDefault();
      const origin = lastClusters[index];
      let best = null;
      for (let candidateIndex = 0; candidateIndex < lastClusters.length; candidateIndex += 1) {
        if (candidateIndex === index) continue;
        const candidate = lastClusters[candidateIndex];
        const dx = candidate.x - origin.x;
        const dy = candidate.y - origin.y;
        if (direction[0] && Math.sign(dx) !== direction[0]) continue;
        if (direction[1] && Math.sign(dy) !== direction[1]) continue;
        const distance = Math.hypot(dx, dy);
        const crossAxis = direction[0] ? Math.abs(dy) : Math.abs(dx);
        const score = distance + crossAxis * 1.5;
        if (!best || score < best.score) best = { candidateIndex, score };
      }
      if (best) {
        const buttons = markerLayer.querySelectorAll(".map-marker");
        if (buttons[best.candidateIndex]) buttons[best.candidateIndex].focus();
      }
    }

    function renderMarkers(clusters) {
      markerLayer.replaceChildren();
      const buttons = [];
      clusters.forEach((cluster, index) => {
        const count = cluster.events.length;
        const button = element("button", `map-marker${count > 1 ? " is-cluster" : " is-single"}`);
        button.type = "button";
        button.style.left = `${cluster.x}px`;
        button.style.top = `${cluster.y}px`;
        button.dataset.clusterIndex = String(index);
        if (count > 1) {
          button.textContent = String(count);
          button.setAttribute("aria-controls", "map-cluster-panel");
          button.setAttribute("aria-expanded", "false");
        }
        if (cluster.events.some((event) => event.id === filters.selectedEventId)) button.classList.add("is-selected");
        button.setAttribute("aria-label", count > 1 ? clusterAriaLabel(cluster) : singletonAriaLabel(cluster.events[0]));
        button.addEventListener("pointerenter", () => showTooltip(cluster));
        button.addEventListener("pointerleave", () => {
          if (document.activeElement !== button) hideTooltip();
        });
        button.addEventListener("focus", () => showTooltip(cluster));
        button.addEventListener("blur", () => hideTooltip());
        button.addEventListener("keydown", (event) => markerKeydown(event, index));
        button.addEventListener("click", () => {
          if (count === 1) {
            selectEvent(cluster.events[0]);
          } else if (sameExactCoordinate(cluster.events) || view.zoom >= MAX_ZOOM) {
            openClusterPanel(cluster, button);
          } else {
            pendingFocusEventId = cluster.events[0].id;
            zoomAt(cluster.x, cluster.y, Math.min(MAX_ZOOM, view.zoom * 2));
          }
        });
        markerLayer.append(button);
        buttons.push(button);
      });
      if (pendingFocusEventId) {
        const focusIndex = clusters.findIndex((cluster) =>
          cluster.events.some((event) => event.id === pendingFocusEventId));
        pendingFocusEventId = null;
        if (focusIndex >= 0) buttons[focusIndex].focus();
      }
    }

    function render() {
      cancelAnimationFrame(renderFrame);
      renderFrame = 0;
      const { width, height } = dimensions();
      const candidates = contextEvents();
      const located = currentEvents();
      const clusters = clusterEvents(located, { width, height, view, cellSize: DEFAULT_CELL_SIZE });
      lastClusters = clusters;
      const description = `${located.length} publishable event points match the selected map filters. Points are unreviewed source assertions and coordinate precision is unknown.`;
      drawBasemap(svg, width, height, view, description);
      renderMarkers(clusters);
      hideTooltip();

      const unavailable = Math.max(0, candidates.length - located.length);
      const eventWord = located.length === 1 ? "event" : "events";
      const clusterWord = clusters.length === 1 ? "marker cluster" : "marker clusters";
      const unavailableText = unavailable
        ? ` ${unavailable} filtered ${unavailable === 1 ? "event has" : "events have"} no publishable Point and ${unavailable === 1 ? "is" : "are"} not plotted.`
        : "";
      summary.textContent = `${located.length} mapped ${eventWord} in ${clusters.length} visible ${clusterWord}.${unavailableText}`;
      return { eligible: candidates.length, plotted: located.length, clusters: clusters.length, unplotted: unavailable };
    }

    function scheduleRender() {
      cancelAnimationFrame(renderFrame);
      renderFrame = requestAnimationFrame(render);
    }

    function setEvents(events) {
      allEvents = Array.isArray(events) ? [...events] : [];
      mapIndex = createMapIndex(allEvents);
      scheduleRender();
      return mapIndex.length;
    }

    function update(nextFilters) {
      closeClusterPanel(false);
      hideTooltip();
      markerLayer.replaceChildren();
      lastClusters = [];
      summary.textContent = "Updating map for the selected information horizon.";
      filters = { ...filters, ...(nextFilters || {}) };
      scheduleRender();
    }

    function zoomIn() {
      const { width, height } = dimensions();
      zoomAt(width / 2, height / 2, view.zoom * 2);
    }

    function zoomOut() {
      const { width, height } = dimensions();
      zoomAt(width / 2, height / 2, view.zoom / 2);
    }

    function resetView() {
      view = normalizeView({ zoom: 1, centerX: 0.5, centerY: 0.5 });
      closeClusterPanel(false);
      scheduleRender();
    }

    clusterClose.addEventListener("click", () => closeClusterPanel(true));
    clusterPanel.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        event.preventDefault();
        closeClusterPanel(true);
      }
    });

    frame.addEventListener("pointerdown", (event) => {
      if (event.button !== 0 || event.target.closest("button")) return;
      drag = { pointerId: event.pointerId, x: event.clientX, y: event.clientY };
      frame.setPointerCapture(event.pointerId);
      frame.classList.add("is-panning");
    });
    frame.addEventListener("pointermove", (event) => {
      if (!drag || drag.pointerId !== event.pointerId) return;
      const { width, height } = dimensions();
      const dx = event.clientX - drag.x;
      const dy = event.clientY - drag.y;
      drag.x = event.clientX;
      drag.y = event.clientY;
      view = normalizeView({
        zoom: view.zoom,
        centerX: view.centerX - dx / (width * view.zoom),
        centerY: view.centerY - dy / (height * view.zoom),
      });
      scheduleRender();
    });
    const endPan = (event) => {
      if (!drag || drag.pointerId !== event.pointerId) return;
      drag = null;
      frame.classList.remove("is-panning");
      if (frame.hasPointerCapture(event.pointerId)) frame.releasePointerCapture(event.pointerId);
    };
    frame.addEventListener("pointerup", endPan);
    frame.addEventListener("pointercancel", endPan);
    frame.addEventListener("wheel", (event) => {
      event.preventDefault();
      const bounds = frame.getBoundingClientRect();
      const x = clamp(event.clientX - bounds.left, 0, bounds.width);
      const y = clamp(event.clientY - bounds.top, 0, bounds.height);
      zoomAt(x, y, event.deltaY < 0 ? view.zoom * 1.5 : view.zoom / 1.5);
    }, { passive: false });

    let resizeObserver = null;
    const resizeHandler = () => scheduleRender();
    if ("ResizeObserver" in window) {
      resizeObserver = new ResizeObserver(resizeHandler);
      resizeObserver.observe(frame);
    } else {
      window.addEventListener("resize", resizeHandler);
    }

    return {
      closeClusterPanel,
      getIndex: () => [...mapIndex],
      render,
      resetView,
      setEvents,
      update,
      zoomIn,
      zoomOut,
      destroy() {
        cancelAnimationFrame(renderFrame);
        if (resizeObserver) resizeObserver.disconnect();
        else window.removeEventListener("resize", resizeHandler);
      },
    };
  }

  return {
    MAX_ZOOM,
    MIN_ZOOM,
    confidenceBand,
    clusterEvents,
    createBattleMap,
    createMapIndex,
    eventLayer,
    eventOverlapsWindow,
    filterMapEvents,
    normalizeView,
    projectEquirectangular,
    safeMapEvent,
    timeWindow,
  };
});
