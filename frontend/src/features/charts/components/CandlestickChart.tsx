import { useEffect, useRef } from "react";
import { CandlestickData, CandlestickSeries, ColorType, IChartApi, ISeriesApi, Time, createChart } from "lightweight-charts";

export interface CandlePoint {
  time: Time;
  open: number;
  high: number;
  low: number;
  close: number;
}

interface CandlestickChartProps {
  data: CandlePoint[];
  liveBar?: CandlePoint | null;
}

export function CandlestickChart({ data, liveBar }: CandlestickChartProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const seriesRef = useRef<ISeriesApi<"Candlestick"> | null>(null);

  useEffect(() => {
    if (!containerRef.current) {
      return;
    }
    const chart = createChart(containerRef.current, {
      layout: { background: { type: ColorType.Solid, color: "transparent" }, textColor: "#d1d4dc" },
      grid: { vertLines: { color: "#2a2e39" }, horzLines: { color: "#2a2e39" } },
      height: 480,
      autoSize: true
    });
    chartRef.current = chart;

    const series = chart.addSeries(CandlestickSeries, {
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350"
    });
    seriesRef.current = series;

    return () => {
      chart.remove();
      chartRef.current = null;
      seriesRef.current = null;
    };
  }, []);

  useEffect(() => {
    if (!seriesRef.current) {
      return;
    }
    seriesRef.current.setData(data as CandlestickData[]);
    chartRef.current?.timeScale().fitContent();
  }, [data]);

  useEffect(() => {
    if (!seriesRef.current || !liveBar) {
      return;
    }
    seriesRef.current.update(liveBar as CandlestickData);
  }, [liveBar]);

  return <div ref={containerRef} style={{ width: "100%" }} />;
}