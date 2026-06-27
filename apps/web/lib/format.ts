/** Small presentation helpers. */

/** Match minute as a clock label, e.g. 90.5 -> "90+1'". */
export function minuteLabel(minute: number): string {
  if (minute > 90) {
    const extra = Math.max(1, Math.round(minute - 90));
    return `90+${extra}'`;
  }
  if (minute > 45 && minute < 46) {
    return "45+1'";
  }
  return `${Math.floor(minute)}'`;
}
