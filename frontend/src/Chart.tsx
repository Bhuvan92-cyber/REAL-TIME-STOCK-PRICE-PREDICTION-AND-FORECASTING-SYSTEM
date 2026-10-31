import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer, BarChart, Bar, Legend } from "recharts";
import type { MarketResponse } from "./api";

export function PriceChart({ candles, indicators = true }: { candles: MarketResponse["candles"]; indicators?: boolean }) {
  const data = candles.map((c) => ({ ...c, date: new Date(c.timestamp).toLocaleDateString(undefined, { month: "short", day: "numeric" }) }));
  return <ResponsiveContainer width="100%" height={360}><LineChart data={data}><CartesianGrid stroke="#223c5b" /><XAxis dataKey="date" minTickGap={30} /><YAxis domain={["auto", "auto"]} /><Tooltip /><Legend /><Line type="monotone" dataKey="close" stroke="#38bdf8" dot={false} name="Close" />{indicators && <><Line type="monotone" dataKey="sma_20" stroke="#fbbf24" dot={false} name="SMA 20" /><Line type="monotone" dataKey="ema_20" stroke="#a78bfa" dot={false} name="EMA 20" /><Line type="monotone" dataKey="bb_upper" stroke="#64748b" dot={false} name="Bollinger upper" /><Line type="monotone" dataKey="bb_lower" stroke="#64748b" dot={false} name="Bollinger lower" /></>}</LineChart></ResponsiveContainer>;
}

export function VolumeChart({ candles }: { candles: MarketResponse["candles"] }) {
  return <ResponsiveContainer width="100%" height={160}><BarChart data={candles.slice(-90)}><XAxis dataKey="timestamp" hide /><YAxis hide /><Tooltip /><Bar dataKey="volume" fill="#64748b" /></BarChart></ResponsiveContainer>;
}
