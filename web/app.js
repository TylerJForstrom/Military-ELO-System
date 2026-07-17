(function () {
  "use strict";

  const DATA_URL = "./data/results.json";
  const SVG_NS = "http://www.w3.org/2000/svg";
  const MAX_PINNED = 10;
  const REGISTRY_PAGE_SIZE = 200;
  const REGISTRY_STATUSES = new Set(["rated", "unrated", "provisional"]);
  const locationContract = window.MilitaryEloLocation;
  const mapContract = window.MilitaryEloMap;
  const horizonContract = window.MilitaryEloHorizon;

  if (!locationContract || !mapContract || !horizonContract) {
    throw new Error("A required dashboard location, map, or information-horizon contract failed to load.");
  }

  const METRIC_LABELS = {
    composite: "Composite",
    strategic: "Strategic",
    operational: "Operational",
    tactical: "Tactical",
  };

  const PERSPECTIVE_LABELS = {
    historical_success: "Historical success",
    current: "Current composite",
    peak: "Peak rating",
    sustained: "Sustained rating",
    achievement: "Achievement",
  };

  const SERIES_COLORS = [
    "#64d5c0",
    "#f2b46d",
    "#88b8f7",
    "#e68f9d",
    "#b6a0ef",
    "#b7cc6a",
    "#80c6e8",
    "#d89bd1",
    "#e3d2a0",
    "#ffcf5c",
  ];

  const DASH_PATTERNS = ["", "", "", "", "", "", "", "", "", "", "7 4", "3 4", "10 4 2 4"];

  const elements = {
    datasetBadge: document.getElementById("dataset-badge"),
    generatedLabel: document.getElementById("generated-label"),
    coverageRegistryPolities: document.getElementById("coverage-registry-polities"),
    coverageRatedEntities: document.getElementById("coverage-rated-entities"),
    coverageRatedEvents: document.getElementById("coverage-rated-events"),
    coverageStagedRecords: document.getElementById("coverage-staged-records"),
    datasetNotice: document.getElementById("dataset-notice"),
    noticeTitle: document.getElementById("notice-title"),
    noticeCopy: document.getElementById("notice-copy"),
    noticeDetails: document.getElementById("notice-details"),
    registryCount: document.getElementById("registry-count"),
    registrySearch: document.getElementById("registry-search"),
    registryStatus: document.getElementById("registry-status-filter"),
    registryKind: document.getElementById("registry-kind-filter"),
    registrySummary: document.getElementById("registry-summary"),
    registryBody: document.getElementById("registry-body"),
    registryEmpty: document.getElementById("registry-empty"),
    registryShowing: document.getElementById("registry-showing"),
    registryShowMore: document.getElementById("registry-show-more"),
    search: document.getElementById("entity-search"),
    searchResultsWrap: document.getElementById("search-results-wrap"),
    searchResults: document.getElementById("search-results"),
    metric: document.getElementById("metric-select"),
    perspective: document.getElementById("perspective-select"),
    topN: document.getElementById("top-n-select"),
    pinRow: document.getElementById("pin-row"),
    pinList: document.getElementById("pin-list"),
    clearPins: document.getElementById("clear-pins"),
    selectedYear: document.getElementById("selected-year"),
    slider: document.getElementById("year-slider"),
    sliderMin: document.getElementById("slider-min"),
    sliderMax: document.getElementById("slider-max"),
    previousEvent: document.getElementById("previous-event"),
    nextEvent: document.getElementById("next-event"),
    chartFrame: document.getElementById("chart-frame"),
    chart: document.getElementById("timeline-chart"),
    chartDescription: document.getElementById("chart-description"),
    chartTooltip: document.getElementById("chart-tooltip"),
    chartEmpty: document.getElementById("chart-empty"),
    chartLegend: document.getElementById("chart-legend"),
    chartSummary: document.getElementById("chart-summary"),
    chartFrameModern: document.getElementById("chart-frame-modern"),
    chartModern: document.getElementById("timeline-chart-modern"),
    chartEmptyModern: document.getElementById("chart-empty-modern"),
    chartSummaryModern: document.getElementById("chart-summary-modern"),
    modernSlider: document.getElementById("modern-year-slider"),
    modernSliderMin: document.getElementById("modern-slider-min"),
    modernSliderMax: document.getElementById("modern-slider-max"),
    modernSelectedYear: document.getElementById("modern-selected-year"),
    timelineRankingTitle: document.getElementById("timeline-ranking-title"),
    timelineRankingMetric: document.getElementById("timeline-ranking-metric"),
    timelineRankingList: document.getElementById("timeline-ranking-list"),
    timelineRankingEmpty: document.getElementById("timeline-ranking-empty"),
    mapYear: document.getElementById("map-year"),
    mapWindow: document.getElementById("map-window-select"),
    mapDomain: document.getElementById("map-domain-select"),
    mapLayer: document.getElementById("map-layer-select"),
    mapConfidence: document.getElementById("map-confidence-select"),
    mapLocationStatus: document.getElementById("map-location-status-select"),
    mapFrame: document.getElementById("battle-map-frame"),
    mapSvg: document.getElementById("battle-map"),
    mapMarkerLayer: document.getElementById("map-marker-layer"),
    mapTooltip: document.getElementById("map-tooltip"),
    mapSummary: document.getElementById("map-summary"),
    mapZoomIn: document.getElementById("map-zoom-in"),
    mapZoomOut: document.getElementById("map-zoom-out"),
    mapResetView: document.getElementById("map-reset-view"),
    mapClusterPanel: document.getElementById("map-cluster-panel"),
    mapClusterTitle: document.getElementById("map-cluster-title"),
    mapClusterList: document.getElementById("map-cluster-list"),
    mapClusterClose: document.getElementById("map-cluster-close"),
    leaderboardTitle: document.getElementById("leaderboard-title"),
    leaderboardMetric: document.getElementById("leaderboard-metric"),
    leaderboardCaption: document.getElementById("leaderboard-caption"),
    leaderboardBody: document.getElementById("leaderboard-body"),
    leaderboardEmpty: document.getElementById("leaderboard-empty"),
    momentumWindow: document.getElementById("momentum-window"),
    risersList: document.getElementById("risers-list"),
    fallersList: document.getElementById("fallers-list"),
    moversEmpty: document.getElementById("movers-empty"),
    eventsYear: document.getElementById("events-year"),
    eventDomain: document.getElementById("event-domain-select"),
    eventList: document.getElementById("event-list"),
    eventsEmpty: document.getElementById("events-empty"),
    eventDetail: document.getElementById("event-detail"),
    methodologyNote: document.getElementById("methodology-note"),
    footerCoverage: document.getElementById("footer-coverage"),
    toast: document.getElementById("toast"),
  };

  const state = {
    data: null,
    entityById: new Map(),
    leaderboardById: new Map(),
    eventById: new Map(),
    entityEventYears: new Map(),
    entityEvents: new Map(),
    ratedEntityIds: new Set(),
    eventYears: [],
    latestRatedEventYear: -Infinity,
    minYear: 0,
    maxYear: 1,
    selectedYear: 1,
    metric: "composite",
    perspective: "historical_success",
    topN: 8,
    pinned: new Set(),
    selectedEventId: null,
    eventDomain: "all",
    mapWindow: "25",
    mapDomain: "all",
    mapLayer: "all",
    mapConfidence: "all",
    mapLocationStatus: "all",
    battleMap: null,
    visibleEntityIds: [],
    searchMatches: [],
    searchIndex: -1,
    registryVisibleLimit: REGISTRY_PAGE_SIZE,
    fallbackUsed: false,
    renderFrame: 0,
    resizeFrame: 0,
    toastTimer: 0,
  };

  init();

  async function init() {
    bindControls();

    let payload;
    try {
      const response = await fetch(DATA_URL, { cache: "no-store" });
      if (!response.ok) {
        throw new Error(`The dataset returned HTTP ${response.status}.`);
      }
      payload = await response.json();
    } catch (error) {
      state.fallbackUsed = true;
      payload = createFallbackData();
      console.warn("Using the built-in dashboard preview because results.json could not be loaded.", error);
    }

    try {
      state.data = normalizeData(payload);
    } catch (error) {
      state.fallbackUsed = true;
      state.data = normalizeData(createFallbackData());
      console.error("The results dataset was invalid; using the built-in preview.", error);
    }

    buildIndexes();
    configureTimeline();
    configureMap();
    configureRegistry();
    renderMetadata();
    renderRegistry();
    renderAll();
    observeChartSize();
  }

  function bindControls() {
    elements.metric.addEventListener("change", () => {
      state.metric = elements.metric.value;
      scheduleRender();
    });

    elements.perspective.addEventListener("change", () => {
      state.perspective = elements.perspective.value;
      scheduleRender();
    });

    elements.topN.addEventListener("change", () => {
      state.topN = Number(elements.topN.value) || 8;
      scheduleRender();
    });

    elements.slider.addEventListener("input", () => {
      state.selectedYear = Number(elements.slider.value);
      scheduleRender();
    });

    elements.modernSlider.addEventListener("input", () => {
      state.modernEndYear = Number(elements.modernSlider.value);
      renderModernChart(state.visibleEntityIds ?? []);
    });

    elements.previousEvent.addEventListener("click", () => jumpToAdjacentEvent(-1));
    elements.nextEvent.addEventListener("click", () => jumpToAdjacentEvent(1));

    elements.mapWindow.addEventListener("change", () => {
      state.mapWindow = elements.mapWindow.value;
      scheduleRender();
    });
    elements.mapDomain.addEventListener("change", () => {
      state.mapDomain = elements.mapDomain.value;
      scheduleRender();
    });
    elements.mapLayer.addEventListener("change", () => {
      state.mapLayer = elements.mapLayer.value;
      scheduleRender();
    });
    elements.mapConfidence.addEventListener("change", () => {
      state.mapConfidence = elements.mapConfidence.value;
      scheduleRender();
    });
    elements.mapLocationStatus.addEventListener("change", () => {
      state.mapLocationStatus = elements.mapLocationStatus.value;
      scheduleRender();
    });
    elements.mapZoomIn.addEventListener("click", () => state.battleMap && state.battleMap.zoomIn());
    elements.mapZoomOut.addEventListener("click", () => state.battleMap && state.battleMap.zoomOut());
    elements.mapResetView.addEventListener("click", () => state.battleMap && state.battleMap.resetView());

    elements.eventDomain.addEventListener("change", () => {
      state.eventDomain = elements.eventDomain.value;
      state.selectedEventId = null;
      renderEvents();
    });

    elements.search.addEventListener("input", () => {
      state.searchIndex = -1;
      renderSearchResults();
    });

    elements.search.addEventListener("focus", () => {
      if (elements.search.value.trim()) {
        renderSearchResults();
      }
    });

    elements.search.addEventListener("keydown", handleSearchKeyboard);

    elements.clearPins.addEventListener("click", () => {
      state.pinned.clear();
      renderAll();
      showToast("All pinned polities cleared.");
    });

    elements.registrySearch.addEventListener("input", () => {
      state.registryVisibleLimit = REGISTRY_PAGE_SIZE;
      renderRegistry();
    });

    elements.registryStatus.addEventListener("change", () => {
      state.registryVisibleLimit = REGISTRY_PAGE_SIZE;
      renderRegistry();
    });

    elements.registryKind.addEventListener("change", () => {
      state.registryVisibleLimit = REGISTRY_PAGE_SIZE;
      renderRegistry();
    });

    elements.registryShowMore.addEventListener("click", () => {
      state.registryVisibleLimit += REGISTRY_PAGE_SIZE;
      renderRegistry();
    });

    document.addEventListener("click", (event) => {
      if (!event.target.closest(".field-search") && !event.target.closest("#search-results-wrap")) {
        closeSearchResults();
      }
    });
  }

  function observeChartSize() {
    if ("ResizeObserver" in window) {
      const observer = new ResizeObserver(() => {
        cancelAnimationFrame(state.resizeFrame);
        state.resizeFrame = requestAnimationFrame(() => renderChart(state.visibleEntityIds));
      });
      observer.observe(elements.chartFrame);
    } else {
      window.addEventListener("resize", () => {
        cancelAnimationFrame(state.resizeFrame);
        state.resizeFrame = requestAnimationFrame(() => renderChart(state.visibleEntityIds));
      });
    }
  }

  function normalizeData(raw) {
    if (!raw || typeof raw !== "object") {
      throw new Error("Expected a JSON object at the dataset root.");
    }

    const entities = Array.isArray(raw.entities)
      ? raw.entities
          .map((entity, index) => ({
            id: String(entity.id ?? `entity-${index + 1}`),
            name: String(entity.name ?? entity.id ?? `Entity ${index + 1}`),
            kind: cleanOptionalText(entity.kind),
            start_year: finiteNumber(entity.start_year),
            end_year: finiteNumber(entity.end_year),
            region: cleanOptionalText(entity.region),
          }))
          .filter((entity) => entity.id)
      : [];

    const series = {};
    const rawSeries = raw.series && typeof raw.series === "object" ? raw.series : {};

    for (const entity of entities) {
      const sourcePoints = Array.isArray(rawSeries[entity.id]) ? rawSeries[entity.id] : [];
      const normalizedPoints = sourcePoints
        .map((point, index) => normalizePoint(point, index))
        .filter(Boolean)
        .sort((a, b) => a.year - b.year || a._sourceIndex - b._sourceIndex)
        .map((point, index) => ({ ...point, _index: index }));
      series[entity.id] = normalizedPoints;
    }

    for (const [entityId, sourcePoints] of Object.entries(rawSeries)) {
      if (series[entityId] || !Array.isArray(sourcePoints)) continue;
      series[entityId] = sourcePoints
        .map((point, index) => normalizePoint(point, index))
        .filter(Boolean)
        .sort((a, b) => a.year - b.year || a._sourceIndex - b._sourceIndex)
        .map((point, index) => ({ ...point, _index: index }));
    }

    const events = Array.isArray(raw.events)
      ? raw.events
          .map((event, index) => normalizeEvent(event, index))
          .filter(Boolean)
          .sort((a, b) => a.year - b.year || a.name.localeCompare(b.name))
      : [];

    const normalizedLeaderboard = Array.isArray(raw.leaderboard)
      ? raw.leaderboard.map((row, index) => normalizeLeaderboardRow(row, index))
      : [];

    const eventParticipantIds = new Set(
      events.flatMap((event) => event.participants.map((participant) => participant.entity_id)),
    );
    const leaderboard = normalizedLeaderboard.filter((row) =>
      row.events !== null ? row.events > 0 : eventParticipantIds.has(row.entity_id),
    );
    const summaryById = new Map(normalizedLeaderboard.map((row) => [row.entity_id, row]));

    const rawRegistry = raw.registry && typeof raw.registry === "object" ? raw.registry : {};
    const registryInput = Array.isArray(rawRegistry.entities) ? rawRegistry.entities : entities;
    const seenRegistryIds = new Set();
    const registryEntities = registryInput
      .map((entity, index) => normalizeRegistryEntity(entity, index, summaryById, eventParticipantIds))
      .filter((entity) => {
        if (!entity || seenRegistryIds.has(entity.id)) return false;
        seenRegistryIds.add(entity.id);
        return true;
      })
      .sort((a, b) => a.name.localeCompare(b.name));

    const coverageInput = rawRegistry.coverage && typeof rawRegistry.coverage === "object" ? rawRegistry.coverage : {};
    const registryCoverage = {
      registry_polities: nonNegativeNumber(coverageInput.registry_polities) ?? registryEntities.length,
      rated_entities:
        nonNegativeNumber(coverageInput.rated_entities) ??
        registryEntities.filter((entity) => entity.status === "rated" || entity.status === "provisional").length,
      rated_events: nonNegativeNumber(coverageInput.rated_events) ?? events.length,
      staged_source_records:
        nonNegativeNumber(coverageInput.staged_source_records) ??
        nonNegativeNumber(coverageInput.staged_source_assertions) ??
        nonNegativeNumber(coverageInput.unresolved_source_assertions),
    };

    const yearCandidates = [];
    for (const [entityId, points] of Object.entries(series)) {
      if (!eventParticipantIds.has(entityId)) continue;
      for (const point of points) yearCandidates.push(point.year);
    }
    for (const event of events) {
      yearCandidates.push(event.year);
      if (event.end_year !== null) yearCandidates.push(event.end_year);
    }
    for (const entity of entities) {
      if (!eventParticipantIds.has(entity.id)) continue;
      if (entity.start_year !== null) yearCandidates.push(entity.start_year);
      if (entity.end_year !== null) yearCandidates.push(entity.end_year);
    }

    if (!entities.length || !yearCandidates.length) {
      throw new Error("The dataset needs at least one entity and one dated record.");
    }

    return {
      meta: raw.meta && typeof raw.meta === "object" ? raw.meta : {},
      entities,
      series,
      leaderboard,
      events,
      registry: {
        entities: registryEntities,
        coverage: registryCoverage,
      },
    };
  }

  function normalizeRegistryEntity(entity, index, summaryById, eventParticipantIds) {
    if (!entity || typeof entity !== "object") return null;
    const id = String(entity.id ?? `registry-${index + 1}`).trim();
    if (!id) return null;

    const suppliedStatus = String(entity.status ?? "").trim().toLocaleLowerCase();
    let status = REGISTRY_STATUSES.has(suppliedStatus) ? suppliedStatus : null;
    if (!status) {
      const summary = summaryById.get(id);
      status = eventParticipantIds.has(id) ? (summary && summary.established === false ? "provisional" : "rated") : "unrated";
    }

    const suppliedIdentityStatus = String(entity.identity_status ?? "").trim().toLocaleLowerCase();
    const identityStatus = suppliedIdentityStatus === "curated" ? "curated" : "source_candidate";
    const region = cleanOptionalText(entity.region);

    return {
      id,
      name: String(entity.name ?? id),
      kind: cleanOptionalText(entity.kind),
      start_year: finiteNumber(entity.start_year),
      end_year: finiteNumber(entity.end_year),
      region: region && region.toLocaleLowerCase() !== "unclassified" ? region : null,
      status,
      identity_status: identityStatus,
      coverage_discontinuous: entity.coverage_discontinuous === true,
    };
  }

  function normalizePoint(point, sourceIndex) {
    if (!point || typeof point !== "object") return null;
    const year = finiteNumber(point.year);
    if (year === null) return null;

    let tactical = finiteNumber(point.tactical);
    let strategic = finiteNumber(point.strategic);
    let operational = finiteNumber(point.operational);
    let composite = finiteNumber(point.composite);

    if (operational === null && tactical !== null && strategic !== null) {
      operational = (tactical + strategic) / 2;
    }
    if (composite === null) {
      composite = average([tactical, operational, strategic]);
    }
    if (tactical === null) tactical = composite;
    if (strategic === null) strategic = composite;
    if (operational === null) operational = composite;

    if (composite === null) return null;

    return {
      year,
      event_id: point.event_id === null || point.event_id === undefined ? null : String(point.event_id),
      tactical,
      operational,
      strategic,
      composite,
      uncertainty: nonNegativeNumber(point.uncertainty),
      delta: finiteNumber(point.delta),
      _sourceIndex: sourceIndex,
    };
  }

  function normalizeEvent(event, index) {
    if (!event || typeof event !== "object") return null;
    const year = finiteNumber(event.year);
    if (year === null) return null;

    const participants = Array.isArray(event.participants)
      ? event.participants.map((participant) => ({
          entity_id: String(participant.entity_id ?? "unknown"),
          side: cleanOptionalText(participant.side),
          result_class: cleanOptionalText(participant.result_class),
          utility: finiteNumber(participant.utility),
          delta: finiteNumber(participant.delta),
          importance: participant.importance ?? null,
          termination: cleanOptionalText(participant.termination),
        }))
      : [];

    const sources = Array.isArray(event.sources)
      ? event.sources
          .filter((source) => source && typeof source === "object")
          .map((source) => ({
            id: cleanOptionalText(source.id ?? source.source_id),
            title: String(source.title ?? source.url ?? "Untitled source"),
            url: cleanOptionalText(source.url),
            source_family_id: cleanOptionalText(source.source_family_id),
            evidence_roles: cleanTextArray(source.evidence_roles),
          }))
      : [];

    return {
      id: String(event.id ?? `event-${index + 1}`),
      name: String(event.name ?? `Event ${index + 1}`),
      year,
      end_year: finiteNumber(event.end_year),
      type: cleanOptionalText(event.type),
      war_type: cleanOptionalText(event.war_type),
      scale: event.scale ?? null,
      stakes: event.stakes ?? null,
      confidence: finiteNumber(event.confidence),
      summary: cleanOptionalText(event.summary),
      domain: cleanOptionalText(event.domain),
      geographic_scope: cleanOptionalText(event.geographic_scope),
      evidence_weight: nonNegativeNumber(event.evidence_weight) ?? 1,
      participants,
      source_ids: cleanTextArray(event.source_ids),
      outcome_source_ids: cleanTextArray(event.outcome_source_ids),
      outcome_source_family_ids: cleanTextArray(event.outcome_source_family_ids),
      sources,
      ...locationContract.normalizeEventLocation(event),
    };
  }

  function normalizeLeaderboardRow(row, index) {
    const safeRow = row && typeof row === "object" ? row : {};
    return {
      entity_id: String(safeRow.entity_id ?? `leader-${index + 1}`),
      name: String(safeRow.name ?? safeRow.entity_id ?? `Entity ${index + 1}`),
      composite: finiteNumber(safeRow.composite),
      tactical: finiteNumber(safeRow.tactical),
      operational: finiteNumber(safeRow.operational),
      strategic: finiteNumber(safeRow.strategic),
      peak: finiteNumber(safeRow.peak),
      peak_year: finiteNumber(safeRow.peak_year),
      sustained: finiteNumber(safeRow.sustained),
      achievement: finiteNumber(safeRow.achievement),
      historical_success: finiteNumber(safeRow.historical_success),
      events: finiteNumber(safeRow.events),
      wars: finiteNumber(safeRow.wars),
      wins: finiteNumber(safeRow.wins),
      losses: finiteNumber(safeRow.losses),
      draws: finiteNumber(safeRow.draws),
      confidence: finiteNumber(safeRow.confidence),
      uncertainty: nonNegativeNumber(safeRow.uncertainty),
      network_component: safeRow.network_component ?? null,
      established: safeRow.established !== false,
    };
  }

  function buildIndexes() {
    state.entityById = new Map(state.data.entities.map((entity) => [entity.id, entity]));
    state.leaderboardById = new Map(state.data.leaderboard.map((row) => [row.entity_id, row]));
    state.eventById = new Map(state.data.events.map((event) => [event.id, event]));
    state.ratedEntityIds = new Set(
      state.data.events.flatMap((event) => event.participants.map((participant) => participant.entity_id)),
    );

    const allYears = [];
    for (const [entityId, points] of Object.entries(state.data.series)) {
      if (!state.ratedEntityIds.has(entityId)) continue;
      for (const point of points) allYears.push(point.year);
    }
    for (const event of state.data.events) {
      allYears.push(event.year);
      if (event.end_year !== null) allYears.push(event.end_year);
    }

    for (const entity of state.data.entities) {
      if (!state.ratedEntityIds.has(entity.id)) continue;
      if (entity.start_year !== null) allYears.push(entity.start_year);
      if (entity.end_year !== null) allYears.push(entity.end_year);
    }

    const metaEndYear =
      finiteNumber(state.data.meta.coverage_end_year) ??
      finiteNumber(state.data.meta.max_year) ??
      finiteNumber(state.data.meta.as_of_year);
    if (metaEndYear !== null) {
      allYears.push(metaEndYear);
    } else if (state.data.entities.some((entity) => entity.end_year === null)) {
      allYears.push(new Date().getFullYear());
    }

    state.minYear = Math.floor(Math.min(...allYears));
    state.maxYear = Math.ceil(Math.max(...allYears));
    if (state.minYear === state.maxYear) state.maxYear += 1;
    state.selectedYear = state.maxYear;
    state.eventYears = [...new Set(state.data.events.map(horizonContract.eventAvailabilityYear).filter(Number.isFinite))].sort(
      (a, b) => a - b,
    );
    state.latestRatedEventYear = state.eventYears.length ? state.eventYears[state.eventYears.length - 1] : -Infinity;

    state.entityEventYears = new Map();
    state.entityEvents = new Map();
    for (const event of state.data.events) {
      const availableYear = horizonContract.eventAvailabilityYear(event);
      if (!Number.isFinite(availableYear)) continue;
      const indexedParticipants = new Set();
      for (const participant of event.participants) {
        if (indexedParticipants.has(participant.entity_id)) continue;
        indexedParticipants.add(participant.entity_id);
        if (!state.entityEventYears.has(participant.entity_id)) {
          state.entityEventYears.set(participant.entity_id, []);
          state.entityEvents.set(participant.entity_id, []);
        }
        state.entityEventYears.get(participant.entity_id).push(availableYear);
        state.entityEvents.get(participant.entity_id).push(event);
      }
    }
    for (const years of state.entityEventYears.values()) years.sort((a, b) => a - b);
    for (const events of state.entityEvents.values()) {
      events.sort((left, right) => horizonContract.eventAvailabilityYear(left) - horizonContract.eventAvailabilityYear(right));
    }
  }

  function configureTimeline() {
    elements.slider.min = String(state.minYear);
    elements.slider.max = String(state.maxYear);
    elements.slider.value = String(state.selectedYear);
    elements.sliderMin.textContent = formatYear(state.minYear);
    elements.sliderMax.textContent = formatYear(state.maxYear);

    state.modernEndYear = state.maxYear;
    elements.modernSlider.min = String(state.minYear);
    elements.modernSlider.max = String(state.maxYear);
    elements.modernSlider.value = String(state.modernEndYear);
    elements.modernSliderMin.textContent = formatYear(state.minYear);
    elements.modernSliderMax.textContent = formatYear(state.maxYear);

    const domains = [...new Set(state.data.events.map((event) => event.domain).filter(Boolean))].sort((a, b) =>
      a.localeCompare(b),
    );
    elements.eventDomain.replaceChildren();
    const allDomains = createElement("option", "", "All domains");
    allDomains.value = "all";
    elements.eventDomain.append(allDomains);
    for (const domain of domains) {
      const option = createElement("option", "", humanize(domain));
      option.value = domain;
      elements.eventDomain.append(option);
    }
    elements.eventDomain.disabled = domains.length < 2;

    if (!state.data.leaderboard.some((row) => row.historical_success !== null)) {
      state.perspective = "current";
      elements.perspective.value = "current";
    }
  }

  function configureMap() {
    state.battleMap = mapContract.createBattleMap({
      frame: elements.mapFrame,
      svg: elements.mapSvg,
      markerLayer: elements.mapMarkerLayer,
      tooltip: elements.mapTooltip,
      summary: elements.mapSummary,
      clusterPanel: elements.mapClusterPanel,
      clusterTitle: elements.mapClusterTitle,
      clusterList: elements.mapClusterList,
      clusterClose: elements.mapClusterClose,
      entityName: (entityId) => state.entityById.get(entityId)?.name ?? entityId,
      formatYear,
      formatConfidence: (value) => formatConfidence(value) || "Confidence unavailable",
      formatSigned,
      onSelectEvent: (event) => {
        state.selectedEventId = event.id;
        state.eventDomain = "all";
        elements.eventDomain.value = "all";
        jumpToYear(horizonContract.eventAvailabilityYear(event));
        showToast(`${event.name} opened in the evidence trail.`);
        requestAnimationFrame(() => {
          elements.eventDetail.tabIndex = -1;
          elements.eventDetail.focus({ preventScroll: true });
        });
      },
    });
    state.battleMap.setEvents(state.data.events);

    const mapDomains = [
      ...new Set(state.battleMap.getIndex().map((event) => event.domain).filter(Boolean)),
    ].sort((left, right) => left.localeCompare(right));
    elements.mapDomain.replaceChildren();
    const allDomains = createElement("option", "", "All domains");
    allDomains.value = "all";
    elements.mapDomain.append(allDomains);
    for (const domain of mapDomains) {
      const option = createElement("option", "", humanize(domain));
      option.value = domain;
      elements.mapDomain.append(option);
    }
    elements.mapDomain.disabled = mapDomains.length < 2;
  }

  function configureRegistry() {
    const kinds = [...new Set(state.data.registry.entities.map((entity) => entity.kind).filter(Boolean))].sort((a, b) =>
      a.localeCompare(b),
    );
    elements.registryKind.replaceChildren();
    const allKinds = createElement("option", "", "All kinds");
    allKinds.value = "all";
    elements.registryKind.append(allKinds);
    for (const kind of kinds) {
      const option = createElement("option", "", humanize(kind));
      option.value = kind;
      elements.registryKind.append(option);
    }
    elements.registryKind.disabled = kinds.length < 2;
  }

  function renderRegistry() {
    if (!state.data) return;

    const query = elements.registrySearch.value.trim().toLocaleLowerCase();
    const status = elements.registryStatus.value;
    const kind = elements.registryKind.value;
    const matches = state.data.registry.entities.filter((entity) => {
      if (status !== "all" && entity.status !== status) return false;
      if (kind !== "all" && entity.kind !== kind) return false;
      if (!query) return true;
      const searchable = [entity.name, entity.kind, entity.region, entityEra(entity)]
        .filter(Boolean)
        .join(" ")
        .toLocaleLowerCase();
      return searchable.includes(query);
    });

    const visible = matches.slice(0, state.registryVisibleLimit);
    elements.registryBody.replaceChildren();
    elements.registryEmpty.hidden = matches.length > 0;
    elements.registryCount.textContent = `${formatInteger(state.data.registry.coverage.registry_polities)} registered`;
    elements.registrySummary.textContent = registryFilterSummary(matches.length, status, kind, query);

    for (const entity of visible) {
      const row = createElement("tr");
      const nameCell = createElement("td", "registry-name-cell");
      nameCell.append(createElement("span", "registry-name", entity.name));
      if (entity.region) nameCell.append(createElement("span", "registry-region", entity.region));

      const statusCell = createElement("td");
      statusCell.append(createElement("span", `registry-status is-${entity.status}`, humanize(entity.status)));
      if (entity.identity_status === "source_candidate") {
        statusCell.append(
          createElement(
            "span",
            "registry-identity-note",
            entity.coverage_discontinuous ? "Source candidate · coverage gaps" : "Source candidate",
          ),
        );
      }
      row.append(
        nameCell,
        createElement("td", "registry-era", entityEra(entity)),
        createElement("td", "registry-kind", entity.kind ? humanize(entity.kind) : "—"),
        statusCell,
      );
      elements.registryBody.append(row);
    }

    elements.registryShowing.textContent = matches.length
      ? `Showing ${formatInteger(visible.length)} of ${formatInteger(matches.length)} matching polities`
      : "";
    elements.registryShowMore.hidden = visible.length >= matches.length;
    if (!elements.registryShowMore.hidden) {
      const remaining = matches.length - visible.length;
      elements.registryShowMore.textContent = `Show ${formatInteger(Math.min(REGISTRY_PAGE_SIZE, remaining))} more`;
    }
  }

  function registryFilterSummary(matchCount, status, kind, query) {
    const filters = [];
    if (status !== "all") filters.push(`${humanize(status)} status`);
    if (kind !== "all") filters.push(humanize(kind));
    if (query) filters.push(`matching “${query}”`);
    const scope = filters.length ? ` for ${filters.join(" · ")}` : " across the full registry";
    return `${formatInteger(matchCount)} ${matchCount === 1 ? "polity" : "polities"}${scope}.`;
  }

  function renderMetadata() {
    const meta = state.data.meta;
    const coverageStatus = `${meta.status ?? ""} ${meta.coverage_status ?? ""}`;
    const demo =
      state.fallbackUsed ||
      Boolean(meta.demo || meta.is_demo || /demo|demonstration|preview/i.test(coverageStatus));
    const limited = !demo && meta.comprehensive === false;
    const warnings = extractCoverageWarnings(meta);

    elements.datasetBadge.classList.remove("is-live", "is-demo", "is-limited");
    elements.datasetBadge.classList.add(demo ? "is-demo" : limited ? "is-limited" : "is-live");
    elements.datasetBadge.lastChild.textContent = demo
      ? " Demonstration data"
      : limited
        ? " Limited dataset"
        : " Research dataset";

    const generated = meta.generated_at ?? meta.generated ?? meta.as_of ?? null;
    elements.generatedLabel.textContent = generated ? `Updated ${formatDate(generated)}` : "";

    const registryCoverage = state.data.registry.coverage;
    elements.coverageRegistryPolities.textContent = formatInteger(registryCoverage.registry_polities);
    elements.coverageRatedEntities.textContent = formatInteger(registryCoverage.rated_entities);
    elements.coverageRatedEvents.textContent = formatInteger(registryCoverage.rated_events);
    elements.coverageStagedRecords.textContent = formatInteger(registryCoverage.staged_source_records);

    if (demo || limited || warnings.length) {
      elements.datasetNotice.hidden = false;
      elements.noticeTitle.textContent = demo
        ? warnings.length
          ? "Demonstration data with coverage limits"
          : "Demonstration dataset"
        : limited
          ? "Incomplete research coverage"
          : "Coverage and comparability warning";

      elements.noticeCopy.textContent = state.fallbackUsed
        ? "results.json was unavailable, so this page is showing a small built-in preview. Its scores are illustrative only."
        : cleanOptionalText(meta.coverage_note) ??
          cleanOptionalText(meta.notice) ??
          (demo
            ? "Rankings are illustrative until the research dataset and its citations are complete."
            : limited
              ? "The registry and rated-event record are still incomplete; absence from either is not evidence of military inactivity."
            : "Some ratings are not directly comparable across the full dataset.");

      elements.noticeDetails.replaceChildren();
      for (const warning of warnings) {
        elements.noticeDetails.append(createElement("li", "", warning));
      }
      elements.noticeDetails.hidden = warnings.length === 0;
    } else {
      elements.datasetNotice.hidden = true;
    }

    const methodology = cleanOptionalText(meta.methodology_note) ?? cleanOptionalText(meta.methodology);
    if (methodology) elements.methodologyNote.textContent = methodology;

    const footerNote = cleanOptionalText(meta.footer_note) ?? cleanOptionalText(meta.coverage_note);
    if (footerNote) elements.footerCoverage.textContent = footerNote;
  }

  function extractCoverageWarnings(meta) {
    const warnings = [];
    const candidates = [
      meta.coverage_warnings,
      meta.warnings,
      meta.network_warning,
      meta.disconnected_network_warning,
      meta.comparison_warning,
      meta.coverage && meta.coverage.warnings,
      meta.network && meta.network.warning,
    ];

    for (const candidate of candidates) {
      for (const message of warningMessages(candidate)) {
        if (message && !warnings.includes(message)) warnings.push(message);
      }
    }

    const declaredComponents =
      finiteNumber(meta.network_components) ??
      finiteNumber(meta.component_count) ??
      finiteNumber(meta.network && meta.network.components);
    const rowComponents = new Set(
      state.data.leaderboard
        .map((row) => row.network_component)
        .filter((component) => component !== null && component !== undefined)
        .map(String),
    );
    const componentCount = declaredComponents ?? rowComponents.size;
    if (componentCount > 1 && !warnings.some((warning) => /component|disconnect/i.test(warning))) {
      warnings.push(
        `${formatInteger(componentCount)} disconnected comparison networks are present. Scores across those components carry extra comparability uncertainty.`,
      );
    }

    const auditWarnings = finiteNumber(meta.audit_warnings);
    if (auditWarnings > 0 && !warnings.some((warning) => /audit/i.test(warning))) {
      warnings.push(`${formatInteger(auditWarnings)} dataset audit warning${auditWarnings === 1 ? " remains" : "s remain"} for review.`);
    }

    return warnings.slice(0, 6);
  }

  function warningMessages(value) {
    if (value === null || value === undefined || value === false) return [];
    if (typeof value === "string") return [value];
    if (Array.isArray(value)) return value.flatMap(warningMessages);
    if (typeof value === "object") {
      return warningMessages(value.message ?? value.label ?? value.warning ?? value.detail);
    }
    return value === true ? ["The dataset reports a coverage limitation."] : [];
  }

  function scheduleRender() {
    cancelAnimationFrame(state.renderFrame);
    state.renderFrame = requestAnimationFrame(renderAll);
  }

  function renderAll() {
    if (!state.data) return;

    updatePerspectiveAvailability();
    elements.selectedYear.textContent = formatYear(state.selectedYear);
    elements.slider.value = String(state.selectedYear);
    elements.eventsYear.textContent = formatYear(state.selectedYear);

    const snapshotRows = getSnapshotRows(state.selectedYear, state.metric);
    state.visibleEntityIds = getTimelineEntityIds(snapshotRows);

    renderPins();
    renderChart(state.visibleEntityIds);
    renderLegend(state.visibleEntityIds);
    renderTimelineRanking(snapshotRows);
    renderLeaderboard(snapshotRows);
    renderMovers();
    renderEvents();
    renderMap();
    updateTimelineButtons();
    if (!elements.searchResultsWrap.hidden && elements.search.value.trim()) renderSearchResults();
  }

  function renderMap() {
    elements.mapYear.textContent = formatYear(state.selectedYear);
    if (!state.battleMap) return;
    state.battleMap.update({
      selectedYear: state.selectedYear,
      window: state.mapWindow,
      domain: state.mapDomain,
      layer: state.mapLayer,
      confidence: state.mapConfidence,
      locationStatus: state.mapLocationStatus,
      selectedEventId: state.selectedEventId,
    });
  }

  function isFullRatingHorizon() {
    return state.selectedYear >= state.latestRatedEventYear;
  }

  function updatePerspectiveAvailability() {
    const unavailable = !isFullRatingHorizon();
    for (const value of ["historical_success", "achievement"]) {
      const option = elements.perspective.querySelector(`option[value="${value}"]`);
      if (!option) continue;
      option.disabled = unavailable;
      option.title = unavailable ? "Available only when the selected year includes the complete rating ledger." : "";
    }
    if (unavailable && (state.perspective === "historical_success" || state.perspective === "achievement")) {
      state.perspective = "current";
      elements.perspective.value = "current";
    }
  }

  function entityHasRatedEventAsOf(entityId, year) {
    return countAtOrBefore(state.entityEventYears.get(entityId) ?? [], year) > 0;
  }

  function eventTrack(event) {
    const type = String(event && event.type ? event.type : "").toLocaleLowerCase();
    if (type.includes("engagement") || type.includes("battle") || type.includes("siege") || type.includes("raid")) {
      return "tactical";
    }
    if (type.includes("campaign")) return "operational";
    return "strategic";
  }

  function asOfEvidence(entityId, year, point) {
    let effectiveEvents = 0;
    let effectiveWars = 0;
    for (const event of state.entityEvents.get(entityId) ?? []) {
      if (!horizonContract.eventIsAvailable(event, year)) break;
      const weight = finiteNumber(event.evidence_weight) ?? 1;
      effectiveEvents += weight;
      if (eventTrack(event) === "strategic") effectiveWars += weight;
    }
    const uncertainty = finiteNumber(point && point.uncertainty);
    return {
      effectiveEvents,
      effectiveWars,
      established: effectiveEvents >= 5 && effectiveWars >= 3 && uncertainty !== null && uncertainty <= 200,
    };
  }

  function getSnapshotRows(year, metric) {
    return horizonContract
      .rankAtYear({
        entities: state.data.entities,
        series: state.data.series,
        events: state.data.events,
        year,
        metric,
        activeOnly: true,
      })
      .map((row) => ({ ...row, established: asOfEvidence(row.entity.id, year, row.point).established }));
  }

  function getTimelineEntityIds(snapshotRows) {
    const ids = [];
    for (const row of snapshotRows.slice(0, state.topN)) ids.push(row.entity.id);
    for (const id of state.pinned) {
      if (!ids.includes(id) && entityHasRatedEventAsOf(id, state.selectedYear)) ids.push(id);
    }
    return ids;
  }

  function renderPins() {
    elements.pinList.replaceChildren();
    let visiblePins = 0;
    for (const id of state.pinned) {
      const entity = state.entityById.get(id);
      if (!entity || !entityHasRatedEventAsOf(id, state.selectedYear)) continue;
      visiblePins += 1;
      const button = createElement("button", "pin-chip");
      button.type = "button";
      button.setAttribute("aria-label", `Unpin ${entity.name}`);
      button.append(createElement("span", "", entity.name), closeIcon());
      button.addEventListener("click", () => togglePin(id));
      elements.pinList.append(button);
    }
    const hiddenPins = state.pinned.size - visiblePins;
    if (hiddenPins > 0) {
      elements.pinList.append(
        createElement(
          "span",
          "pin-hidden-count",
          `${hiddenPins} pin${hiddenPins === 1 ? " is" : "s are"} outside this information horizon.`,
        ),
      );
    }
    elements.pinRow.hidden = state.pinned.size === 0;
  }

  function togglePin(entityId) {
    const entity = state.entityById.get(entityId);
    if (!entity || !state.ratedEntityIds.has(entityId)) return;

    if (state.pinned.has(entityId)) {
      state.pinned.delete(entityId);
      showToast(`${entity.name} unpinned.`);
    } else {
      if (!entityHasRatedEventAsOf(entityId, state.selectedYear)) {
        showToast(`${entity.name} has no rated evidence by ${formatYear(state.selectedYear)}.`);
        return;
      }
      if (state.pinned.size >= MAX_PINNED) {
        showToast(`You can pin up to ${MAX_PINNED} polities at once.`);
        return;
      }
      state.pinned.add(entityId);
      showToast(`${entity.name} pinned to the timeline.`);
    }
    renderAll();
  }

  function renderSearchResults() {
    const query = elements.search.value.trim().toLocaleLowerCase();
    if (!query) {
      closeSearchResults();
      return;
    }

    state.searchMatches = state.data.entities
      .filter((entity) => entityHasRatedEventAsOf(entity.id, state.selectedYear))
      .map((entity) => ({
        entity,
        rank: searchRank(entity, query),
      }))
      .filter((match) => match.rank < 100)
      .sort((a, b) => a.rank - b.rank || a.entity.name.localeCompare(b.entity.name))
      .slice(0, 8)
      .map((match) => match.entity);

    elements.searchResults.replaceChildren();
    if (!state.searchMatches.length) {
      const item = createElement("li", "search-result-button", "No matching polity");
      item.setAttribute("aria-disabled", "true");
      elements.searchResults.append(item);
    } else {
      state.searchMatches.forEach((entity, index) => {
        const item = createElement("li");
        const button = createElement("button", "search-result-button");
        button.type = "button";
        button.id = `search-option-${index}`;
        button.setAttribute("role", "option");
        button.setAttribute("aria-selected", String(index === state.searchIndex));
        if (index === state.searchIndex) button.classList.add("is-active");

        const text = createElement("span");
        text.append(
          createElement("span", "search-result-name", entity.name),
          createElement("span", "search-result-meta", entityDescriptor(entity)),
        );
        button.append(
          text,
          createElement("span", "search-result-action", state.pinned.has(entity.id) ? "Unpin" : "Pin"),
        );
        button.addEventListener("click", () => selectSearchResult(entity));
        item.append(button);
        elements.searchResults.append(item);
      });
    }

    elements.searchResultsWrap.hidden = false;
    elements.search.setAttribute("aria-expanded", "true");
    updateActiveSearchDescendant();
  }

  function searchRank(entity, query) {
    const name = entity.name.toLocaleLowerCase();
    const region = (entity.region ?? "").toLocaleLowerCase();
    const kind = (entity.kind ?? "").toLocaleLowerCase();
    if (name === query) return 0;
    if (name.startsWith(query)) return 1;
    if (name.includes(query)) return 2;
    if (region.includes(query) || kind.includes(query)) return 3;
    return 100;
  }

  function handleSearchKeyboard(event) {
    if (event.key === "Escape") {
      closeSearchResults();
      return;
    }

    if (event.key === "ArrowDown" || event.key === "ArrowUp") {
      event.preventDefault();
      if (elements.searchResultsWrap.hidden) renderSearchResults();
      if (!state.searchMatches.length) return;
      const change = event.key === "ArrowDown" ? 1 : -1;
      state.searchIndex = (state.searchIndex + change + state.searchMatches.length) % state.searchMatches.length;
      renderSearchResults();
      return;
    }

    if (event.key === "Enter" && state.searchMatches.length) {
      event.preventDefault();
      const index = state.searchIndex >= 0 ? state.searchIndex : 0;
      selectSearchResult(state.searchMatches[index]);
    }
  }

  function updateActiveSearchDescendant() {
    if (state.searchIndex >= 0) {
      elements.search.setAttribute("aria-activedescendant", `search-option-${state.searchIndex}`);
    } else {
      elements.search.removeAttribute("aria-activedescendant");
    }
  }

  function selectSearchResult(entity) {
    togglePin(entity.id);
    elements.search.value = "";
    closeSearchResults();
    elements.search.focus();
  }

  function closeSearchResults() {
    elements.searchResultsWrap.hidden = true;
    elements.search.setAttribute("aria-expanded", "false");
    elements.search.removeAttribute("aria-activedescendant");
    state.searchIndex = -1;
  }

  function renderChart(entityIds) {
    if (!state.data) return;

    hideChartTooltip();
    const svg = elements.chart;
    const width = Math.max(240, Math.round(elements.chartFrame.clientWidth || 900));
    const height = width <= 640 ? 350 : 430;
    const margins = {
      top: 24,
      right: width <= 520 ? 12 : 20,
      bottom: 48,
      left: width <= 520 ? 50 : 62,
    };
    const plotWidth = width - margins.left - margins.right;
    const plotHeight = height - margins.top - margins.bottom;
    const metric = state.metric;
    const chartMinYear = state.selectedYear <= state.minYear ? state.selectedYear - 1 : state.minYear;
    const chartMaxYear = state.selectedYear;

    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.replaceChildren();
    svg.append(
      svgElement("title", { id: "chart-title" }, `${METRIC_LABELS[metric]} military Elo rating timeline`),
      svgElement(
        "desc",
        { id: "chart-description" },
        `Step-line ratings for ${entityIds.length} visible polities through ${formatYear(chartMaxYear)}. No later outcomes are included.`,
      ),
    );

    const chartSeries = entityIds
      .map((id, index) => ({
        id,
        entity: state.entityById.get(id),
        points: horizonContract
          .authorizedSeriesThrough(state.data.series[id] ?? [], state.eventById, id, chartMaxYear)
          .filter((point) => point[metric] !== null),
        color: SERIES_COLORS[index % SERIES_COLORS.length],
        dash: DASH_PATTERNS[Math.floor(index / SERIES_COLORS.length) + (index % SERIES_COLORS.length === 0 ? 0 : 0)] ?? "7 4",
      }))
      .filter((series) => state.ratedEntityIds.has(series.id) && series.entity && series.points.length);

    elements.chartEmpty.hidden = chartSeries.length > 0;
    if (!chartSeries.length) {
      elements.chartSummary.textContent = "No visible rating series at this date.";
      return;
    }

    const domainValues = [];
    for (const series of chartSeries) {
      for (const point of series.points) {
        const uncertainty = point.uncertainty ?? 0;
        domainValues.push(point[metric] - uncertainty, point[metric] + uncertainty);
      }
    }

    let yMin = Math.min(...domainValues);
    let yMax = Math.max(...domainValues);
    if (!Number.isFinite(yMin) || !Number.isFinite(yMax)) {
      yMin = 1300;
      yMax = 1700;
    }
    // Fit the axis to the visible data (uncertainty bands included above).
    // Only a small floor is kept so near-flat series still get a readable
    // scale; a one-point rating move then spans ~10% of the plot instead of
    // disappearing into a fixed 100-point window.
    if (yMax - yMin < 10) {
      const center = (yMax + yMin) / 2;
      yMin = center - 5;
      yMax = center + 5;
    }
    const yPadding = (yMax - yMin) * 0.08;
    yMin -= yPadding;
    yMax += yPadding;

    const xScale = (year) => margins.left + ((year - chartMinYear) / (chartMaxYear - chartMinYear)) * plotWidth;
    const yScale = (value) => margins.top + ((yMax - value) / (yMax - yMin)) * plotHeight;
    const xInvert = (pixel) => chartMinYear + ((pixel - margins.left) / plotWidth) * (chartMaxYear - chartMinYear);

    const gridGroup = svgElement("g", { "aria-hidden": "true" });
    const yTicks = numericTicks(yMin, yMax, 6);
    for (const tick of yTicks) {
      const y = yScale(tick);
      gridGroup.append(
        svgElement("line", {
          class: "grid-line",
          x1: margins.left,
          x2: width - margins.right,
          y1: y,
          y2: y,
        }),
        svgElement(
          "text",
          { class: "tick-label", x: margins.left - 9, y: y + 4, "text-anchor": "end" },
          formatRating(tick),
        ),
      );
    }

    const xTicks = yearTicks(chartMinYear, chartMaxYear, width < 360 ? 3 : width <= 520 ? 4 : 7);
    for (const tick of xTicks) {
      const x = xScale(tick);
      gridGroup.append(
        svgElement("line", {
          class: "grid-line",
          x1: x,
          x2: x,
          y1: margins.top,
          y2: height - margins.bottom,
        }),
        svgElement(
          "text",
          { class: "tick-label", x, y: height - margins.bottom + 23, "text-anchor": "middle" },
          formatAxisYear(tick),
        ),
      );
    }

    gridGroup.append(
      svgElement("line", {
        class: "axis-line",
        x1: margins.left,
        x2: width - margins.right,
        y1: height - margins.bottom,
        y2: height - margins.bottom,
      }),
      svgElement(
        "text",
        {
          class: "axis-label",
          x: 13,
          y: margins.top + plotHeight / 2,
          transform: `rotate(-90 13 ${margins.top + plotHeight / 2})`,
          "text-anchor": "middle",
        },
        `${METRIC_LABELS[metric]} Elo`,
      ),
    );
    svg.append(gridGroup);

    const rugGroup = svgElement("g", { "aria-hidden": "true" });
    const availableEventYears = state.eventYears.filter((year) => year <= chartMaxYear);
    const rugYears = availableEventYears.length > 500 ? sampleEvenly(availableEventYears, 500) : availableEventYears;
    for (const year of rugYears) {
      const x = xScale(year);
      rugGroup.append(
        svgElement("line", {
          class: "event-rug",
          x1: x,
          x2: x,
          y1: height - margins.bottom + 1,
          y2: height - margins.bottom + 6,
        }),
      );
    }
    svg.append(rugGroup);

    const bands = svgElement("g", { "aria-hidden": "true" });
    const lines = svgElement("g", { "aria-hidden": "true" });
    chartSeries.forEach((series, index) => {
      const extended = extendSeries(series.points, series.entity);
      const uncertaintyPath = buildBandPath(extended, metric, xScale, yScale);
      if (uncertaintyPath) {
        bands.append(
          svgElement("path", {
            class: "uncertainty-band",
            d: uncertaintyPath,
            fill: series.color,
          }),
        );
      }

      const linePath = buildStepPath(extended, (point) => point[metric], xScale, yScale);
      const path = svgElement("path", {
        class: `rating-line${state.pinned.has(series.id) ? " is-pinned" : ""}`,
        d: linePath,
        stroke: series.color,
      });
      const dash = DASH_PATTERNS[Math.floor(index / SERIES_COLORS.length)] ?? "";
      if (dash) path.setAttribute("stroke-dasharray", dash);
      lines.append(path);
    });
    svg.append(bands, lines);

    const selectionX = xScale(state.selectedYear);
    const selection = svgElement("g", { "aria-hidden": "true" });
    selection.append(
      svgElement("line", {
        class: "selection-rule",
        x1: selectionX,
        x2: selectionX,
        y1: margins.top,
        y2: height - margins.bottom,
      }),
    );

    for (const series of chartSeries) {
      if (!isEntityActive(series.entity, state.selectedYear)) continue;
      const point = pointAt(series.id, state.selectedYear);
      if (!point || point[metric] === null) continue;
      selection.append(
        svgElement("circle", {
          class: "selection-dot",
          cx: selectionX,
          cy: yScale(point[metric]),
          r: state.pinned.has(series.id) ? 4.5 : 3.5,
          fill: series.color,
        }),
      );
    }
    svg.append(selection);

    const interaction = svgElement("rect", {
      class: "interaction-layer",
      x: margins.left,
      y: margins.top,
      width: plotWidth,
      height: plotHeight,
      role: "presentation",
    });
    interaction.addEventListener("pointermove", (event) => {
      const bounds = svg.getBoundingClientRect();
      const pixelX = clamp(event.clientX - bounds.left, margins.left, width - margins.right);
      const year = Math.round(xInvert(pixelX));
      showChartTooltip(event, pixelX, year, chartSeries);
    });
    interaction.addEventListener("pointerleave", hideChartTooltip);
    interaction.addEventListener("click", (event) => {
      const bounds = svg.getBoundingClientRect();
      const pixelX = clamp(event.clientX - bounds.left, margins.left, width - margins.right);
      jumpToYear(Math.round(xInvert(pixelX)));
    });
    svg.append(interaction);

    const selectedRows = chartSeries
      .map((series) => {
        if (!isEntityActive(series.entity, state.selectedYear)) return null;
        const point = pointAt(series.id, state.selectedYear);
        return point ? { series, point } : null;
      })
      .filter(Boolean)
      .sort((a, b) => b.point[metric] - a.point[metric]);

    if (selectedRows.length) {
      const leader = selectedRows[0];
      const uncertainty = formatUncertainty(leader.point.uncertainty);
      elements.chartSummary.textContent = `${leader.series.entity.name} leads the visible lines at ${formatRating(leader.point[metric])}${uncertainty ? ` ${uncertainty}` : ""} in ${formatYear(state.selectedYear)}.`;
    } else {
      elements.chartSummary.textContent = `No visible line is active in ${formatYear(state.selectedYear)}.`;
    }

    renderModernChart(entityIds);
  }

  // A second, fixed-window view of the same authorized series covering the
  // 250 years before the selected date, where most of the rated evidence
  // lives. Shares the horizon contract and colors with the main chart; the
  // hover tooltip stays on the main chart, click-to-jump works on both.
  function renderModernChart(entityIds) {
    const svg = elements.chartModern;
    if (!svg || !state.data) return;

    const width = Math.max(240, Math.round(elements.chartFrameModern.clientWidth || 900));
    const height = width <= 640 ? 300 : 360;
    const margins = {
      top: 24,
      right: width <= 520 ? 12 : 20,
      bottom: 48,
      left: width <= 520 ? 50 : 62,
    };
    const plotWidth = width - margins.left - margins.right;
    const plotHeight = height - margins.top - margins.bottom;
    const metric = state.metric;
    const windowMaxYear = state.modernEndYear ?? state.maxYear;
    const windowMinYear = windowMaxYear - 250;
    if (elements.modernSelectedYear) {
      elements.modernSelectedYear.textContent = formatYear(windowMaxYear);
    }

    svg.setAttribute("viewBox", `0 0 ${width} ${height}`);
    svg.replaceChildren();
    svg.append(
      svgElement("title", { id: "chart-title-modern" }, `${METRIC_LABELS[metric]} military Elo, ${formatYear(windowMinYear)} to ${formatYear(windowMaxYear)}`),
      svgElement(
        "desc",
        { id: "chart-description-modern" },
        `Step-line ratings over the 250 years through ${formatYear(windowMaxYear)}. No later outcomes are included.`,
      ),
    );

    const chartSeries = entityIds
      .map((id, index) => {
        const authorized = horizonContract
          .authorizedSeriesThrough(state.data.series[id] ?? [], state.eventById, id, windowMaxYear)
          .filter((point) => point[metric] !== null);
        const before = authorized.filter((point) => point.year <= windowMinYear);
        const inside = authorized.filter((point) => point.year > windowMinYear);
        const entry = before.length
          ? [{ ...before[before.length - 1], year: windowMinYear, _synthetic: true }]
          : [];
        return {
          id,
          entity: state.entityById.get(id),
          points: [...entry, ...inside],
          color: SERIES_COLORS[index % SERIES_COLORS.length],
        };
      })
      .filter((series) => state.ratedEntityIds.has(series.id) && series.entity && series.points.length);

    elements.chartEmptyModern.hidden = chartSeries.length > 0;
    if (!chartSeries.length) {
      elements.chartSummaryModern.textContent = "No visible rating series in this window.";
      return;
    }

    const domainValues = [];
    for (const series of chartSeries) {
      for (const point of series.points) {
        const uncertainty = point.uncertainty ?? 0;
        domainValues.push(point[metric] - uncertainty, point[metric] + uncertainty);
      }
    }
    let yMin = Math.min(...domainValues);
    let yMax = Math.max(...domainValues);
    if (!Number.isFinite(yMin) || !Number.isFinite(yMax)) {
      yMin = 1300;
      yMax = 1700;
    }
    if (yMax - yMin < 10) {
      const center = (yMax + yMin) / 2;
      yMin = center - 5;
      yMax = center + 5;
    }
    const yPadding = (yMax - yMin) * 0.08;
    yMin -= yPadding;
    yMax += yPadding;

    const yScale = (value) => margins.top + ((yMax - value) / (yMax - yMin)) * plotHeight;
    const xScale = (year) => margins.left + ((year - windowMinYear) / (windowMaxYear - windowMinYear)) * plotWidth;
    const xInvert = (pixel) => windowMinYear + ((pixel - margins.left) / plotWidth) * (windowMaxYear - windowMinYear);

    const gridGroup = svgElement("g", { "aria-hidden": "true" });
    for (const tick of numericTicks(yMin, yMax, 6)) {
      const y = yScale(tick);
      gridGroup.append(
        svgElement("line", { class: "grid-line", x1: margins.left, x2: width - margins.right, y1: y, y2: y }),
        svgElement("text", { class: "tick-label", x: margins.left - 9, y: y + 4, "text-anchor": "end" }, formatRating(tick)),
      );
    }
    for (const tick of yearTicks(windowMinYear, windowMaxYear, width < 360 ? 3 : width <= 520 ? 4 : 7)) {
      const x = xScale(tick);
      gridGroup.append(
        svgElement("line", { class: "grid-line", x1: x, x2: x, y1: margins.top, y2: height - margins.bottom }),
        svgElement("text", { class: "tick-label", x, y: height - margins.bottom + 23, "text-anchor": "middle" }, formatAxisYear(tick)),
      );
    }
    gridGroup.append(
      svgElement("line", {
        class: "axis-line",
        x1: margins.left,
        x2: width - margins.right,
        y1: height - margins.bottom,
        y2: height - margins.bottom,
      }),
      svgElement(
        "text",
        {
          class: "axis-label",
          x: 13,
          y: margins.top + plotHeight / 2,
          transform: `rotate(-90 13 ${margins.top + plotHeight / 2})`,
          "text-anchor": "middle",
        },
        `${METRIC_LABELS[metric]} Elo`,
      ),
    );
    svg.append(gridGroup);

    const rugGroup = svgElement("g", { "aria-hidden": "true" });
    const windowEventYears = state.eventYears.filter((year) => year > windowMinYear && year <= windowMaxYear);
    const rugYears = windowEventYears.length > 500 ? sampleEvenly(windowEventYears, 500) : windowEventYears;
    for (const year of rugYears) {
      const x = xScale(year);
      rugGroup.append(
        svgElement("line", { class: "event-rug", x1: x, x2: x, y1: height - margins.bottom + 1, y2: height - margins.bottom + 6 }),
      );
    }
    svg.append(rugGroup);

    const bands = svgElement("g", { "aria-hidden": "true" });
    const lines = svgElement("g", { "aria-hidden": "true" });
    chartSeries.forEach((series, index) => {
      const extended = extendSeries(series.points, series.entity);
      const uncertaintyPath = buildBandPath(extended, metric, xScale, yScale);
      if (uncertaintyPath) {
        bands.append(svgElement("path", { class: "uncertainty-band", d: uncertaintyPath, fill: series.color }));
      }
      const path = svgElement("path", {
        class: `rating-line${state.pinned.has(series.id) ? " is-pinned" : ""}`,
        d: buildStepPath(extended, (point) => point[metric], xScale, yScale),
        stroke: series.color,
      });
      const dash = DASH_PATTERNS[Math.floor(index / SERIES_COLORS.length)] ?? "";
      if (dash) path.setAttribute("stroke-dasharray", dash);
      lines.append(path);
    });
    svg.append(bands, lines);

    if (state.selectedYear >= windowMinYear && state.selectedYear <= windowMaxYear) {
      const selectionX = xScale(state.selectedYear);
      const selection = svgElement("g", { "aria-hidden": "true" });
      selection.append(
        svgElement("line", {
          class: "selection-rule",
          x1: selectionX,
          x2: selectionX,
          y1: margins.top,
          y2: height - margins.bottom,
        }),
      );
      for (const series of chartSeries) {
        if (!isEntityActive(series.entity, state.selectedYear)) continue;
        const point = pointAt(series.id, state.selectedYear);
        if (!point || point[metric] === null) continue;
        selection.append(
          svgElement("circle", {
            class: "selection-dot",
            cx: selectionX,
            cy: yScale(point[metric]),
            r: state.pinned.has(series.id) ? 4.5 : 3.5,
            fill: series.color,
          }),
        );
      }
      svg.append(selection);
    }

    const interaction = svgElement("rect", {
      class: "interaction-layer",
      x: margins.left,
      y: margins.top,
      width: plotWidth,
      height: plotHeight,
      role: "presentation",
    });
    interaction.addEventListener("click", (event) => {
      const bounds = svg.getBoundingClientRect();
      const pixelX = clamp(event.clientX - bounds.left, margins.left, width - margins.right);
      jumpToYear(Math.round(xInvert(pixelX)));
    });
    svg.append(interaction);

    const activeRows = chartSeries
      .map((series) => {
        if (!isEntityActive(series.entity, windowMaxYear)) return null;
        const point = pointAt(series.id, windowMaxYear);
        return point ? { series, point } : null;
      })
      .filter(Boolean)
      .sort((a, b) => b.point[metric] - a.point[metric]);
    if (activeRows.length) {
      const leader = activeRows[0];
      elements.chartSummaryModern.textContent = `${formatYear(windowMinYear)}–${formatYear(windowMaxYear)}: ${leader.series.entity.name} leads at ${formatRating(leader.point[metric])}.`;
    } else {
      elements.chartSummaryModern.textContent = `No visible line is active in ${formatYear(windowMaxYear)}.`;
    }
  }

  function extendSeries(points, entity) {
    if (!points.length) return [];
    const extended = points.map((point) => ({ ...point }));
    const last = extended[extended.length - 1];
    const endYear = Math.min(state.selectedYear, entity.end_year ?? state.selectedYear);
    if (endYear > last.year) {
      extended.push({ ...last, year: endYear, _synthetic: true });
    }
    return extended;
  }

  function buildStepPath(points, valueAccessor, xScale, yScale) {
    if (!points.length) return "";
    const coordinates = stepCoordinates(points, valueAccessor, xScale, yScale);
    return coordinates.map(([x, y], index) => `${index ? "L" : "M"}${round2(x)},${round2(y)}`).join(" ");
  }

  function buildBandPath(points, metric, xScale, yScale) {
    if (!points.some((point) => (point.uncertainty ?? 0) > 0)) return "";
    const upper = stepCoordinates(points, (point) => point[metric] + (point.uncertainty ?? 0), xScale, yScale);
    const lower = stepCoordinates(points, (point) => point[metric] - (point.uncertainty ?? 0), xScale, yScale).reverse();
    const all = upper.concat(lower);
    return `${all.map(([x, y], index) => `${index ? "L" : "M"}${round2(x)},${round2(y)}`).join(" ")} Z`;
  }

  function stepCoordinates(points, valueAccessor, xScale, yScale) {
    const coordinates = [[xScale(points[0].year), yScale(valueAccessor(points[0]))]];
    for (let index = 1; index < points.length; index += 1) {
      const previous = points[index - 1];
      const current = points[index];
      const x = xScale(current.year);
      coordinates.push([x, yScale(valueAccessor(previous))], [x, yScale(valueAccessor(current))]);
    }
    return coordinates;
  }

  function showChartTooltip(event, pixelX, year, chartSeries) {
    const rows = chartSeries
      .map((series) => {
        if (!isEntityActive(series.entity, year)) return null;
        const point = pointAt(series.id, year);
        return point && point[state.metric] !== null ? { series, point } : null;
      })
      .filter(Boolean)
      .sort((a, b) => b.point[state.metric] - a.point[state.metric])
      .slice(0, 6);

    elements.chartTooltip.replaceChildren(createElement("div", "tooltip-year", formatYear(year)));
    if (!rows.length) {
      elements.chartTooltip.append(createElement("div", "tooltip-name", "No visible active rating"));
    } else {
      for (const row of rows) {
        const line = createElement("div", "tooltip-row");
        const swatch = createElement("span", "tooltip-swatch");
        swatch.style.setProperty("--swatch", row.series.color);
        const uncertainty = row.point.uncertainty !== null ? ` ±${formatCompactNumber(row.point.uncertainty)}` : "";
        line.append(
          swatch,
          createElement("span", "tooltip-name", row.series.entity.name),
          createElement("span", "tooltip-value", `${formatRating(row.point[state.metric])}${uncertainty}`),
        );
        elements.chartTooltip.append(line);
      }
    }

    elements.chartTooltip.hidden = false;
    const frameBounds = elements.chartFrame.getBoundingClientRect();
    const tooltipBounds = elements.chartTooltip.getBoundingClientRect();
    const pointerY = event.clientY - frameBounds.top;
    let left = pixelX + 14;
    if (left + tooltipBounds.width > frameBounds.width - 4) left = pixelX - tooltipBounds.width - 14;
    left = clamp(left, 4, Math.max(4, frameBounds.width - tooltipBounds.width - 4));
    const top = clamp(pointerY - tooltipBounds.height / 2, 4, Math.max(4, frameBounds.height - tooltipBounds.height - 4));
    elements.chartTooltip.style.left = `${left}px`;
    elements.chartTooltip.style.top = `${top}px`;
  }

  function hideChartTooltip() {
    elements.chartTooltip.hidden = true;
  }

  function renderLegend(entityIds) {
    elements.chartLegend.replaceChildren();
    entityIds.forEach((id, index) => {
      const entity = state.entityById.get(id);
      if (!entity) return;
      const item = createElement("li");
      const button = createElement("button", "legend-button");
      button.type = "button";
      button.setAttribute("aria-pressed", String(state.pinned.has(id)));
      button.setAttribute("aria-label", `${state.pinned.has(id) ? "Unpin" : "Pin"} ${entity.name}`);
      const swatch = createElement("span", "legend-swatch");
      swatch.style.setProperty("--swatch", SERIES_COLORS[index % SERIES_COLORS.length]);
      const point = isEntityActive(entity, state.selectedYear) ? pointAt(id, state.selectedYear) : null;
      button.append(
        swatch,
        createElement("span", "legend-name", entity.name),
        createElement(
          "span",
          "legend-value",
          point && point[state.metric] !== null ? formatRating(point[state.metric]) : "inactive",
        ),
      );
      button.addEventListener("click", () => togglePin(id));
      item.append(button);
      elements.chartLegend.append(item);
    });
  }

  function renderTimelineRanking(snapshotRows) {
    const rows = snapshotRows.slice(0, state.topN);
    elements.timelineRankingTitle.textContent = `Top ${state.topN} at ${formatYear(state.selectedYear)}`;
    elements.timelineRankingMetric.textContent = `${METRIC_LABELS[state.metric]} Elo`;
    elements.timelineRankingList.replaceChildren();
    elements.timelineRankingEmpty.hidden = rows.length > 0;

    rows.forEach((row, index) => {
      const item = createElement("li", "timeline-ranking-item");
      const rank = createElement("span", "timeline-ranking-rank", String(index + 1));
      rank.setAttribute("aria-hidden", "true");

      const identity = createElement("div", "timeline-ranking-identity");
      const button = createElement("button", "timeline-ranking-name", row.entity.name);
      button.type = "button";
      button.setAttribute("aria-pressed", String(state.pinned.has(row.entity.id)));
      button.setAttribute("aria-label", `${state.pinned.has(row.entity.id) ? "Unpin" : "Pin"} ${row.entity.name}`);
      button.addEventListener("click", () => togglePin(row.entity.id));

      const movement = finiteNumber(row.lastMove);
      const details = [
        movement === null ? "no prior move" : `last move ${formatSigned(movement, Math.abs(movement) < 10 ? 1 : 0)}`,
        row.established === false ? "low coverage" : "coverage threshold met",
      ];
      identity.append(button, createElement("span", "timeline-ranking-status", details.join(" · ")));

      const score = createElement("div", "timeline-ranking-score");
      score.append(
        createElement("strong", "", formatRating(row.value)),
        createElement("span", "", METRIC_LABELS[state.metric]),
      );
      item.append(rank, identity, score);
      elements.timelineRankingList.append(item);
    });
  }

  function renderLeaderboard(snapshotRows) {
    const perspective = state.perspective;
    const isCurrent = perspective === "current";
    const rows = isCurrent
      ? state.metric === "composite"
        ? snapshotRows
        : getSnapshotRows(state.selectedYear, "composite")
      : getPerspectiveRows(perspective, state.selectedYear);
    const visibleRows = rows.slice(0, Math.max(10, state.topN));
    const headers = elements.leaderboardBody.closest("table").querySelectorAll("thead th");

    if (isCurrent) {
      elements.leaderboardTitle.textContent = `Leaderboard at ${formatYear(state.selectedYear)}`;
      elements.leaderboardMetric.textContent = "Composite Elo";
      elements.leaderboardCaption.textContent = `Composite military Elo leaderboard at ${formatYear(state.selectedYear)}`;
      headers[2].textContent = "Rating ± uncertainty";
      headers[3].textContent = "Last move";
    } else {
      elements.leaderboardTitle.textContent = `Leaderboard through ${formatYear(state.selectedYear)}`;
      elements.leaderboardMetric.textContent = PERSPECTIVE_LABELS[perspective];
      elements.leaderboardCaption.textContent = `Military leaderboard through ${formatYear(state.selectedYear)} by ${PERSPECTIVE_LABELS[perspective].toLowerCase()}`;
      headers[2].textContent = PERSPECTIVE_LABELS[perspective];
      headers[3].textContent = "Evidence status";
    }

    elements.leaderboardBody.replaceChildren();
    elements.leaderboardEmpty.hidden = visibleRows.length > 0;

    visibleRows.forEach((row, index) => {
      const tr = createElement("tr");
      tr.append(createElement("td", "rank-number", String(index + 1)));

      const entityCell = createElement("td", "entity-cell");
      const entityButton = createElement("button", "entity-button");
      entityButton.type = "button";
      entityButton.setAttribute("aria-pressed", String(state.pinned.has(row.entity.id)));
      entityButton.setAttribute("aria-label", `${state.pinned.has(row.entity.id) ? "Unpin" : "Pin"} ${row.entity.name}`);
      entityButton.append(pinIcon(state.pinned.has(row.entity.id)), createElement("span", "", row.entity.name));
      entityButton.addEventListener("click", () => togglePin(row.entity.id));
      entityCell.append(entityButton);

      if (row.established === false) {
        entityCell.append(createElement("span", "provisional-badge", "Low coverage"));
      }

      const descriptorParts = [row.entity.kind, row.entity.region].filter(Boolean);
      if (row.summary && row.summary.network_component !== null && hasMultipleNetworkComponents()) {
        descriptorParts.push(`network ${row.summary.network_component}`);
      }
      entityCell.append(createElement("span", "entity-subline", descriptorParts.join(" · ") || entityEraThrough(row.entity, state.selectedYear)));
      tr.append(entityCell);

      if (isCurrent) {
        const ratingCell = createElement("td");
        ratingCell.append(
          createElement("span", "rating-main", formatRating(row.value)),
          createElement(
            "span",
            "uncertainty-label",
            row.point.uncertainty !== null ? `± ${formatCompactNumber(row.point.uncertainty)} rating points` : "uncertainty unavailable",
          ),
        );
        tr.append(ratingCell, deltaCell(row.lastMove), createElement("td", "", formatInteger(row.events)));
      } else {
        const scoreCell = createElement("td");
        scoreCell.append(
          createElement("span", "rating-main", formatPerspectiveValue(perspective, row.value)),
          createElement("span", "uncertainty-label", perspectiveContext(perspective, row)),
        );
        tr.append(scoreCell);

        const statusCell = createElement("td");
        statusCell.append(
          createElement(
            "span",
            row.established === false ? "status-text provisional" : "status-text established",
            row.established === false ? "Low coverage" : "Coverage threshold met",
          ),
        );
        if (row.summary && row.summary.confidence !== null) {
          statusCell.append(createElement("span", "uncertainty-label", `${formatConfidence(row.summary.confidence)} confidence`));
        }
        tr.append(statusCell, createElement("td", "", formatInteger(row.events ?? 0)));
      }

      elements.leaderboardBody.append(tr);
    });
  }

  function getPerspectiveRows(perspective, year) {
    if ((perspective === "historical_success" || perspective === "achievement") && !isFullRatingHorizon()) return [];

    const rows = [];
    for (const entity of state.data.entities) {
      const events = countAtOrBefore(state.entityEventYears.get(entity.id) ?? [], year);
      if (events < 1) continue;
      const points = horizonContract.authorizedSeriesThrough(
        state.data.series[entity.id] ?? [],
        state.eventById,
        entity.id,
        year,
      );
      const point = points[points.length - 1] ?? null;
      if (!point) continue;

      let value = null;
      let peakYear = null;
      let summary = null;
      if (perspective === "peak") {
        for (const candidate of points) {
          if (!Number.isFinite(candidate.composite)) continue;
          if (value === null || candidate.composite > value) {
            value = candidate.composite;
            peakYear = candidate.year;
          }
        }
      } else if (perspective === "sustained") {
        value = median(horizonContract.ratedSeriesThrough(points, year).map((candidate) => candidate.composite));
      } else {
        summary = state.leaderboardById.get(entity.id) ?? null;
        value = finiteNumber(summary && summary[perspective]);
      }

      if (!Number.isFinite(value)) continue;
      rows.push({
        entity,
        point,
        summary,
        value,
        peak_year: peakYear,
        events,
        established: asOfEvidence(entity.id, year, point).established,
      });
    }
    return rows.sort((left, right) => right.value - left.value || left.entity.name.localeCompare(right.entity.name));
  }

  function perspectiveContext(perspective, row) {
    if (perspective === "peak" && row.peak_year !== null) return `reached ${formatYear(row.peak_year)}`;
    if (row.point && row.point.uncertainty !== null) return `model uncertainty ± ${formatCompactNumber(row.point.uncertainty)}`;
    if (perspective === "historical_success") return "normalized 0–100 index";
    return `modeled through ${formatYear(state.selectedYear)}`;
  }

  function formatPerspectiveValue(perspective, value) {
    if (perspective === "historical_success") return `${formatDecimal(value, 1)} / 100`;
    return formatRating(value);
  }

  function hasMultipleNetworkComponents() {
    const components = new Set(
      state.data.leaderboard
        .map((row) => row.network_component)
        .filter((component) => component !== null && component !== undefined)
        .map(String),
    );
    return components.size > 1;
  }

  function deltaCell(value) {
    const cell = createElement("td");
    const numeric = finiteNumber(value);
    const className = numeric === null || Math.abs(numeric) < 0.05 ? "neutral" : numeric > 0 ? "positive" : "negative";
    const label = numeric === null ? "—" : formatSigned(numeric, Math.abs(numeric) < 10 ? 1 : 0);
    cell.append(createElement("span", `delta ${className}`, label));
    return cell;
  }

  function renderMovers() {
    const span = state.selectedYear - state.minYear;
    const windowYears = span > 3000 ? 50 : span > 1000 ? 30 : 25;
    const baselineYear = Math.max(state.minYear, state.selectedYear - windowYears);
    elements.momentumWindow.textContent = `${windowYears}-year change`;

    const movers = [];
    for (const entity of state.data.entities) {
      if (!state.ratedEntityIds.has(entity.id)) continue;
      if (!isEntityActive(entity, state.selectedYear)) continue;
      if (countAtOrBefore(state.entityEventYears.get(entity.id) ?? [], state.selectedYear) < 1) continue;
      const current = pointAt(entity.id, state.selectedYear);
      if (!current || current[state.metric] === null) continue;

      let baseline = pointAt(entity.id, baselineYear);
      if (!baseline) {
        const availablePoints = horizonContract.authorizedSeriesThrough(
          state.data.series[entity.id] ?? [],
          state.eventById,
          entity.id,
          current.year,
        );
        if (availablePoints.length > 1) baseline = availablePoints[availablePoints.length - 2];
      }
      if (!baseline || baseline === current || baseline[state.metric] === null) continue;
      const change = current[state.metric] - baseline[state.metric];
      if (Math.abs(change) < 0.05) continue;
      movers.push({ entity, change, from: baseline.year, to: current.year });
    }

    const risers = movers.filter((row) => row.change > 0).sort((a, b) => b.change - a.change).slice(0, 4);
    const fallers = movers.filter((row) => row.change < 0).sort((a, b) => a.change - b.change).slice(0, 4);

    renderMoverList(elements.risersList, risers, "positive");
    renderMoverList(elements.fallersList, fallers, "negative");
    elements.moversEmpty.hidden = risers.length + fallers.length > 0;
  }

  function renderMoverList(list, rows, deltaClass) {
    list.replaceChildren();
    for (const row of rows) {
      const item = createElement("li");
      const name = createElement("span", "mover-name", row.entity.name);
      name.append(createElement("span", "mover-context", `${formatYear(row.from)} to ${formatYear(row.to)}`));
      item.append(name, createElement("span", `delta ${deltaClass}`, formatSigned(row.change, Math.abs(row.change) < 10 ? 1 : 0)));
      list.append(item);
    }
  }

  function renderEvents() {
    let events = nearestEvents(state.selectedYear, 9);
    const selectedEvent = state.eventById.get(state.selectedEventId);
    const selectedMatchesDomain =
      selectedEvent &&
      horizonContract.eventIsAvailable(selectedEvent, state.selectedYear) &&
      (state.eventDomain === "all" || selectedEvent.domain === state.eventDomain);
    if (
      selectedMatchesDomain &&
      horizonContract.eventAvailabilityYear(selectedEvent) === state.selectedYear &&
      !events.some((event) => event.id === selectedEvent.id)
    ) {
      events = [selectedEvent, ...events.filter((event) => event.id !== selectedEvent.id)].slice(0, 9);
    }
    elements.eventList.replaceChildren();
    elements.eventsEmpty.hidden = events.length > 0;

    if (!events.length) {
      renderEventDetail(null);
      return;
    }

    if (!state.selectedEventId || !events.some((event) => event.id === state.selectedEventId)) {
      const prior = events.find((event) => horizonContract.eventIsAvailable(event, state.selectedYear));
      state.selectedEventId = (prior ?? events[0]).id;
    }

    for (const event of events) {
      const item = createElement("li");
      const button = createElement("button", "event-item-button");
      button.type = "button";
      button.setAttribute("aria-current", String(event.id === state.selectedEventId));
      button.append(
        createElement("span", "event-item-year", formatEventDate(event)),
        eventListText(event),
      );
      button.addEventListener("click", () => {
        state.selectedEventId = event.id;
        renderEvents();
      });
      item.append(button);
      elements.eventList.append(item);
    }

    renderEventDetail(state.eventById.get(state.selectedEventId) ?? events[0]);
  }

  function eventListText(event) {
    const wrapper = createElement("span");
    wrapper.append(
      createElement("span", "event-item-name", event.name),
      createElement(
        "span",
        "event-item-meta",
        [
          humanize(event.domain),
          humanize(event.war_type ?? event.type),
          relativeYearLabel(horizonContract.eventAvailabilityYear(event), state.selectedYear),
          formatConfidence(event.confidence),
        ]
          .filter(Boolean)
          .join(" · "),
      ),
    );
    return wrapper;
  }

  function renderEventDetail(event) {
    elements.eventDetail.replaceChildren();
    if (!event || !horizonContract.eventIsAvailable(event, state.selectedYear)) {
      const placeholder = createElement("div", "event-detail-placeholder");
      placeholder.append(documentIcon(), createElement("p", "", "No event record is available near this date."));
      elements.eventDetail.append(placeholder);
      return;
    }

    const header = createElement("header", "event-detail-header");
    const titleWrap = createElement("div");
    titleWrap.append(
      createElement("div", "event-date", formatEventDate(event)),
      createElement("h3", "", event.name),
    );

    const confidence = createElement("div", "confidence-gauge");
    confidence.append(
      createElement("strong", "", formatConfidence(event.confidence)),
      createElement("span", "", "source confidence"),
    );
    header.append(titleWrap, confidence);
    elements.eventDetail.append(header);

    elements.eventDetail.append(
      createElement(
        "p",
        "event-summary",
        event.summary ?? "This event record does not yet include a narrative summary.",
      ),
    );

    if (event.hced_candidate_id) {
      elements.eventDetail.append(
        createElement(
          "p",
          "hced-candidate-binding",
          `HCED candidate ID: ${event.hced_candidate_id}`,
        ),
      );
    }

    if (event.location_provenance) {
      const location = createElement("section", "location-assertion");
      location.append(createElement("h4", "", "Source-transcribed location"));
      const values = createElement("dl", "location-values");
      if (event.modern_location_country) {
        addFact(values, "Source geographic-jurisdiction label", event.modern_location_country);
      }
      const point = locationContract.formatPoint(event.geometry);
      if (point) {
        addFact(values, "Point [longitude, latitude]", point);
      }
      addFact(values, "HCED source record", event.location_provenance.source_record_id);
      location.append(
        values,
        createElement(
          "p",
          "location-warning",
          "Modern HCED location notice — " + locationContract.LOCATION_WARNING,
        ),
      );
      elements.eventDetail.append(location);
    }

    const facts = createElement("dl", "event-facts");
    addFact(facts, "Event type", humanize(event.type) || "Not classified");
    addFact(facts, "War type", humanize(event.war_type) || "Not classified");
    addFact(facts, "Domain", humanize(event.domain) || "Not classified");
    addFact(facts, "Geographic scope", humanize(event.geographic_scope) || "Not classified");
    addFact(facts, "Scale", formatModelField(event.scale));
    addFact(facts, "Stakes", formatModelField(event.stakes));
    elements.eventDetail.append(facts);

    elements.eventDetail.append(createElement("h4", "", "Participant outcome coding"));
    if (event.participants.length) {
      const tableWrap = createElement("div", "table-wrap participant-table");
      const table = createElement("table");
      const caption = createElement("caption", "sr-only", `Participants and modeled outcomes for ${event.name}`);
      const head = createElement("thead");
      const headRow = createElement("tr");
      for (const label of ["Polity", "Side", "Result class", "Importance", "Termination", "Utility", "Elo Δ"]) {
        const th = createElement("th", "", label);
        th.scope = "col";
        headRow.append(th);
      }
      head.append(headRow);

      const body = createElement("tbody");
      for (const participant of event.participants) {
        const row = createElement("tr");
        const entity = state.entityById.get(participant.entity_id);
        row.append(
          createElement("td", "", entity ? entity.name : participant.entity_id),
          createElement("td", "", humanize(participant.side) || "—"),
        );
        const resultCell = createElement("td");
        const result = humanize(participant.result_class) || "Unclassified";
        const pill = createElement("span", "result-pill", result);
        pill.dataset.result = String(participant.result_class ?? "").toLocaleLowerCase();
        resultCell.append(pill);
        row.append(
          resultCell,
          createElement("td", "", formatModelField(participant.importance)),
          createElement("td", "", humanize(participant.termination) || "—"),
          createElement("td", "", formatUtility(participant.utility)),
          createElement("td", "", participant.delta === null ? "—" : formatSigned(participant.delta, 1)),
        );
        body.append(row);
      }
      table.append(caption, head, body);
      tableWrap.append(table);
      elements.eventDetail.append(tableWrap);
    } else {
      elements.eventDetail.append(createElement("p", "empty-state", "Participant outcomes have not been coded for this event."));
    }

    elements.eventDetail.append(createElement("h4", "", `Sources (${event.sources.length})`));
    const outcomeFamilySummary = event.outcome_source_family_ids.length
      ? `Direct outcome family: ${event.outcome_source_family_ids.map((family) => humanize(family)).join(", ")}.`
      : "Direct outcome family: unmapped pending claim-level locator review.";
    elements.eventDetail.append(createElement("p", "source-contract", outcomeFamilySummary));
    const sources = createElement("ul", "source-list");
    if (!event.sources.length) {
      sources.append(createElement("li", "", "No linked source in this record."));
    } else {
      for (const source of event.sources) {
        const item = createElement("li");
        const safeUrl = safeHttpUrl(source.url);
        if (safeUrl) {
          const link = createElement("a", "", "");
          link.href = safeUrl;
          link.target = "_blank";
          link.rel = "noopener noreferrer";
          link.append(externalLinkIcon(), createElement("span", "", source.title));
          item.append(link);
        } else {
          const label = createElement("span");
          label.append(documentSmallIcon(), createElement("span", "", source.title));
          item.append(label);
        }
        const outcomeSubsetStatus = event.outcome_source_ids.includes(source.id)
          ? "Outcome subset: direct"
          : event.outcome_source_ids.length
            ? "Outcome subset: provenance only"
            : "Outcome subset: unmapped";
        const sourceDetails = [
          outcomeSubsetStatus,
          source.id ? `Source ID: ${source.id}` : null,
          source.source_family_id ? `Family: ${source.source_family_id}` : null,
          source.evidence_roles.length
            ? `Roles: ${source.evidence_roles.map((role) => humanize(role)).join(", ")}`
            : null,
        ].filter(Boolean);
        if (sourceDetails.length) {
          item.append(createElement("div", "source-metadata", sourceDetails.join(" · ")));
        }
        sources.append(item);
      }
    }
    elements.eventDetail.append(sources);
  }

  function nearestEvents(year, count) {
    return state.data.events
      .filter((event) => state.eventDomain === "all" || event.domain === state.eventDomain)
      .filter((event) => horizonContract.eventIsAvailable(event, year))
      .sort(
        (left, right) =>
          horizonContract.eventAvailabilityYear(right) - horizonContract.eventAvailabilityYear(left) ||
          right.year - left.year ||
          left.name.localeCompare(right.name),
      )
      .slice(0, count);
  }

  function jumpToAdjacentEvent(direction) {
    if (!state.eventYears.length) return;
    const index = lowerBound(state.eventYears, state.selectedYear, (year) => year);
    let target;
    if (direction < 0) {
      target = index < state.eventYears.length && state.eventYears[index] === state.selectedYear ? state.eventYears[index - 1] : state.eventYears[index - 1];
    } else {
      target = index < state.eventYears.length && state.eventYears[index] === state.selectedYear ? state.eventYears[index + 1] : state.eventYears[index];
    }
    if (target !== undefined) jumpToYear(target);
  }

  function updateTimelineButtons() {
    const index = lowerBound(state.eventYears, state.selectedYear, (year) => year);
    const atExact = index < state.eventYears.length && state.eventYears[index] === state.selectedYear;
    elements.previousEvent.disabled = index === 0;
    elements.nextEvent.disabled = atExact ? index >= state.eventYears.length - 1 : index >= state.eventYears.length;
  }

  function jumpToYear(year) {
    state.selectedYear = clamp(Math.round(year), state.minYear, state.maxYear);
    elements.slider.value = String(state.selectedYear);
    renderAll();
  }

  function pointAt(entityId, year) {
    const points = state.data.series[entityId] ?? [];
    const available = horizonContract.authorizedSeriesThrough(points, state.eventById, entityId, year);
    return available[available.length - 1] ?? null;
  }

  function isEntityActive(entity, year) {
    const points = state.data.series[entity.id] ?? [];
    const firstYear = entity.start_year ?? points[0]?.year ?? -Infinity;
    const lastYear = entity.end_year ?? Infinity;
    return year >= firstYear && year <= lastYear;
  }

  function lowerBound(array, value, accessor) {
    let low = 0;
    let high = array.length;
    while (low < high) {
      const middle = (low + high) >>> 1;
      if (accessor(array[middle]) < value) low = middle + 1;
      else high = middle;
    }
    return low;
  }

  function countAtOrBefore(sortedYears, year) {
    let low = 0;
    let high = sortedYears.length;
    while (low < high) {
      const middle = (low + high) >>> 1;
      if (sortedYears[middle] <= year) low = middle + 1;
      else high = middle;
    }
    return low;
  }

  function yearTicks(min, max, desiredCount) {
    const step = niceStep((max - min) / Math.max(1, desiredCount - 1));
    const first = Math.ceil(min / step) * step;
    const ticks = [];
    for (let value = first; value <= max + step * 0.001; value += step) ticks.push(Math.round(value));
    return ticks.length ? ticks : [min, max];
  }

  function numericTicks(min, max, desiredCount) {
    const step = niceStep((max - min) / Math.max(1, desiredCount - 1));
    const first = Math.ceil(min / step) * step;
    const ticks = [];
    for (let value = first; value <= max + step * 0.001; value += step) ticks.push(value);
    return ticks;
  }

  function niceStep(roughStep) {
    if (!Number.isFinite(roughStep) || roughStep <= 0) return 1;
    const power = 10 ** Math.floor(Math.log10(roughStep));
    const error = roughStep / power;
    const factor = error >= 7.5 ? 10 : error >= 3.5 ? 5 : error >= 1.5 ? 2 : 1;
    return factor * power;
  }

  function sampleEvenly(values, maxItems) {
    if (values.length <= maxItems) return values;
    const result = [];
    const stride = values.length / maxItems;
    for (let index = 0; index < maxItems; index += 1) result.push(values[Math.floor(index * stride)]);
    return result;
  }

  function createElement(tag, className = "", text = null) {
    const element = document.createElement(tag);
    if (className) element.className = className;
    if (text !== null && text !== undefined) element.textContent = String(text);
    return element;
  }

  function svgElement(tag, attributes = {}, text = null) {
    const element = document.createElementNS(SVG_NS, tag);
    for (const [name, value] of Object.entries(attributes)) {
      if (value !== null && value !== undefined) element.setAttribute(name, String(value));
    }
    if (text !== null && text !== undefined) element.textContent = String(text);
    return element;
  }

  function closeIcon() {
    const svg = svgElement("svg", { viewBox: "0 0 16 16", "aria-hidden": "true" });
    svg.append(svgElement("path", { d: "m4 4 8 8m0-8-8 8" }));
    return svg;
  }

  function pinIcon(filled) {
    const svg = svgElement("svg", { viewBox: "0 0 20 20", "aria-hidden": "true" });
    svg.append(svgElement("path", { d: "m7.2 3.2 5.7.1-.9 4 2.6 2.6-3.2 1.4-2.7 5.5-.7-5.9-4-2.5 3.6-1.1.6-4.1Z", fill: filled ? "currentColor" : "none" }));
    return svg;
  }

  function documentIcon() {
    const svg = svgElement("svg", { viewBox: "0 0 48 48", "aria-hidden": "true" });
    svg.append(svgElement("path", { d: "M10 9h28v30H10zM16 16h16M16 23h16M16 30h10" }));
    return svg;
  }

  function documentSmallIcon() {
    const svg = svgElement("svg", { viewBox: "0 0 16 16", "aria-hidden": "true" });
    svg.append(svgElement("path", { d: "M3 2.5h7l3 3v8H3zM10 2.5v3h3" }));
    return svg;
  }

  function externalLinkIcon() {
    const svg = svgElement("svg", { viewBox: "0 0 16 16", "aria-hidden": "true" });
    svg.append(svgElement("path", { d: "M6.5 3H3v10h10V9.5M8.5 2.5h5v5m-.3-4.7L7 9" }));
    return svg;
  }

  function addFact(list, label, value) {
    const wrapper = createElement("div");
    wrapper.append(createElement("dt", "", label), createElement("dd", "", value));
    list.append(wrapper);
  }

  function countUniqueSources(events) {
    const keys = new Set();
    for (const event of events) {
      for (const source of event.sources) keys.add(source.url || source.title);
    }
    return keys.size;
  }

  function entityDescriptor(entity) {
    return [entity.kind && humanize(entity.kind), entity.region, entityEraThrough(entity, state.selectedYear)]
      .filter(Boolean)
      .join(" · ");
  }

  function entityEra(entity) {
    if (entity.start_year === null && entity.end_year === null) return "Dates not set";
    const start = entity.start_year === null ? "?" : formatYear(entity.start_year);
    const end = entity.end_year === null ? "present" : formatYear(entity.end_year);
    return `${start}–${end}`;
  }

  function entityEraThrough(entity, year) {
    if (entity.start_year === null) return `Rated by ${formatYear(year)}`;
    const knownEnd = entity.end_year !== null && entity.end_year <= year ? formatYear(entity.end_year) : formatYear(year);
    return `${formatYear(entity.start_year)}–${knownEnd}`;
  }

  function formatEventDate(event) {
    if (event.end_year === null || event.end_year === event.year) return formatYear(event.year);
    return `${formatYear(event.year)}–${formatYear(event.end_year)}`;
  }

  function relativeYearLabel(eventYear, selectedYear) {
    const difference = eventYear - selectedYear;
    if (difference === 0) return "selected year";
    const amount = Math.abs(difference);
    return `${formatInteger(amount)} yr${amount === 1 ? "" : "s"} ${difference < 0 ? "before" : "after"}`;
  }

  function formatYear(value) {
    const year = Math.round(Number(value));
    if (!Number.isFinite(year)) return "Unknown date";
    if (year < 0) return `${formatInteger(Math.abs(year))} BCE`;
    if (year === 0) return "Era boundary";
    return `${formatInteger(year)} CE`;
  }

  function formatAxisYear(value) {
    const year = Math.round(Number(value));
    if (year < 0) return `${formatInteger(Math.abs(year))} BCE`;
    if (year === 0) return "1 CE";
    return year < 1000 ? `${year} CE` : formatInteger(year);
  }

  function formatDate(value) {
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return String(value);
    return new Intl.DateTimeFormat(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
      timeZone: "UTC",
    }).format(date);
  }

  function formatInteger(value) {
    if (value === null || value === undefined || value === "") return "—";
    const number = Number(value);
    return Number.isFinite(number) ? new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(number) : "—";
  }

  function formatRating(value) {
    if (value === null || value === undefined || value === "") return "—";
    return formatInteger(Math.round(Number(value)));
  }

  function formatDecimal(value, digits) {
    if (value === null || value === undefined || value === "") return "—";
    const number = Number(value);
    if (!Number.isFinite(number)) return "—";
    return new Intl.NumberFormat(undefined, { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(number);
  }

  function formatCompactNumber(value) {
    if (value === null || value === undefined || value === "") return "—";
    const number = Number(value);
    if (!Number.isFinite(number)) return "—";
    const digits = Math.abs(number) < 1 ? 2 : Math.abs(number) < 10 ? 1 : 0;
    return new Intl.NumberFormat(undefined, { maximumFractionDigits: digits }).format(number);
  }

  function formatSigned(value, digits = 0) {
    const number = Number(value);
    if (!Number.isFinite(number)) return "—";
    const normalized = Math.abs(number) < 0.000001 ? 0 : number;
    return new Intl.NumberFormat(undefined, {
      signDisplay: normalized === 0 ? "never" : "always",
      minimumFractionDigits: digits,
      maximumFractionDigits: digits,
    }).format(normalized);
  }

  function formatConfidence(value) {
    if (value === null || value === undefined || value === "") return "Not rated";
    const number = Number(value);
    if (!Number.isFinite(number)) return "Not rated";
    const percent = number <= 1 ? number * 100 : number;
    return `${formatInteger(clamp(percent, 0, 100))}%`;
  }

  function formatUncertainty(value) {
    const number = Number(value);
    return Number.isFinite(number) ? `±${formatCompactNumber(number)}` : "";
  }

  function formatUtility(value) {
    if (value === null || value === undefined || value === "") return "—";
    const number = Number(value);
    if (!Number.isFinite(number)) return "—";
    return formatSigned(number, Math.abs(number) <= 1 ? 2 : 1);
  }

  function formatModelField(value) {
    if (value === null || value === undefined || value === "") return "Not classified";
    if (typeof value === "number") return formatCompactNumber(value);
    if (typeof value === "object") {
      const label = value.label ?? value.name ?? value.value;
      return label === undefined ? "Not classified" : humanize(label);
    }
    return humanize(value);
  }

  function humanize(value) {
    if (value === null || value === undefined) return "";
    const text = String(value).trim().replace(/[_-]+/g, " ").replace(/\s+/g, " ");
    return text ? text.charAt(0).toLocaleUpperCase() + text.slice(1) : "";
  }

  function cleanOptionalText(value) {
    if (value === null || value === undefined) return null;
    if (typeof value === "object") return null;
    const text = String(value).trim();
    return text || null;
  }

  function cleanTextArray(value) {
    if (!Array.isArray(value)) return [];
    return [...new Set(value.map((item) => cleanOptionalText(item)).filter(Boolean))];
  }

  function safeHttpUrl(value) {
    if (!value) return null;
    try {
      const url = new URL(String(value), window.location.href);
      return url.protocol === "http:" || url.protocol === "https:" ? url.href : null;
    } catch {
      return null;
    }
  }

  function finiteNumber(value) {
    if (value === null || value === undefined || value === "") return null;
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function nonNegativeNumber(value) {
    const number = finiteNumber(value);
    return number === null ? null : Math.max(0, number);
  }

  function average(values) {
    const finite = values.filter((value) => Number.isFinite(value));
    return finite.length ? finite.reduce((sum, value) => sum + value, 0) / finite.length : null;
  }

  function median(values) {
    const finite = values.filter((value) => Number.isFinite(value)).sort((left, right) => left - right);
    if (!finite.length) return null;
    const middle = Math.floor(finite.length / 2);
    return finite.length % 2 ? finite[middle] : (finite[middle - 1] + finite[middle]) / 2;
  }

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function round2(value) {
    return Math.round(value * 100) / 100;
  }

  function showToast(message) {
    clearTimeout(state.toastTimer);
    elements.toast.textContent = message;
    elements.toast.hidden = false;
    state.toastTimer = window.setTimeout(() => {
      elements.toast.hidden = true;
    }, 2400);
  }

  function createFallbackData() {
    return {
      meta: {
        demo: true,
        status: "preview",
        generated_at: "2026-07-13",
        coverage_note: "This compact preview exists only to demonstrate the interface when the research dataset is unavailable.",
        coverage_warnings: [
          "Preview scores are hand-built interface fixtures, not research conclusions.",
          "Sparse and disconnected conflict records should not be read as globally comparable evidence.",
        ],
      },
      entities: [
        { id: "roman_republic", name: "Roman Republic", kind: "republic", start_year: -509, end_year: -27, region: "Mediterranean" },
        { id: "carthage", name: "Carthage", kind: "city-state", start_year: -814, end_year: -146, region: "North Africa" },
        { id: "mongol_empire", name: "Mongol Empire", kind: "empire", start_year: 1206, end_year: 1368, region: "Eurasia" },
        { id: "ottoman_empire", name: "Ottoman Empire", kind: "empire", start_year: 1299, end_year: 1922, region: "Mediterranean" },
        { id: "british_empire", name: "British Empire", kind: "empire", start_year: 1707, end_year: 1997, region: "Global" },
        { id: "united_states", name: "United States", kind: "country", start_year: 1776, end_year: null, region: "North America" },
        { id: "nazi_germany", name: "Nazi Germany", kind: "regime", start_year: 1933, end_year: 1945, region: "Europe" },
        { id: "north_vietnam", name: "North Vietnam", kind: "country", start_year: 1945, end_year: 1976, region: "Southeast Asia" },
      ],
      series: {
        roman_republic: [
          { year: -264, event_id: null, tactical: 1500, operational: 1500, strategic: 1500, composite: 1500, uncertainty: 95, delta: 0 },
          { year: -201, event_id: "second_punic_war", tactical: 1580, operational: 1610, strategic: 1640, composite: 1610, uncertainty: 72, delta: 110 },
          { year: -146, event_id: "third_punic_war", tactical: 1630, operational: 1660, strategic: 1710, composite: 1667, uncertainty: 60, delta: 57 },
        ],
        carthage: [
          { year: -264, event_id: null, tactical: 1500, operational: 1500, strategic: 1500, composite: 1500, uncertainty: 95, delta: 0 },
          { year: -201, event_id: "second_punic_war", tactical: 1510, operational: 1430, strategic: 1360, composite: 1433, uncertainty: 80, delta: -67 },
          { year: -146, event_id: "third_punic_war", tactical: 1360, operational: 1280, strategic: 1180, composite: 1273, uncertainty: 74, delta: -160 },
        ],
        mongol_empire: [
          { year: 1206, event_id: null, tactical: 1500, operational: 1500, strategic: 1500, composite: 1500, uncertainty: 100, delta: 0 },
          { year: 1221, event_id: "khwarazmian_conquest", tactical: 1700, operational: 1740, strategic: 1690, composite: 1710, uncertainty: 70, delta: 210 },
          { year: 1241, event_id: "mongol_europe", tactical: 1750, operational: 1785, strategic: 1710, composite: 1748, uncertainty: 68, delta: 38 },
        ],
        ottoman_empire: [
          { year: 1299, event_id: null, tactical: 1500, operational: 1500, strategic: 1500, composite: 1500, uncertainty: 100, delta: 0 },
          { year: 1453, event_id: "fall_constantinople", tactical: 1630, operational: 1700, strategic: 1710, composite: 1680, uncertainty: 66, delta: 180 },
          { year: 1683, event_id: "vienna_1683", tactical: 1530, operational: 1500, strategic: 1470, composite: 1500, uncertainty: 72, delta: -180 },
          { year: 1918, event_id: "world_war_one", tactical: 1420, operational: 1360, strategic: 1280, composite: 1353, uncertainty: 58, delta: -147 },
        ],
        british_empire: [
          { year: 1707, event_id: null, tactical: 1500, operational: 1500, strategic: 1500, composite: 1500, uncertainty: 82, delta: 0 },
          { year: 1763, event_id: "seven_years_war", tactical: 1590, operational: 1630, strategic: 1680, composite: 1633, uncertainty: 50, delta: 133 },
          { year: 1815, event_id: "napoleonic_wars", tactical: 1640, operational: 1660, strategic: 1710, composite: 1670, uncertainty: 46, delta: 37 },
          { year: 1945, event_id: "world_war_two", tactical: 1610, operational: 1580, strategic: 1600, composite: 1597, uncertainty: 38, delta: -73 },
        ],
        united_states: [
          { year: 1776, event_id: null, tactical: 1500, operational: 1500, strategic: 1500, composite: 1500, uncertainty: 78, delta: 0 },
          { year: 1945, event_id: "world_war_two", tactical: 1670, operational: 1710, strategic: 1750, composite: 1710, uncertainty: 34, delta: 210 },
          { year: 1975, event_id: "vietnam_war", tactical: 1680, operational: 1660, strategic: 1640, composite: 1660, uncertainty: 40, delta: -50 },
          { year: 1991, event_id: "gulf_war", tactical: 1730, operational: 1750, strategic: 1710, composite: 1730, uncertainty: 36, delta: 70 },
        ],
        nazi_germany: [
          { year: 1939, event_id: null, tactical: 1500, operational: 1500, strategic: 1500, composite: 1500, uncertainty: 55, delta: 0 },
          { year: 1945, event_id: "world_war_two", tactical: 1450, operational: 1320, strategic: 1120, composite: 1297, uncertainty: 32, delta: -203 },
        ],
        north_vietnam: [
          { year: 1955, event_id: null, tactical: 1500, operational: 1500, strategic: 1500, composite: 1500, uncertainty: 70, delta: 0 },
          { year: 1975, event_id: "vietnam_war", tactical: 1580, operational: 1660, strategic: 1730, composite: 1657, uncertainty: 44, delta: 157 },
        ],
      },
      leaderboard: [
        { entity_id: "mongol_empire", name: "Mongol Empire", composite: 1748, tactical: 1750, operational: 1785, strategic: 1710, peak: 1748, peak_year: 1241, sustained: 1648, achievement: 420, historical_success: 88.4, events: 2, wars: 2, wins: 2, losses: 0, draws: 0, confidence: 0.72, uncertainty: 68, network_component: 2, established: true },
        { entity_id: "roman_republic", name: "Roman Republic", composite: 1667, tactical: 1630, operational: 1660, strategic: 1710, peak: 1667, peak_year: -146, sustained: 1592, achievement: 370, historical_success: 84.8, events: 2, wars: 2, wins: 2, losses: 0, draws: 0, confidence: 0.78, uncertainty: 60, network_component: 1, established: true },
        { entity_id: "united_states", name: "United States", composite: 1730, tactical: 1730, operational: 1750, strategic: 1710, peak: 1730, peak_year: 1991, sustained: 1650, achievement: 340, historical_success: 82.2, events: 3, wars: 3, wins: 2, losses: 1, draws: 0, confidence: 0.8, uncertainty: 36, network_component: 3, established: true },
        { entity_id: "british_empire", name: "British Empire", composite: 1597, tactical: 1610, operational: 1580, strategic: 1600, peak: 1670, peak_year: 1815, sustained: 1600, achievement: 390, historical_success: 80.5, events: 3, wars: 3, wins: 3, losses: 0, draws: 0, confidence: 0.77, uncertainty: 38, network_component: 3, established: true },
        { entity_id: "ottoman_empire", name: "Ottoman Empire", composite: 1353, tactical: 1420, operational: 1360, strategic: 1280, peak: 1680, peak_year: 1453, sustained: 1508, achievement: 315, historical_success: 73.6, events: 3, wars: 3, wins: 1, losses: 2, draws: 0, confidence: 0.7, uncertainty: 58, network_component: 2, established: true },
        { entity_id: "north_vietnam", name: "North Vietnam", composite: 1657, tactical: 1580, operational: 1660, strategic: 1730, peak: 1657, peak_year: 1975, sustained: 1579, achievement: 157, historical_success: 66.4, events: 1, wars: 1, wins: 1, losses: 0, draws: 0, confidence: 0.62, uncertainty: 44, network_component: 3, established: false },
        { entity_id: "carthage", name: "Carthage", composite: 1273, tactical: 1360, operational: 1280, strategic: 1180, peak: 1500, peak_year: -264, sustained: 1402, achievement: 140, historical_success: 46.8, events: 2, wars: 2, wins: 0, losses: 2, draws: 0, confidence: 0.7, uncertainty: 74, network_component: 1, established: true },
        { entity_id: "nazi_germany", name: "Nazi Germany", composite: 1297, tactical: 1450, operational: 1320, strategic: 1120, peak: 1500, peak_year: 1939, sustained: 1398, achievement: 120, historical_success: 35.2, events: 1, wars: 1, wins: 0, losses: 1, draws: 0, confidence: 0.86, uncertainty: 32, network_component: 3, established: false },
      ],
      events: [
        {
          id: "second_punic_war",
          name: "Second Punic War",
          year: -218,
          end_year: -201,
          type: "war",
          war_type: "interstate total war",
          scale: "major",
          stakes: "existential",
          confidence: 0.75,
          summary: "A long interstate war ending in Roman strategic victory and the loss of Carthaginian great-power status.",
          participants: [
            { entity_id: "roman_republic", side: "Roman coalition", result_class: "major strategic victory", utility: 0.9, delta: 110 },
            { entity_id: "carthage", side: "Carthaginian coalition", result_class: "major strategic defeat", utility: -0.9, delta: -67 },
          ],
          sources: [{ title: "Encyclopaedia Britannica — Second Punic War", url: "https://www.britannica.com/event/Second-Punic-War" }],
        },
        {
          id: "third_punic_war",
          name: "Third Punic War",
          year: -149,
          end_year: -146,
          type: "war",
          war_type: "interstate conquest",
          scale: "major",
          stakes: "existential",
          confidence: 0.76,
          summary: "Rome destroyed Carthage as an independent polity after a three-year siege.",
          participants: [
            { entity_id: "roman_republic", side: "Rome", result_class: "regime-destroying victory", utility: 1, delta: 57 },
            { entity_id: "carthage", side: "Carthage", result_class: "polity-ending defeat", utility: -1, delta: -160 },
          ],
          sources: [{ title: "Encyclopaedia Britannica — Third Punic War", url: "https://www.britannica.com/event/Third-Punic-War" }],
        },
        {
          id: "khwarazmian_conquest",
          name: "Mongol conquest of Khwarazm",
          year: 1219,
          end_year: 1221,
          type: "campaign",
          war_type: "imperial conquest",
          scale: "major",
          stakes: "regime survival",
          confidence: 0.7,
          summary: "A fast multi-theater conquest that destroyed the Khwarazmian state and expanded Mongol control into Central Asia.",
          participants: [{ entity_id: "mongol_empire", side: "Mongol forces", result_class: "decisive conquest", utility: 1, delta: 210 }],
          sources: [{ title: "Encyclopaedia Britannica — Genghis Khan", url: "https://www.britannica.com/biography/Genghis-Khan" }],
        },
        {
          id: "mongol_europe",
          name: "Mongol invasion of Europe",
          year: 1236,
          end_year: 1241,
          type: "campaign series",
          war_type: "imperial expansion",
          scale: "major",
          stakes: "territorial",
          confidence: 0.66,
          summary: "Mongol armies defeated multiple European forces before withdrawing after Ögedei Khan's death.",
          participants: [{ entity_id: "mongol_empire", side: "Mongol forces", result_class: "major operational victory", utility: 0.65, delta: 38 }],
          sources: [{ title: "Encyclopaedia Britannica — Battle of Legnica", url: "https://www.britannica.com/event/Battle-of-Legnica" }],
        },
        {
          id: "fall_constantinople",
          name: "Fall of Constantinople",
          year: 1453,
          end_year: 1453,
          type: "siege",
          war_type: "imperial conquest",
          scale: "major",
          stakes: "capital and regime survival",
          confidence: 0.86,
          summary: "The Ottoman capture of Constantinople ended the Byzantine Empire and secured a strategic imperial capital.",
          participants: [{ entity_id: "ottoman_empire", side: "Ottoman forces", result_class: "regime-destroying victory", utility: 1, delta: 180 }],
          sources: [{ title: "Encyclopaedia Britannica — Fall of Constantinople", url: "https://www.britannica.com/event/Fall-of-Constantinople-1453" }],
        },
        {
          id: "vienna_1683",
          name: "Battle of Vienna",
          year: 1683,
          end_year: 1683,
          type: "battle",
          war_type: "interstate coalition war",
          scale: "major",
          stakes: "strategic theater",
          confidence: 0.8,
          summary: "A relief coalition broke the Ottoman siege, marking a major strategic reversal in Central Europe.",
          participants: [{ entity_id: "ottoman_empire", side: "Ottoman forces", result_class: "major strategic defeat", utility: -0.8, delta: -180 }],
          sources: [{ title: "Encyclopaedia Britannica — Siege of Vienna", url: "https://www.britannica.com/event/Siege-of-Vienna-1683" }],
        },
        {
          id: "seven_years_war",
          name: "Seven Years’ War",
          year: 1756,
          end_year: 1763,
          type: "war",
          war_type: "global interstate war",
          scale: "global",
          stakes: "imperial position",
          confidence: 0.8,
          summary: "Britain gained substantial imperial territory and maritime advantage despite a complex coalition war.",
          participants: [{ entity_id: "british_empire", side: "Anglo-Prussian coalition", result_class: "major strategic victory", utility: 0.82, delta: 133 }],
          sources: [{ title: "Encyclopaedia Britannica — Seven Years’ War", url: "https://www.britannica.com/event/Seven-Years-War" }],
        },
        {
          id: "napoleonic_wars",
          name: "Napoleonic Wars",
          year: 1803,
          end_year: 1815,
          type: "war series",
          war_type: "coalition great-power war",
          scale: "continental",
          stakes: "balance of power",
          confidence: 0.84,
          summary: "Britain remained at war through successive coalitions and emerged with enhanced global and maritime power.",
          participants: [{ entity_id: "british_empire", side: "Anti-French coalitions", result_class: "major coalition victory", utility: 0.85, delta: 37 }],
          sources: [{ title: "Encyclopaedia Britannica — Napoleonic Wars", url: "https://www.britannica.com/event/Napoleonic-Wars" }],
        },
        {
          id: "world_war_one",
          name: "First World War",
          year: 1914,
          end_year: 1918,
          type: "war",
          war_type: "global industrial war",
          scale: "global",
          stakes: "regime survival",
          confidence: 0.9,
          summary: "The Ottoman state was defeated, occupied in part, and dissolved in the war's aftermath.",
          participants: [{ entity_id: "ottoman_empire", side: "Central Powers", result_class: "regime-ending defeat", utility: -1, delta: -147 }],
          sources: [{ title: "Encyclopaedia Britannica — World War I", url: "https://www.britannica.com/event/World-War-I" }],
        },
        {
          id: "world_war_two",
          name: "Second World War",
          year: 1939,
          end_year: 1945,
          type: "war",
          war_type: "global industrial total war",
          scale: "global",
          stakes: "existential",
          confidence: 0.94,
          summary: "A global coalition victory that destroyed the Nazi regime while leaving the United States in a greatly strengthened strategic position.",
          participants: [
            { entity_id: "united_states", side: "Allies", result_class: "decisive coalition victory", utility: 1, delta: 210 },
            { entity_id: "british_empire", side: "Allies", result_class: "major victory with high cost", utility: 0.72, delta: -73 },
            { entity_id: "nazi_germany", side: "Axis", result_class: "unconditional regime-ending defeat", utility: -1, delta: -203 },
          ],
          sources: [{ title: "Encyclopaedia Britannica — World War II", url: "https://www.britannica.com/event/World-War-II" }],
        },
        {
          id: "vietnam_war",
          name: "Vietnam War",
          year: 1955,
          end_year: 1975,
          type: "war",
          war_type: "internationalized civil and insurgency war",
          scale: "major regional",
          stakes: "limited for US; existential for Vietnamese belligerents",
          confidence: 0.87,
          summary: "The United States withdrew without achieving its political objective; North Vietnam achieved reunification. This is coded as a limited strategic defeat for the US, not a regime-ending loss.",
          participants: [
            { entity_id: "united_states", side: "South Vietnam and allies", result_class: "limited strategic defeat and withdrawal", utility: -0.35, delta: -50 },
            { entity_id: "north_vietnam", side: "North Vietnam and allies", result_class: "war aims achieved", utility: 0.9, delta: 157 },
          ],
          sources: [{ title: "Encyclopaedia Britannica — Vietnam War", url: "https://www.britannica.com/event/Vietnam-War" }],
        },
        {
          id: "gulf_war",
          name: "Gulf War",
          year: 1990,
          end_year: 1991,
          type: "war",
          war_type: "coalition interstate war",
          scale: "major regional",
          stakes: "limited territorial objective",
          confidence: 0.92,
          summary: "A US-led coalition expelled Iraqi forces from Kuwait while stopping short of regime change in Baghdad.",
          participants: [{ entity_id: "united_states", side: "Coalition", result_class: "decisive limited-aim victory", utility: 0.8, delta: 70 }],
          sources: [{ title: "Encyclopaedia Britannica — Persian Gulf War", url: "https://www.britannica.com/event/Persian-Gulf-War" }],
        },
      ],
    };
  }
})();
