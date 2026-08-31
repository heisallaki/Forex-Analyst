export function humanizeSnakeCase(value: string): string {
  if (!value) {
    return value;
  }
  const withSpaces = value.replace(/_/g, " ").trim();
  const lower = withSpaces.toLowerCase();
  return lower.charAt(0).toUpperCase() + lower.slice(1);
}