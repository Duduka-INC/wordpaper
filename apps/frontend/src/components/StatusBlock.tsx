import { LoaderCircle } from "lucide-react";
import { useLocaleStore } from "../locale";

export function StatusBlock({ label }: { label?: string }) {
  const locale = useLocaleStore((state) => state.locale);
  return (
    <div className="status-block" role="status">
      <LoaderCircle className="spin" size={22} />
      <span>{label ?? (locale === "ru" ? "Собираем композицию" : "Composing wallpaper")}</span>
    </div>
  );
}
