(function (root, factory) {
  "use strict";

  const api = factory();
  if (typeof module === "object" && module.exports) module.exports = api;
  if (root) root.MilitaryEloLocation = api;
})(typeof globalThis === "undefined" ? this : globalThis, function () {
  "use strict";

  const LOCATION_WARNING =
    "HCED location fields are unreviewed source assertions. Quarantined values are withheld, not corrected. Coordinate precision is unknown.";
  const PROVENANCE_KEYS = [
    "assertion_status",
    "coordinate_precision",
    "source_id",
    "source_record_id",
  ];

  function exactNonblankText(value) {
    if (typeof value !== "string" || !value.trim() || value !== value.trim()) return null;
    return value;
  }

  function normalizeGeoJsonPoint(value) {
    if (!value || typeof value !== "object" || Array.isArray(value) || value.type !== "Point") return null;
    const keys = Object.keys(value).sort();
    if (keys.length !== 2 || keys[0] !== "coordinates" || keys[1] !== "type") return null;
    if (!Array.isArray(value.coordinates) || value.coordinates.length !== 2) return null;
    const [longitude, latitude] = value.coordinates;
    if (typeof longitude !== "number" || typeof latitude !== "number") return null;
    if (!Number.isFinite(longitude) || !Number.isFinite(latitude)) return null;
    if (longitude < -180 || longitude > 180 || latitude < -90 || latitude > 90) return null;
    return { type: "Point", coordinates: [longitude, latitude] };
  }

  function normalizeProvenance(value) {
    if (!value || typeof value !== "object" || Array.isArray(value)) return null;
    const keys = Object.keys(value).sort();
    if (keys.length !== PROVENANCE_KEYS.length || keys.some((key, index) => key !== PROVENANCE_KEYS[index])) return null;
    const sourceRecordId = exactNonblankText(value.source_record_id);
    if (
      value.source_id !== "hced_dataset" ||
      value.assertion_status !== "unreviewed_source_assertion" ||
      value.coordinate_precision !== "unknown" ||
      sourceRecordId === null
    ) {
      return null;
    }
    return {
      source_id: "hced_dataset",
      source_record_id: sourceRecordId,
      assertion_status: "unreviewed_source_assertion",
      coordinate_precision: "unknown",
    };
  }

  function normalizeEventLocation(event) {
    const candidateId = exactNonblankText(event && event.hced_candidate_id);
    const result = candidateId === null ? {} : { hced_candidate_id: candidateId };
    const provenance = normalizeProvenance(event && event.location_provenance);
    const sourceIds = event && event.source_ids;
    if (
      candidateId === null ||
      provenance === null ||
      !Array.isArray(sourceIds) ||
      !sourceIds.includes("hced_dataset")
    ) return result;

    const country = exactNonblankText(event.modern_location_country);
    let geometry = normalizeGeoJsonPoint(event.geometry);
    if (
      geometry !== null &&
      geometry.coordinates[0] === 0 &&
      geometry.coordinates[1] === 0
    ) geometry = null;
    if (country === null && geometry === null) return result;
    if (country !== null) result.modern_location_country = country;
    if (geometry !== null) result.geometry = geometry;
    result.location_provenance = provenance;
    return result;
  }

  function formatPoint(geometry) {
    const point = normalizeGeoJsonPoint(geometry);
    return point === null ? null : `[${point.coordinates[0]}, ${point.coordinates[1]}]`;
  }

  return {
    LOCATION_WARNING,
    formatPoint,
    normalizeEventLocation,
    normalizeGeoJsonPoint,
    normalizeProvenance,
  };
});
