(function (root, factory) {
  const contract = factory();
  if (typeof module === "object" && module.exports) module.exports = contract;
  if (root) root.MilitaryEloHorizon = contract;
})(typeof globalThis !== "undefined" ? globalThis : this, function () {
  "use strict";

  function finiteNumber(value) {
    if (value === null || value === undefined || value === "") return null;
    const number = Number(value);
    return Number.isFinite(number) ? number : null;
  }

  function eventAvailabilityYear(event) {
    if (!event || typeof event !== "object") return null;
    return finiteNumber(event.end_year) ?? finiteNumber(event.year);
  }

  function eventIsAvailable(event, year) {
    const availableYear = eventAvailabilityYear(event);
    const horizon = finiteNumber(year);
    return availableYear !== null && horizon !== null && availableYear <= horizon;
  }

  function eventsAtOrBefore(events, year) {
    if (!Array.isArray(events)) return [];
    return events.filter((event) => eventIsAvailable(event, year));
  }

  function seriesThrough(points, year) {
    if (!Array.isArray(points)) return [];
    const horizon = finiteNumber(year);
    if (horizon === null) return [];
    return points.filter((point) => finiteNumber(point && point.year) !== null && Number(point.year) <= horizon);
  }

  function pointAtOrBefore(points, year) {
    if (!Array.isArray(points) || !points.length) return null;
    const horizon = finiteNumber(year);
    if (horizon === null) return null;
    let low = 0;
    let high = points.length;
    while (low < high) {
      const middle = (low + high) >>> 1;
      const pointYear = finiteNumber(points[middle] && points[middle].year);
      if (pointYear !== null && pointYear <= horizon) low = middle + 1;
      else high = middle;
    }
    return points[low - 1] ?? null;
  }

  function ratedSeriesThrough(points, year) {
    return seriesThrough(points, year).filter((point) => {
      const eventId = point && point.event_id;
      return eventId !== null && eventId !== undefined && String(eventId).toLocaleLowerCase() !== "origin";
    });
  }

  function eventLookup(events) {
    if (events instanceof Map) return events;
    const lookup = new Map();
    if (!Array.isArray(events)) return lookup;
    for (const event of events) {
      if (event && event.id !== null && event.id !== undefined) lookup.set(String(event.id), event);
    }
    return lookup;
  }

  function authorizedSeriesThrough(points, events, entityId, year) {
    if (!Array.isArray(points)) return [];
    const horizon = finiteNumber(year);
    if (horizon === null) return [];
    const lookup = eventLookup(events);
    const expectedEntityId = String(entityId);
    return points.filter((point, index) => {
      const pointYear = finiteNumber(point && point.year);
      if (pointYear === null || pointYear > horizon) return false;
      const eventId = point && point.event_id;
      const origin = eventId === null || eventId === undefined || String(eventId).toLocaleLowerCase() === "origin";
      if (origin) return index === 0;
      const event = lookup.get(String(eventId));
      if (!event || !eventIsAvailable(event, horizon)) return false;
      const participants = Array.isArray(event.participants) ? event.participants : [];
      return participants.some(
        (participant) =>
          participant &&
          participant.entity_id !== null &&
          participant.entity_id !== undefined &&
          String(participant.entity_id) === expectedEntityId,
      );
    });
  }

  function isEntityActive(entity, year, points) {
    const horizon = finiteNumber(year);
    if (!entity || horizon === null) return false;
    const firstPointYear = finiteNumber(Array.isArray(points) && points.length ? points[0].year : null);
    const firstYear = finiteNumber(entity.start_year) ?? firstPointYear ?? -Infinity;
    const lastYear = finiteNumber(entity.end_year) ?? Infinity;
    return horizon >= firstYear && horizon <= lastYear;
  }

  function eventCountsByEntity(events, year) {
    const counts = new Map();
    for (const event of eventsAtOrBefore(events, year)) {
      const participants = Array.isArray(event.participants) ? event.participants : [];
      const seen = new Set();
      for (const participant of participants) {
        const id = participant && participant.entity_id;
        if (id === null || id === undefined || seen.has(String(id))) continue;
        seen.add(String(id));
        counts.set(String(id), (counts.get(String(id)) ?? 0) + 1);
      }
    }
    return counts;
  }

  function rankAtYear({ entities, series, events, year, metric = "composite", activeOnly = true } = {}) {
    const horizon = finiteNumber(year);
    if (horizon === null) return [];
    const entityList = Array.isArray(entities) ? entities : [];
    const seriesByEntity = series && typeof series === "object" ? series : {};
    const eventList = Array.isArray(events) ? events : [];
    const eventCounts = eventCountsByEntity(eventList, horizon);
    const eventsById = eventLookup(eventList);
    const rows = [];

    for (const entity of entityList) {
      if (!entity || entity.id === null || entity.id === undefined) continue;
      const id = String(entity.id);
      const eventCount = eventCounts.get(id) ?? 0;
      if (eventCount < 1) continue;
      const points = Array.isArray(seriesByEntity[id]) ? seriesByEntity[id] : [];
      if (activeOnly && !isEntityActive(entity, horizon, points)) continue;

      const availablePoints = authorizedSeriesThrough(points, eventsById, id, horizon);
      const point = availablePoints[availablePoints.length - 1] ?? null;
      const value = finiteNumber(point && point[metric]);
      if (!point || value === null) continue;

      const previous = availablePoints.length > 1 ? availablePoints[availablePoints.length - 2] : null;
      const previousValue = finiteNumber(previous && previous[metric]);
      const pointDelta = finiteNumber(point.delta);
      rows.push({
        entity,
        point,
        value,
        lastMove: previousValue === null ? pointDelta : value - previousValue,
        events: eventCount,
      });
    }

    return rows.sort((left, right) => right.value - left.value || String(left.entity.name).localeCompare(String(right.entity.name)));
  }

  return Object.freeze({
    eventAvailabilityYear,
    eventIsAvailable,
    eventsAtOrBefore,
    seriesThrough,
    pointAtOrBefore,
    ratedSeriesThrough,
    authorizedSeriesThrough,
    eventCountsByEntity,
    rankAtYear,
  });
});
