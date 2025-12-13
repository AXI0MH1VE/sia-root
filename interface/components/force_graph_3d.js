export function toForceGraphFormat(graphJson) {
  const nodes = (graphJson?.nodes || []).map(n => ({
    id: n.id,
    name: n.label,
    score: n.score,
    content: n.content
  }));
  const links = (graphJson?.nodes || [])
    .filter(n => n.parent)
    .map(n => ({ source: n.parent, target: n.id }));
  return { nodes, links };
}
