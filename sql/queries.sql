-- name: interests
SELECT id, name FROM interests ORDER BY name;
-- name: events
SELECT * FROM events ORDER BY date, id;
-- name: available_events
SELECT * FROM events WHERE active = 1 AND date >= ? ORDER BY date, id;
-- name: search_events
SELECT * FROM events
WHERE instr(CASEFOLD(name), CASEFOLD(?)) > 0 ORDER BY date, id;
-- name: event_tags
SELECT ei.event_id, i.id, i.name FROM event_interests ei
JOIN interests i ON i.id = ei.interest_id ORDER BY i.name;
-- name: recommendations
SELECT r.*, v.name AS visitor_name, e.name AS event_name
FROM recommendations r JOIN visitors v ON v.id = r.visitor_id
JOIN events e ON e.id = r.event_id ORDER BY r.id;
-- name: event_count
SELECT count(*) AS total FROM events;
-- name: price_range
SELECT min(price) AS minimum, max(price) AS maximum FROM events WHERE active = 1;
-- name: events_per_interest
SELECT i.id, i.name, count(ei.event_id) AS total FROM interests i
LEFT JOIN event_interests ei ON ei.interest_id = i.id
GROUP BY i.id, i.name ORDER BY total DESC, i.name;
-- name: visitors_per_interest
SELECT i.name, count(vi.visitor_id) AS total FROM interests i
LEFT JOIN visitor_interests vi ON vi.interest_id = i.id
GROUP BY i.id, i.name ORDER BY total DESC, i.name;
-- name: matching_events
SELECT e.*, count(vi.interest_id) AS score FROM events e
JOIN event_interests ei ON ei.event_id = e.id
JOIN visitor_interests vi ON vi.interest_id = ei.interest_id
JOIN visitors v ON v.id = vi.visitor_id
LEFT JOIN recommendations r ON r.visitor_id = v.id AND r.event_id = e.id
WHERE v.id = ? AND e.active = 1 AND e.date >= ?
AND e.min_age <= v.age AND e.price <= v.budget
AND coalesce(r.status, 'new') <> 'dismissed'
GROUP BY e.id HAVING count(vi.interest_id) > 0
ORDER BY score DESC, e.price, e.date, e.id;
