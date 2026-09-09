export function humanizeSnakeCase(value: string): string {
  if (!value) return "";

  return value
    .split("_")
    .filter(Boolean)
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}