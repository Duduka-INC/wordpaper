import { LoaderCircle } from "lucide-react";

export function StatusBlock({ label = "Собираем композицию" }: { label?: string }) {
  return (
    <div className="status-block" role="status">
      <LoaderCircle className="spin" size={22} />
      <span>{label}</span>
    </div>
  );
}
