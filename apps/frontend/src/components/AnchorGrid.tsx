const POSITIONS = [
  ["top_left", 1, 1],
  ["top_left_middle", 2, 1],
  ["top_center", 3, 1],
  ["top_right_middle", 4, 1],
  ["top_right", 5, 1],
  ["left_top_middle", 1, 2],
  ["right_top_middle", 5, 2],
  ["left_center", 1, 3],
  ["center", 3, 3],
  ["right_center", 5, 3],
  ["left_bottom_middle", 1, 4],
  ["right_bottom_middle", 5, 4],
  ["bottom_left", 1, 5],
  ["bottom_left_middle", 2, 5],
  ["bottom_center", 3, 5],
  ["bottom_right_middle", 4, 5],
  ["bottom_right", 5, 5]
] as const;

export function AnchorGrid({
  value,
  onChange
}: {
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <div className="anchor-grid" aria-label="Text block position">
      {POSITIONS.map(([id, column, row]) => (
        <button
          key={id}
          type="button"
          className={value === id ? "is-active" : ""}
          style={{ gridColumn: column, gridRow: row }}
          onClick={() => onChange(id)}
          aria-label={id.replaceAll("_", " ")}
          aria-pressed={value === id}
        />
      ))}
    </div>
  );
}
